"""
OpenAI API provider integration
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

from models.llm_models import LLMParameters, ModelCapability


class OpenAIProvider(BaseProvider):
    """OpenAI API provider implementation"""
    
    # OpenAI model configurations
    MODEL_CONFIGS = {
        "gpt-4": {
            "name": "GPT-4",
            "description": "Most capable GPT-4 model, great for complex tasks",
            "max_tokens": 8192,
            "context_window": 8192,
            "cost_per_1k_tokens": 0.03,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION
            ]
        },
        "gpt-4-turbo": {
            "name": "GPT-4 Turbo",
            "description": "Faster and more efficient GPT-4 model",
            "max_tokens": 4096,
            "context_window": 128000,
            "cost_per_1k_tokens": 0.01,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION
            ]
        },
        "gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "description": "Fast and efficient model for most tasks",
            "max_tokens": 4096,
            "context_window": 16385,
            "cost_per_1k_tokens": 0.002,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        },
        "gpt-3.5-turbo-16k": {
            "name": "GPT-3.5 Turbo 16K",
            "description": "GPT-3.5 with extended context window",
            "max_tokens": 4096,
            "context_window": 16385,
            "cost_per_1k_tokens": 0.004,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        }
    }
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize OpenAI provider
        
        Args:
            api_key (str): OpenAI API key
            base_url (str, optional): Custom base URL
        """
        super().__init__(api_key, base_url)
        self._setup_openai_session()
    
    def get_default_base_url(self) -> str:
        """Get default OpenAI API base URL"""
        return "https://api.openai.com/v1"
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "OpenAI"
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported OpenAI models"""
        return list(self.MODEL_CONFIGS.keys())
    
    def _setup_openai_session(self) -> None:
        """Setup session with OpenAI-specific headers"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'OpenAI-Beta': 'assistants=v1'
        })
    
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate OpenAI API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API key cannot be empty"
        
        # OpenAI API keys start with 'sk-' and are typically 51 characters long
        if not api_key.startswith('sk-'):
            return False, "OpenAI API key must start with 'sk-'"
        
        if len(api_key) < 20:
            return False, "OpenAI API key is too short"
        
        # Check for valid characters (alphanumeric and some special chars)
        if not re.match(r'^sk-[A-Za-z0-9\-_]+$', api_key):
            return False, "OpenAI API key contains invalid characters"
        
        return True, ""
    
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to OpenAI API
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        try:
            # Test with a simple models list request
            success, response_data, response_time = self._make_request('GET', 'models')
            
            if success:
                # Check if we got a valid models response
                if 'data' in response_data and isinstance(response_data['data'], list):
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
        Generate text using OpenAI's completion API
        
        Args:
            prompt (str): Input prompt
            model_id (str): OpenAI model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from OpenAI
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data
        request_data = {
            "model": model_id,
            "prompt": prompt,
            "max_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
            "temperature": parameters.temperature,
            "top_p": parameters.top_p,
            "frequency_penalty": parameters.frequency_penalty,
            "presence_penalty": parameters.presence_penalty
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["stop"] = parameters.stop_sequences
        
        try:
            success, response_data, response_time = self._make_request('POST', 'completions', request_data)
            
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
            choices = response_data.get('choices', [])
            if not choices:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No response choices returned"
                )
            
            content = choices[0].get('text', '')
            
            # Calculate usage and cost
            usage = response_data.get('usage', {})
            tokens_used = usage.get('total_tokens', self._estimate_tokens(prompt + content))
            cost = self._calculate_cost(tokens_used, model_id)
            
            return ProviderResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                model_used=model_id,
                success=True,
                metadata={
                    'finish_reason': choices[0].get('finish_reason'),
                    'usage': usage
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
        Chat completion using OpenAI's chat API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): OpenAI model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from OpenAI
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data
        request_data = {
            "model": model_id,
            "messages": messages,
            "max_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
            "temperature": parameters.temperature,
            "top_p": parameters.top_p,
            "frequency_penalty": parameters.frequency_penalty,
            "presence_penalty": parameters.presence_penalty
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["stop"] = parameters.stop_sequences
        
        try:
            success, response_data, response_time = self._make_request('POST', 'chat/completions', request_data)
            
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
            choices = response_data.get('choices', [])
            if not choices:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No response choices returned"
                )
            
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            # Calculate usage and cost
            usage = response_data.get('usage', {})
            tokens_used = usage.get('total_tokens', self._estimate_tokens(str(messages) + content))
            cost = self._calculate_cost(tokens_used, model_id)
            
            return ProviderResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                model_used=model_id,
                success=True,
                metadata={
                    'finish_reason': choices[0].get('finish_reason'),
                    'usage': usage,
                    'role': message.get('role', 'assistant')
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
    
    def _calculate_cost(self, tokens_used: int, model_id: str) -> float:
        """
        Calculate cost for OpenAI models
        
        Args:
            tokens_used (int): Number of tokens used
            model_id (str): Model identifier
            
        Returns:
            float: Cost in USD
        """
        if model_id in self.MODEL_CONFIGS:
            cost_per_1k = self.MODEL_CONFIGS[model_id]["cost_per_1k_tokens"]
            return (tokens_used / 1000) * cost_per_1k
        
        # Fallback to base implementation
        return super()._calculate_cost(tokens_used, model_id)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific OpenAI model
        
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
        Validate parameters for OpenAI models
        
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
        
        # OpenAI-specific validation
        if model_id in self.MODEL_CONFIGS:
            max_tokens = self.MODEL_CONFIGS[model_id]["max_tokens"]
            if parameters.max_tokens > max_tokens:
                return False, f"max_tokens cannot exceed {max_tokens} for model {model_id}"
        
        # Validate stop sequences
        if len(parameters.stop_sequences) > 4:
            return False, "OpenAI supports maximum 4 stop sequences"
        
        return True, ""
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available OpenAI models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.MODEL_CONFIGS.keys():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models