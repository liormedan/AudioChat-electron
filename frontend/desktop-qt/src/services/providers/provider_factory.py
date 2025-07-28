"""
Provider factory for creating and managing LLM provider instances
"""

from typing import Dict, Type, Optional, List
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .cohere_provider import CohereProvider
from .huggingface_provider import HuggingFaceProvider


class ProviderFactory:
    """Factory for creating LLM provider instances"""
    
    # Registry of available providers
    PROVIDERS: Dict[str, Type[BaseProvider]] = {
        "OpenAI": OpenAIProvider,
        "Anthropic": AnthropicProvider,
        "Google": GoogleProvider,
        "Cohere": CohereProvider,
        "Hugging Face": HuggingFaceProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: str, base_url: str = None) -> Optional[BaseProvider]:
        """
        Create a provider instance
        
        Args:
            provider_name (str): Name of the provider
            api_key (str): API key for authentication
            base_url (str, optional): Custom base URL
            
        Returns:
            Optional[BaseProvider]: Provider instance or None if not found
        """
        provider_class = cls.PROVIDERS.get(provider_name)
        if not provider_class:
            return None
        
        try:
            return provider_class(api_key, base_url)
        except Exception as e:
            print(f"Error creating provider {provider_name}: {e}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider names
        
        Returns:
            List[str]: List of provider names
        """
        return list(cls.PROVIDERS.keys())
    
    @classmethod
    def is_provider_supported(cls, provider_name: str) -> bool:
        """
        Check if a provider is supported
        
        Args:
            provider_name (str): Provider name to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return provider_name in cls.PROVIDERS
    
    @classmethod
    def get_provider_class(cls, provider_name: str) -> Optional[Type[BaseProvider]]:
        """
        Get provider class by name
        
        Args:
            provider_name (str): Provider name
            
        Returns:
            Optional[Type[BaseProvider]]: Provider class or None if not found
        """
        return cls.PROVIDERS.get(provider_name)
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a new provider
        
        Args:
            provider_name (str): Name of the provider
            provider_class (Type[BaseProvider]): Provider class
        """
        cls.PROVIDERS[provider_name] = provider_class
    
    @classmethod
    def unregister_provider(cls, provider_name: str) -> bool:
        """
        Unregister a provider
        
        Args:
            provider_name (str): Name of the provider to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if provider_name in cls.PROVIDERS:
            del cls.PROVIDERS[provider_name]
            return True
        return False
