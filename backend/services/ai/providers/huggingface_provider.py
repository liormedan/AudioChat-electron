"""
Hugging Face API provider integration
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


class HuggingFaceProvider(BaseProvider):
    """Hugging Face API provider implementation"""
    
    # Hugging Face model configurations
    MODEL_CONFIGS = {
        "microsoft/DialoGPT-medium": {
            "name": "DialoGPT Medium",
            "description": "Microsoft's conversational AI model",
            "max_tokens": 1024,
            "context_window": 1024,
            "cost_per_1k_tokens": 0.0002,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT
            ]
        },
        "microsoft/DialoGPT-large": {
            "name": "DialoGPT Large",
            "description": "Larger version of Microsoft's conversational AI",
            "max_tokens": 1024,
            "context_window": 1024,
            "cost_per_1k_tokens": 0.0004,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT
            ]
        },
        "bigscience/bloom": {
            "name": "BLOOM",
            "description": "Large multilingual language model",
            "max_tokens": 2048,
            "context_window": 2048,
            "cost_per_1k_tokens": 0.0006,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.TRANSLATION
            ]
        },
        "meta-llama/Llama-2-7b-chat-hf": {
            "name": "Llama 2 7B Chat",
            "description": "Meta's Llama 2 model fine-tuned for chat",
            "max_tokens": 4096,
            "context_window": 4096,
            "cost_per_1k_tokens": 0.0003,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        },
        "meta-llama/Llama-2-13b-chat-hf": {
            "name": "Llama 2 13B Chat",
            "description": "Larger version of Llama 2 chat model",
            "max_tokens": 4096,
            "context_window": 4096,
            "cost_per_1k_tokens": 0.0005,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        },
        "codellama/CodeLlama-7b-Instruct-hf": {
            "name": "Code Llama 7B Instruct",
            "description": "Meta's Code Llama model for code generation",
            "max_tokens": 4096,
            "context_window": 16384,
            "cost_per_1k_tokens": 0.0003,
            "capabilities": [
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_GENERATION
            ]
        },
        "mistralai/Mistral-7B-Instruct-v0.1": {
            "name": "Mistral 7B Instruct",
            "description": "Mistral AI's instruction-following model",
            "max_tokens": 4096,
            "context_window": 8192,
            "cost_per_1k_tokens": 0.0002,
            "capabilities": [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION
            ]
        }
    }
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize Hugging Face provider
        
        Args:
            api_key (str): Hugging Face API key
            base_url (str, optional): Custom base URL
        """
        super().__init__(api_key, base_url)
        self._setup_huggingface_session()
    
    def get_default_base_url(self) -> str:
        """Get default Hugging Face API base URL"""
        return "https://api-inference.huggingface.co"
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Hugging Face"
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Hugging Face models"""
        return list(self.MODEL_CONFIGS.keys())
    
    def _setup_huggingface_session(self) -> None:
        """Setup session with Hugging Face-specific headers"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Hugging Face API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API key cannot be empty"
        
        # Hugging Face API keys start with 'hf_' and are typically long
        if not api_key.startswith('hf_'):
            return False, "Hugging Face API key must start with 'hf_'"
        
        if len(api_key) < 20:
            return False, "Hugging Face API key is too short"
        
        # Check for valid characters (alphanumeric and some special chars)
        if not re.match(r'^hf_[A-Za-z0-9\-_]+$', api_key):
            return False, "Hugging Face API key contains invalid characters"
        
        return True, ""
    
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to Hugging Face API
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        try:
            # Test with a simple generation request using a lightweight model
            test_data = {
                "inputs": "Hi",
                "parameters": {
                    "max_new_tokens": 10,
                    "temperature": 0.7
                }
            }
            
            # Use DialoGPT-medium for testing as it's relatively fast
            endpoint = "models/microsoft/DialoGPT-medium"
            success, response_data, response_time = self._make_request('POST', endpoint, test_data)
            
            if success:
                # Check if we got a valid response
                if isinstance(response_data, list) and len(response_data) > 0:
                    return True, "Connection successful", response_time
                elif isinstance(response_data, dict) and 'generated_text' in response_data:
                    return True, "Connection successful", response_time
                else:
                    return False, "Invalid response format", response_time
            else:
                error_msg = response_data.get('error', 'Unknown error')
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
        Generate text using Hugging Face's inference API
        
        Args:
            prompt (str): Input prompt
            model_id (str): Hugging Face model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Hugging Face
        """
        # Validate model
        if model_id not in self.MODEL_CONFIGS:
            raise ModelNotFoundError(f"Model {model_id} not supported")
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(parameters, model_id)
        if not is_valid:
            raise ProviderError(error_msg)
        
        # Prepare request data for Hugging Face format
        request_data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": min(parameters.max_tokens, self.MODEL_CONFIGS[model_id]["max_tokens"]),
                "temperature": parameters.temperature,
                "top_p": parameters.top_p,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        # Add stop sequences if provided
        if parameters.stop_sequences:
            request_data["parameters"]["stop"] = parameters.stop_sequences
        
        try:
            endpoint = f"models/{model_id}"
            success, response_data, response_time = self._make_request('POST', endpoint, request_data)
            
            if not success:
                error_msg = response_data.get('error', 'Unknown error')
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
            content = ""
            if isinstance(response_data, list) and len(response_data) > 0:
                content = response_data[0].get('generated_text', '')
            elif isinstance(response_data, dict):
                content = response_data.get('generated_text', '')
            
            if not content:
                return ProviderResponse(
                    content="",
                    tokens_used=0,
                    cost=0.0,
                    response_time=response_time,
                    model_used=model_id,
                    success=False,
                    error_message="No generated text returned"
                )
            
            # Calculate usage and cost (Hugging Face doesn't provide token counts)
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
                    'estimated_tokens': True,
                    'model_type': 'huggingface_inference'
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
        Chat completion using Hugging Face's inference API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Hugging Face model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from Hugging Face
        """
        # Convert messages to a single prompt for most HF models
        prompt = self._format_messages_for_model(messages, model_id)
        
        # Use generate_text for chat completion
        response = self.generate_text(prompt, model_id, parameters)
        
        # Update metadata to indicate this was a chat completion
        if response.metadata:
            response.metadata['request_type'] = 'chat'
            response.metadata['role'] = 'assistant'
        
        return response
    
    def _format_messages_for_model(self, messages: List[Dict[str, str]], model_id: str) -> str:
        """
        Format messages for specific Hugging Face models
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Model identifier
            
        Returns:
            str: Formatted prompt
        """
        if "llama" in model_id.lower():
            # Llama format
            formatted = ""
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                if role == 'system':
                    formatted += f"<<SYS>>\n{content}\n<</SYS>>\n\n"
                elif role == 'user':
                    formatted += f"[INST] {content} [/INST] "
                elif role == 'assistant':
                    formatted += f"{content} "
            
            return formatted.strip()
        
        elif "mistral" in model_id.lower():
            # Mistral format
            formatted = ""
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                if role == 'user':
                    formatted += f"[INST] {content} [/INST] "
                elif role == 'assistant':
                    formatted += f"{content} "
            
            return formatted.strip()
        
        elif "dialogpt" in model_id.lower():
            # DialoGPT format - just use the last user message
            for message in reversed(messages):
                if message.get('role') == 'user':
                    return message.get('content', '')
            return ""
        
        else:
            # Default format - concatenate all messages
            formatted = ""
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                formatted += f"{role.title()}: {content}\n"
            
            formatted += "Assistant:"
            return formatted
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """
        Calculate cost for Hugging Face models
        
        Args:
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens
            model_id (str): Model identifier
            
        Returns:
            float: Cost in USD
        """
        if model_id in self.MODEL_CONFIGS:
            cost_per_1k = self.MODEL_CONFIGS[model_id]["cost_per_1k_tokens"]
            total_tokens = input_tokens + output_tokens
            return (total_tokens / 1000) * cost_per_1k
        
        # Fallback to base implementation
        return super()._calculate_cost(input_tokens + output_tokens, model_id)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific Hugging Face model
        
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
                "provider_model_id": model_id,
                "model_type": "huggingface_inference"
            }
        }
    
    def validate_parameters(self, parameters: LLMParameters, model_id: str) -> Tuple[bool, str]:
        """
        Validate parameters for Hugging Face models
        
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
        
        # Hugging Face-specific validation
        if model_id in self.MODEL_CONFIGS:
            max_tokens = self.MODEL_CONFIGS[model_id]["max_tokens"]
            if parameters.max_tokens > max_tokens:
                return False, f"max_tokens cannot exceed {max_tokens} for model {model_id}"
        
        # Most HF models don't support frequency_penalty and presence_penalty
        if parameters.frequency_penalty != 0.0:
            return False, "Most Hugging Face models do not support frequency_penalty"
        
        if parameters.presence_penalty != 0.0:
            return False, "Most Hugging Face models do not support presence_penalty"
        
        return True, ""
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available Hugging Face models
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.MODEL_CONFIGS.keys():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
