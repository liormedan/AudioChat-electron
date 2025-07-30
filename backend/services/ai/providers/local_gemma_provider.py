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
        print("=" * 50 + "\n")

        try:
            # Check for downloaded model first
            local_path = self._get_local_model_path()
            if local_path:
                path_to_use = local_path
                print(f"Using downloaded model: {local_path}")
            else:
                # Map model IDs to actual model paths/names
                model_mapping = {
                    "microsoft-dialogpt-medium": "microsoft/DialoGPT-medium",
                    "local-gemma-3-4b-it": "google/gemma-3-4b-it", 
                    "google-gemma-2-2b-it": "google/gemma-2-2b-it"
                }
                path_to_use = model_mapping.get(model_id, model_id)
                print(f"Using model ID: {path_to_use}")
            
            print(f"Using model path: {path_to_use}")

            # Determine the device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")

            # Set torch_dtype based on device
            torch_dtype = (
                torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
            )

            # Choose appropriate task based on model
            task = "conversational" if "dialogpt" in actual_model_name.lower() else "text-generation"
            
            model_pipeline = pipeline(
                task,
                model=path_to_use,
                device=device,
                torch_dtype=torch_dtype,
            )
            self._loaded_models[model_id] = model_pipeline
            self.active_model_name = model_id
            print(f"Successfully loaded model '{model_id}' on {device}.")
            return True
        except Exception as e:
            print(f"Error initializing local model: {e}")
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
            # Handle different model types
            if hasattr(active_pipe, 'task') and active_pipe.task == 'conversational':
                # DialoGPT conversational model
                from transformers import Conversation
                
                # Convert messages to conversation format
                conversation_text = ""
                for msg in messages:
                    if msg['role'] == 'user':
                        conversation_text += msg['content'] + " "
                
                conversation = Conversation(conversation_text.strip())
                result = active_pipe(conversation)
                generated_text = result.generated_responses[-1] if result.generated_responses else "I'm sorry, I couldn't generate a response."
                
                prompt_tokens = len(conversation_text.split())
                completion_tokens = len(generated_text.split())
                
            else:
                # Standard text generation model
                # Convert messages to simple prompt
                prompt = ""
                for msg in messages:
                    if msg['role'] == 'user':
                        prompt += f"User: {msg['content']}\n"
                    elif msg['role'] == 'assistant':
                        prompt += f"Assistant: {msg['content']}\n"
                
                prompt += "Assistant: "
                
                # Generate the response
                outputs = active_pipe(
                    prompt,
                    max_new_tokens=params.max_tokens,
                    do_sample=True,
                    temperature=params.temperature,
                    top_p=params.top_p,
                    top_k=params.top_k,
                    pad_token_id=active_pipe.tokenizer.eos_token_id
                )
                
                # Extract only the generated text
                generated_text = outputs[0]["generated_text"][len(prompt):].strip()
                
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
        default_model = "microsoft-dialogpt-medium" # Use the downloaded model
        if self._load_model(default_model):
            # Test a simple generation
            try:
                from backend.models.commands import LLMParameters
                test_messages = [{"role": "user", "content": "Hello"}]
                params = LLMParameters()
                response = self.chat_completion(test_messages, default_model, params)
                if response and response.success:
                    return True, "Model loaded and tested successfully.", 0.0
                else:
                    return False, "Model loaded but failed to generate response.", 0.0
            except Exception as e:
                return False, f"Model loaded but test failed: {e}", 0.0
        else:
            return False, "Model failed to initialize.", 0.0
