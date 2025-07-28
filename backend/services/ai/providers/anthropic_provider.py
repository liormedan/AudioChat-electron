"""
Anthropic Claude API provider integration
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


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider implementation"""
    
    # Anthropic model configurations
    MODEL_CONFIGS = {
        "claude-3-opus-20240229": {
            "name": "Claude 3 Opus",
            "description": "Most powerful Claude model for complex tasks",
            "max_tokens": 4096,
            "context_window": 200000,
            "cost_per_1k_tokens": {
                "input": 0.015,
                "output": 0.075
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.TRANSLATION
            ]
        },
        "claude-3-sonnet-20240229": {
            "name": "Claude 3 Sonnet",
            "description": "Balanced Claude model for most tasks",
            "max_tokens": 4096,
            "context_window": 200000,
            "cost_per_1k_tokens": {
                "input": 0.003,
                "output": 0.015
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.TRANSLATION
            ]
        },
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku",
            "description": "Fastest Claude model for simple tasks",
            "max_tokens": 4096,
            "context_window": 200000,
            "cost_per_1k_tokens": {
                "input": 0.00025,
                "output": 0.00125
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.SUMMARIZATION
            ]
        },
        "claude-2.1": {
            "name": "Claude 2.1",
            "description": "Previous generation Claude model",
            "max_tokens": 4096,
            "context_window": 200000,
            "cost_per_1k_tokens": {
                "input": 0.008,
                "output": 0.024
            },
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.SUMMARIZATION
            ]
        }
    }
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize Anthropic provider
        
        Args:
            api_key (str): Anthropic API key
            base_url (str, optional): Custom base URL
        """
        super().__init__(api_key, base_url)
        self._setup_anthropic_session()
    
    def get_default_base_url(self) -> str:
        """Get default Anthropic API base URL"""
        return "https://api.anthropic.com/v1"
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Anthropic"
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Anthropic models"""
        return list(self.MODEL_CONFIGS.keys())
    
    def _setup_anthropic_session(self) -> None:
        """Setup session with Anthropic-specific headers"""
        self.session.headers.update({
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        })
    
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Anthropic API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API key cannot be empty"
        
        # Anthropic API keys start with 'sk-ant-' and are typically longer
        if not api_key.startswith('sk-ant-'):
            return False, "Anthropic API key must start with 'sk-ant-'"
        
        if len(api_key) < 30:
            return False, "Anthropic API key is too short"
        
        # Check for valid characters
        if not re.match(r'^sk-ant-[A-Za-z0-9\-_]+$', api_key):
            return False, "Anthropic API key contains invalid characters"
        
        return True, ""
    
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to Anthropic API
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        try:
            # Test with a simple message request
            test_data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            
            success, response_data, response_time = self._make_request('POST', 'messages', test_data)
            
            if success:
                # Check if we got a valid response
                if 'content' in response_data and isinstance(response_data['content'], list):
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
        Generate text using Anthropic's messages API
        
        Args:
            prompt (str): Input prompt
            model_id (str): Anthropic model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Anthropic
        """
        # Convert to chat format for Anthropic
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, model_id, parameters)
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model_id: str, 
                       parameters: LLMParameters) -> ProviderResponse:
        """
        Chat completion using Anthropic's messages API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Anthropic model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Anthropic
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data for Anthropic format
        request_data = {
            "model": model_id,
            "max_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
            "messages": messages
        }
        
        # Add temperature if not default
        if parameters.temperature != 0.7:
            request_data["temperature"] = parameters.temperature
        
        # Add top_p if not default
        if parameters.top_p != 0.9:
            request_data["top_p"] = parameters.top_p
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["stop_sequences"] = parameters.stop_sequences
        
        try:
            success, response_data, response_time = self._make_request('POST', 'messages', request_data)
            
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
            content_blocks = response_data.get('content', [])
            if not content_blocks:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No content blocks returned"
                )
            
            # Combine text from all content blocks
            content = ""
            for block in content_blocks:
                if block.get('type') == 'text':
                    content += block.get('text', '')
            
            # Calculate usage and cost
            usage = response_data.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
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
                    'stop_reason': response_data.get('stop_reason'),
                    'usage': usage,
                    'role': response_data.get('role', 'assistant')
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
        Calculate cost for Anthropic models
        
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
        Get information about a specific Anthropic model
        
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
        Validate parameters for Anthropic models
        
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
        
        # Anthropic-specific validation
        if model_id in self.MODEL_CONFIGS:
            max_tokens = self.MODEL_CONFIGS[model_id]["max_tokens"]
            if parameters.max_tokens > max_tokens:
                return False, f"max_tokens cannot exceed {max_tokens} for model {model_id}"
        
        # Anthropic doesn't support frequency_penalty and presence_penalty
        if parameters.frequency_penalty != 0.0:
            return False, "Anthropic models do not support frequency_penalty"
        
        if parameters.presence_penalty != 0.0:
            return False, "Anthropic models do not support presence_penalty"
        
        return True, ""
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available Anthropic models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.MODEL_CONFIGS.keys():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
