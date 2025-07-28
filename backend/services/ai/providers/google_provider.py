"""
Google AI (Gemini) API provider integration
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple

from .base_provider import (
    BaseProvider, ProviderResponse, ProviderError, 
    AuthenticationError, RateLimitError, ModelNotFoundError
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.commands import LLMParameters, ModelCapability


class GoogleProvider(BaseProvider):
    """Google AI (Gemini) API provider implementation"""
    
    # Google AI model configurations
    MODEL_CONFIGS = {
        "gemini-pro": {
            "name": "Gemini Pro",
            "description": "Google's most capable multimodal model",
            "max_tokens": 2048,
            "context_window": 32768,
            "cost_per_1k_tokens": {
                "input": 0.000125,
                "output": 0.000375
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION
            ]
        },
        "gemini-pro-vision": {
            "name": "Gemini Pro Vision",
            "description": "Gemini Pro with vision capabilities",
            "max_tokens": 2048,
            "context_window": 16384,
            "cost_per_1k_tokens": {
                "input": 0.000125,
                "output": 0.000375
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION
            ]
        },
        "gemini-1.5-pro": {
            "name": "Gemini 1.5 Pro",
            "description": "Latest Gemini model with improved capabilities",
            "max_tokens": 8192,
            "context_window": 1000000,
            "cost_per_1k_tokens": {
                "input": 0.0025,
                "output": 0.0075
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.TRANSLATION
            ]
        }
    }
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize Google AI provider
        
        Args:
            api_key (str): Google AI API key
            base_url (str, optional): Custom base URL
        """
        super().__init__(api_key, base_url)
        self._setup_google_session()
    
    def get_default_base_url(self) -> str:
        """Get default Google AI API base URL"""
        return "https://generativelanguage.googleapis.com/v1"
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Google"
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Google AI models"""
        return list(self.MODEL_CONFIGS.keys())
    
    def _setup_google_session(self) -> None:
        """Setup session with Google AI-specific headers"""
        # Google AI allows passing the API key using the ``X-Goog-Api-Key``
        # header.  Using a header means the key will automatically be sent with
        # every request performed through ``self.session`` without having to
        # manually append ``?key=...`` to each endpoint.
        self.session.headers.update({
            'X-Goog-Api-Key': self.api_key
        })
    
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Google AI API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API key cannot be empty"
        
        # Google AI API keys are typically 39 characters long and alphanumeric
        if len(api_key) < 20:
            return False, "Google AI API key is too short"
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[A-Za-z0-9\-_]+$', api_key):
            return False, "Google AI API key contains invalid characters"
        
        return True, ""
    
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to Google AI API
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        try:
            # Test with a simple generation request
            test_data = {
                "contents": [{
                    "parts": [{"text": "Hi"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            
            endpoint = "models/gemini-pro:generateContent"
            success, response_data, response_time = self._make_request('POST', endpoint, test_data)
            
            if success:
                # Check if we got a valid response
                if 'candidates' in response_data and isinstance(response_data['candidates'], list):
                    return True, "Connection successful", response_time
                else:
                    return False, "Invalid response format", response_time
            else:
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                return False, f"Connection failed: {error_msg}", response_time
                
        except AuthenticationError:
            return False, "Invalid API key", 0.0
        except Exception as e:
            return False, f"Connection error: {str(e)}", 0.0
    
    def generate_text(self, 
                     prompt: str, 
                     model_id: str, 
                     parameters: LLMParameters) -> ProviderResponse:
        """
        Generate text using Google AI's generateContent API
        
        Args:
            prompt (str): Input prompt
            model_id (str): Google AI model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Google AI
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data for Google AI format
        request_data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": parameters.temperature,
                "topP": parameters.top_p,
                "maxOutputTokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"])
            }
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["generationConfig"]["stopSequences"] = parameters.stop_sequences
        
        try:
            endpoint = f"models/{model_id}:generateContent"
            success, response_data, response_time = self._make_request('POST', endpoint, request_data)
            
            if not success:
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message=error_msg
                )
            
            # Extract response content
            candidates = response_data.get('candidates', [])
            if not candidates:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No candidates returned"
                )
            
            candidate = candidates[0]
            content_parts = candidate.get('content', {}).get('parts', [])
            
            content = ""
            for part in content_parts:
                if 'text' in part:
                    content += part['text']
            
            # Calculate usage and cost
            usage_metadata = response_data.get('usageMetadata', {})
            prompt_tokens = usage_metadata.get('promptTokenCount', 0)
            completion_tokens = usage_metadata.get('candidatesTokenCount', 0)
            tokens_used = prompt_tokens + completion_tokens
            
            if tokens_used == 0:
                tokens_used = self._estimate_tokens(prompt + content)
            
            cost = self._calculate_cost(tokens_used, model_id)
            
            return ProviderResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                model_used=model_id,
                success=True,
                metadata={
                    'finish_reason': candidate.get('finishReason'),
                    'usage': usage_metadata,
                    'safety_ratings': candidate.get('safetyRatings', [])
                }
            )
            
        except Exception as e:
            return ProviderResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                model_used=model_id,
                success=False,
                error_message=str(e)
            )
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model_id: str, 
                       parameters: LLMParameters) -> ProviderResponse:
        """
        Chat completion using Google AI's generateContent API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Google AI model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Google AI
        """
        # Convert messages to Google AI format
        contents = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Google AI uses 'user' and 'model' roles
            if role == 'assistant':
                role = 'model'
            
            contents.append({
                "role": role,
                "parts": [{"text": content}]
            })
        
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data
        request_data = {
            "contents": contents,
            "generationConfig": {
                "temperature": parameters.temperature,
                "topP": parameters.top_p,
                "maxOutputTokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"])
            }
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["generationConfig"]["stopSequences"] = parameters.stop_sequences
        
        try:
            endpoint = f"models/{model_id}:generateContent"
            success, response_data, response_time = self._make_request('POST', endpoint, request_data)
            
            if not success:
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message=error_msg
                )
            
            # Extract response content
            candidates = response_data.get('candidates', [])
            if not candidates:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No candidates returned"
                )
            
            candidate = candidates[0]
            content_parts = candidate.get('content', {}).get('parts', [])
            
            content = ""
            for part in content_parts:
                if 'text' in part:
                    content += part['text']
            
            # Calculate usage and cost
            usage_metadata = response_data.get('usageMetadata', {})
            prompt_tokens = usage_metadata.get('promptTokenCount', 0)
            completion_tokens = usage_metadata.get('candidatesTokenCount', 0)
            tokens_used = prompt_tokens + completion_tokens
            
            if tokens_used == 0:
                tokens_used = self._estimate_tokens(str(messages) + content)
            
            cost = self._calculate_cost(tokens_used, model_id)
            
            return ProviderResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                model_used=model_id,
                success=True,
                metadata={
                    'finish_reason': candidate.get('finishReason'),
                    'usage': usage_metadata,
                    'safety_ratings': candidate.get('safetyRatings', []),
                    'role': 'assistant'
                }
            )
            
        except Exception as e:
            return ProviderResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                model_used=model_id,
                success=False,
                error_message=str(e)
            )
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model_id: str) -> float:
        """
        Calculate cost for Google AI models
        
        Args:
            prompt_tokens (int): Number of prompt tokens
            completion_tokens (int): Number of completion tokens
            model_id (str): Model identifier
            
        Returns:
            float: Cost in USD
        """
        if model_id in self.MODEL_CONFIGS:
            cost_config = self.MODEL_CONFIGS[model_id]["cost_per_1k_tokens"]
            prompt_cost = (prompt_tokens / 1000) * cost_config["input"]
            completion_cost = (completion_tokens / 1000) * cost_config["output"]
            return prompt_cost + completion_cost
        
        # Fallback to base implementation
        return super()._calculate_cost(prompt_tokens + completion_tokens, model_id)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific Google AI model
        
        Args:
            model_id (str): Model identifier
            
        Returns:
            Optional[Dict[str, Any]]: Model information or None if not found
        """
        if model_id not in self.MODEL_CONFIGS:
            return None
        
        config = self.MODEL_CONFIGS[model_id]
        
        return {
            "id": model_id,
            "name": config["name"],
            "provider": self.get_provider_name(),
            "description": config["description"],
            "max_tokens": config["max_tokens"],
            "context_window": config["context_window"],
            "cost_per_token": config["cost_per_1k_tokens"] / 1000,
            "capabilities": config["capabilities"],
            "metadata": {
                "cost_per_1k_tokens": config["cost_per_1k_tokens"],
                "provider_model_id": model_id
            }
        }
    
    def validate_parameters(self, parameters: LLMParameters, model_id: str) -> Tuple[bool, str]:
        """
        Validate parameters for Google AI models
        
        Args:
            parameters (LLMParameters): Parameters to validate
            model_id (str): Model identifier
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # First run base validation
        is_valid, error_msg = super().validate_parameters(parameters, model_id)
        if not is_valid:
            return is_valid, error_msg
        
        # Google AI-specific validation
        if model_id in self.MODEL_CONFIGS:
            max_tokens = self.MODEL_CONFIGS[model_id]["max_tokens"]
            if parameters.max_tokens > max_tokens:
                return False, f"max_tokens cannot exceed {max_tokens} for model {model_id}"
        
        # Google AI doesn't support frequency_penalty and presence_penalty
        if parameters.frequency_penalty != 0.0:
            return False, "Google AI models do not support frequency_penalty"
        
        if parameters.presence_penalty != 0.0:
            return False, "Google AI models do not support presence_penalty"
        
        return True, ""
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available Google AI models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.MODEL_CONFIGS.keys():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
