"""
Provider for running local Gemma models using Hugging Face Transformers
"""

import os
import torch, gc
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Optional

from .base_provider import BaseProvider, ProviderResponse
from backend.models.commands import LLMParameters

class LocalGemmaProvider(BaseProvider):
    """Provider for local Gemma models"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initializes the LocalGemmaProvider.

        Args:
            api_key (str, optional): Not used for this provider. Defaults to None.
            base_url (str, optional): Not used for this provider. Defaults to None.
        """
        super().__init__(api_key, base_url)
        self.active_model_name: Optional[str] = None
        self._loaded_models: Dict[str, pipeline] = {}

    def _load_model(self, model_id: str):
        """Initializes the model and tokenizer pipeline.

        The ``model_id`` argument can be either a Hugging Face model ID or a
        path to a previously downloaded snapshot.  The loaded pipeline is
        cached so subsequent calls are fast.
        """
        if model_id in self._loaded_models:
            self.active_model_name = model_id
            print(f"Switched to already loaded model '{model_id}'.")
            return True

        print("\n" + "=" * 50)
        print(f"INFO: Loading local model '{model_id}'.")
        print(
            "This might take a while, especially on the first run as the model (several GB) is downloaded."
        )
        print("Please watch the console for a download progress bar.")
        print("=" * 50 + "\n")

        try:
            # Determine the actual path or model ID
            path_to_use = model_id
            if os.path.isdir(model_id):
                path_to_use = model_id

            # Determine the device
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # Set torch_dtype based on device
            torch_dtype = (
                torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
            )

            model_pipeline = pipeline(
                "text-generation",
                model=path_to_use,
                device=device,
                torch_dtype=torch_dtype,
            )
            self._loaded_models[model_id] = model_pipeline
            self.active_model_name = model_id
            print(f"Successfully loaded model '{model_id}' on {device}.")
            return True
        except Exception as e:
            print(f"Error initializing local Gemma model: {e}")
            return False

    def unload_model(self, model_id: Optional[str] = None):
        """Unloads a specific model or all models to free up memory."""
        model_to_unload = model_id or self.active_model_name
        if model_to_unload and model_to_unload in self._loaded_models:
            del self._loaded_models[model_to_unload]
            gc.collect()
            torch.cuda.empty_cache()
            print(f"Model '{model_to_unload}' unloaded.")

    def chat_completion(self, messages: List[Dict[str, str]], model_id: str, params: LLMParameters) -> Optional[ProviderResponse]:
        """
        Generate a chat completion using the local Gemma model.

        Args:
            messages (List[Dict[str, str]]): A list of messages in the conversation.
            model_id (str): The ID of the model to use (e.g., 'gemma-3-4b-it').
            params (LLMParameters): The parameters for the generation.

        Returns:
            Optional[ProviderResponse]: The response from the provider or None on failure.
        """
        # Load or switch model if necessary
        if model_id not in self._loaded_models:
            if not self._load_model(model_id):
                return ProviderResponse(
                    success=False,
                    content=f"Failed to load local Gemma model: {model_id}",
                    error_message=f"Could not initialize model: {model_id}"
                )
        
        self.active_model_name = model_id
        active_pipe = self._loaded_models[self.active_model_name]

        try:
            # Convert messages to the format expected by the model's chat template
            prompt = active_pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            
            # Generate the response
            outputs = active_pipe(
                prompt,
                max_new_tokens=params.max_tokens,
                do_sample=True,
                temperature=params.temperature,
                top_p=params.top_p,
                top_k=params.top_k
            )
            
            # Extract only the generated text
            generated_text = outputs[0]["generated_text"][len(prompt):]
            
            prompt_tokens = len(active_pipe.tokenizer.encode(prompt))
            completion_tokens = len(active_pipe.tokenizer.encode(generated_text))

            return ProviderResponse(
                success=True,
                content=generated_text.strip(),
                model_id=self.active_model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            )
        except Exception as e:
            return ProviderResponse(
                success=False,
                content=None,
                error_message=str(e)
            )

    def test_connection(self) -> tuple[bool, str, float]:
        """
        Test the connection to the local model.
        For local models, this just checks if the model is loaded.
        """
        # Try to load the default model to test functionality
        default_model = "google/gemma-2-2b-it" # Use a smaller model for a quick test
        if self._load_model(default_model):
            # Unload it right after to save resources if not needed immediately
            self.unload_model(default_model)
            return True, "Model loaded successfully.", 0.0
        else:
            return False, "Model failed to initialize.", 0.0
