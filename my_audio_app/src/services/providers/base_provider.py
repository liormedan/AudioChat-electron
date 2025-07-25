"""
Base provider class for LLM integrations
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import requests
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.llm_models import LLMModel, LLMParameters, UsageRecord


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class AuthenticationError(ProviderError):
    """Authentication failed"""
    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    pass


class ModelNotFoundError(ProviderError):
    """Model not found or not available"""
    pass


class InvalidParametersError(ProviderError):
    """Invalid parameters provided"""
    pass


@dataclass
class ProviderResponse:
    """Response from provider API"""
    content: str
    tokens_used: int
    cost: float
    response_time: float
    model_used: str
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize provider
        
        Args:
            api_key (str): API key for authentication
            base_url (str, optional): Base URL for API calls
        """
        self.api_key = api_key
        self.base_url = base_url or self.get_default_base_url()
        self.session = requests.Session()
        self._setup_session()
    
    @abstractmethod
    def get_default_base_url(self) -> str:
        """Get default base URL for this provider"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported model IDs"""
        pass
    
    @abstractmethod
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate API key format
        
        Args:
            api_key (str): API key to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str, float]:
        """
        Test connection to provider
        
        Returns:
            Tuple[bool, str, float]: (success, message, response_time)
        """
        pass
    
    @abstractmethod
    def generate_text(self, 
                     prompt: str, 
                     model_id: str, 
                     parameters: LLMParameters) -> ProviderResponse:
        """
        Generate text using the provider's API
        
        Args:
            prompt (str): Input prompt
            model_id (str): Model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from the provider
        """
        pass
    
    @abstractmethod
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model_id: str, 
                       parameters: LLMParameters) -> ProviderResponse:
        """
        Chat completion using the provider's API
        
        Args:
            messages (List[Dict[str, str]]): Chat messages
            model_id (str): Model identifier
            parameters (LLMParameters): Generation parameters
            
        Returns:
            ProviderResponse: Response from the provider
        """
        pass
    
    def _setup_session(self) -> None:
        """Setup HTTP session with common headers"""
        self.session.headers.update({
            'User-Agent': 'AudioChatQT/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     data: Dict[str, Any] = None,
                     timeout: int = 30) -> Tuple[bool, Dict[str, Any], float]:
        """
        Make HTTP request to provider API
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            data (Dict[str, Any], optional): Request data
            timeout (int): Request timeout in seconds
            
        Returns:
            Tuple[bool, Dict[str, Any], float]: (success, response_data, response_time)
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Handle different response status codes
            if response.status_code == 200:
                return True, response.json(), response_time
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                raise ModelNotFoundError("Model not found or endpoint not available")
            else:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                
                return False, error_data, response_time
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            raise ProviderError(f"Request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            raise ProviderError("Connection error - check internet connection")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            raise ProviderError(f"Request failed: {str(e)}")
    
    def _calculate_cost(self, tokens_used: int, model_id: str) -> float:
        """
        Calculate cost based on tokens used
        
        Args:
            tokens_used (int): Number of tokens used
            model_id (str): Model identifier
            
        Returns:
            float: Estimated cost in USD
        """
        # This should be overridden by each provider with their specific pricing
        return tokens_used * 0.00002  # Default fallback rate
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text (str): Input text
            
        Returns:
            int: Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def _create_usage_record(self, 
                           response: ProviderResponse, 
                           model_id: str,
                           request_type: str = "chat") -> UsageRecord:
        """
        Create usage record from provider response
        
        Args:
            response (ProviderResponse): Provider response
            model_id (str): Model identifier
            request_type (str): Type of request
            
        Returns:
            UsageRecord: Usage record for tracking
        """
        return UsageRecord(
            id=f"{self.get_provider_name()}_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            model_id=model_id,
            provider=self.get_provider_name(),
            tokens_used=response.tokens_used,
            cost=response.cost,
            response_time=response.response_time,
            success=response.success,
            error_message=response.error_message,
            request_type=request_type,
            metadata=response.metadata
        )
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model
        
        Args:
            model_id (str): Model identifier
            
        Returns:
            Optional[Dict[str, Any]]: Model information or None if not found
        """
        # Default implementation - should be overridden by providers
        if model_id in self.get_supported_models():
            return {
                "id": model_id,
                "name": model_id,
                "provider": self.get_provider_name(),
                "description": f"Model {model_id} from {self.get_provider_name()}",
                "max_tokens": 4096,
                "context_window": 4096
            }
        return None
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from this provider
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models = []
        for model_id in self.get_supported_models():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
    
    def validate_parameters(self, parameters: LLMParameters, model_id: str) -> Tuple[bool, str]:
        """
        Validate parameters for a specific model
        
        Args:
            parameters (LLMParameters): Parameters to validate
            model_id (str): Model identifier
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Basic validation - can be overridden by providers
        if not parameters.validate():
            return False, "Invalid parameter values"
        
        if model_id not in self.get_supported_models():
            return False, f"Model {model_id} not supported by {self.get_provider_name()}"
        
        return True, ""
    
    def __del__(self):
        """Cleanup when provider is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
