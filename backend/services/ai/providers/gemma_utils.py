from typing import Optional, Tuple
from huggingface_hub import HfApi, snapshot_download


def download_latest_gemma_model(cache_dir: str | None = None) -> Tuple[Optional[str], Optional[str]]:
    """Download a suitable local chat model.

    Args:
        cache_dir: Optional directory to download the model into.

    Returns:
        A tuple of ``(local_path, model_id)`` where ``local_path`` is the path
        to the downloaded snapshot and ``model_id`` is the Hugging Face model
        identifier. ``None`` is returned for both values if no model is found.
    """
    
    # Try open models that don't require authentication
    open_models = [
        "microsoft/DialoGPT-small",  # Smaller, faster download
        "distilgpt2",                # Very lightweight
        "gpt2"                       # Classic, reliable
    ]
    
    print("🔍 Trying open chat models...")
    for model_id in open_models:
        try:
            print(f"📥 Downloading {model_id}...")
            local_path = snapshot_download(repo_id=model_id, cache_dir=cache_dir)
            print(f"✅ Successfully downloaded {model_id}")
            return local_path, model_id
        except Exception as e:
            print(f"❌ Failed to download {model_id}: {e}")
            continue
    
    print("❌ No suitable models could be downloaded")
    print("💡 For better models, you can manually download Gemma with authentication:")
    print("💡 1. Run: huggingface-cli login")
    print("💡 2. Accept license at: https://huggingface.co/google/gemma-2-2b-it")
    print("💡 3. Run: python scripts/download-gemma.py")
    
    return None, None
