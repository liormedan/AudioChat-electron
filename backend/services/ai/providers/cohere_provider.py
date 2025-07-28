"""
Cohere API provider integration
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


class CohereProvider(BaseProvider):
    """Cohere API provider implementation"""
    
    # Cohere model configurations
    MODEL_CONFIGS = {
        "command": {
            "name": "Command",
            "description": "Cohere's flagship text generation model",
            "max_tokens": 4096,
            "context_window": 4096,
            "cost_per_1k_tokens": 0.002,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION
            ]
        },
        "command-light": {
            "name": "Command Light",
            "description": "Faster, lighter version of Command model",
            "max_tokens": 4096,
            "context_window": 4096,
            "cost_per_1k_tokens": 0.0006,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION
            ]
        },
        "command-nightly": {
            "name": "Command Nightly",
            "description": "Latest experimental Command model",
            "max_tokens": 4096,
            "context_window": 4096,
            "cost_per_1k_tokens": 0.002,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION,
                ModelCapability.CODE_GENERATION
            ]
        },
        "command-r": {
            "name": "Command R",
            "description": "Cohere's retrieval-augmented generation model",
            "max_tokens": 4096,
            "context_window": 128000,
            "cost_per_1k_tokens": {
                "input": 0.0005,
                "output": 0.0015
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION
            ]
        }
    }
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize Cohere provider
        
        Args:
            api_key (str): Cohere API key
            base_url (str, optional): Custom base URL
        """
        super().__init__(api_key, base_url)
        self._setup_cohere_session()
    
    def get_default_base_url(self) -> str:
        """Get default Cohere API base URL"""
        return "https://api.cohere.ai/v1"
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Cohere"
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Cohere models"""
        return list(self.MODEL_CONFIGS.keys())
    
    def _setup_cohere_session(self) -> None:
        """Setup session with Cohere-specific headers"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Cohere-Version': '2022-12-06'
        })
    
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Cohere API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API key cannot be empty"
        
        # Cohere API keys are typically long alphanumeric strings
        if len(api_key) < 20:
            return False, "Cohere API key is too short"
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[A-Za-z0-9\-_]+$', api_key):
            return False, "Cohere API key contains invalid characters"
        
        return True, ""
    
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to Cohere API
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        try:
            # Test with a simple generation request
            test_data = {
                "model": "command-light",
                "prompt": "Hi",
                "max_tokens": 10
            }
            
            success, response_data, response_time = self._make_request('POST', 'generate', test_data)
            
            if success:
                # Check if we got a valid response
                if 'generations' in response_data and isinstance(response_data['generations'], list):
                    return True, "Connection successful", response_time
                else:
                    return False, "Invalid response format", response_time
            else:
                error_msg = response_data.get('message', 'Unknown error')
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
        Generate text using Cohere's generate API
        
        Args:
            prompt (str): Input prompt
            model_id (str): Cohere model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Cohere
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data for Cohere format
        request_data = {
            "model": model_id,
            "prompt": prompt,
            "max_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
            "temperature": parameters.temperature,
            "p": parameters.top_p,  # Cohere uses 'p' instead of 'top_p'
            "truncate": "END"
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["stop_sequences"] = parameters.stop_sequences
        
        try:
            success, response_data, response_time = self._make_request('POST', 'generate', request_data)
            
            if not success:
                error_msg = response_data.get('message', 'Unknown error')
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
            generations = response_data.get('generations', [])
            if not generations:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No generations returned"
                )
            
            content = generations[0].get('text', '')
            
            # Calculate usage and cost
            meta = response_data.get('meta', {})
            billed_units = meta.get('billed_units', {})
            input_tokens = billed_units.get('input_tokens', 0)
            output_tokens = billed_units.get('output_tokens', 0)
            tokens_used = input_tokens + output_tokens
            
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
                    'finish_reason': generations[0].get('finish_reason'),
                    'billed_units': billed_units,
                    'warnings': meta.get('warnings', [])
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
        Chat completion using Cohere's chat API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Cohere model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Cohere
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Convert messages to Cohere format
        chat_history = []
        message = ""
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                message = content  # Last user message becomes the main message
            elif role == 'assistant':
                chat_history.append({
                    "role": "CHATBOT",
                    "message": content
                })
            elif role == 'system':
                # System messages can be added to preamble
                pass
        
        # Prepare request data
        request_data = {
            "model": model_id,
            "message": message,
            "max_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
            "temperature": parameters.temperature,
            "p": parameters.top_p
        }
        
        # Add chat history if available
        if chat_history:
            request_data["chat_history"] = chat_history
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["stop_sequences"] = parameters.stop_sequences
        
        try:
            success, response_data, response_time = self._make_request('POST', 'chat', request_data)
            
            if not success:
                error_msg = response_data.get('message', 'Unknown error')
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
            content = response_data.get('text', '')
            
            # Calculate usage and cost
            meta = response_data.get('meta', {})
            billed_units = meta.get('billed_units', {})
            input_tokens = billed_units.get('input_tokens', 0)
            output_tokens = billed_units.get('output_tokens', 0)
            tokens_used = input_tokens + output_tokens
            
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
                    'finish_reason': response_data.get('finish_reason'),
                    'billed_units': billed_units,
                    'warnings': meta.get('warnings', []),
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
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """
        Calculate cost for Cohere models
        
        Args:
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens
            model_id (str): Model identifier
            
        Returns:
            float: Cost in USD
        """
        if model_id in self.MODEL_CONFIGS:
            cost_config = self.MODEL_CONFIGS[model_id]["cost_per_1k_tokens"]
            input_cost = (input_tokens / 1000) * cost_config["input"]
            output_cost = (output_tokens / 1000) * cost_config["output"]
            return input_cost + output_cost
        
        # Fallback to base implementation
        return super()._calculate_cost(input_tokens + output_tokens, model_id)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific Cohere model
        
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
        Validate parameters for Cohere models
        
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
        
        # Cohere-specific validation
        if model_id in self.MODEL_CONFIGS:
            max_tokens = self.MODEL_CONFIGS[model_id]["max_tokens"]
            if parameters.max_tokens > max_tokens:
                return False, f"max_tokens cannot exceed {max_tokens} for model {model_id}"
        
        # Cohere doesn't support frequency_penalty and presence_penalty
        if parameters.frequency_penalty != 0.0:
            return False, "Cohere models do not support frequency_penalty"
        
        if parameters.presence_penalty != 0.0:
            return False, "Cohere models do not support presence_penalty"
        
        return True, ""
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available Cohere models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.MODEL_CONFIGS.keys():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
