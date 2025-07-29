from typing import Optional, Tuple
from huggingface_hub import HfApi, snapshot_download


def download_latest_gemma_model(cache_dir: str | None = None) -> Tuple[Optional[str], Optional[str]]:
    """Download the latest ``google/gemma-*`` model from Hugging Face.

    Args:
        cache_dir: Optional directory to download the model into.

    Returns:
        A tuple of ``(local_path, model_id)`` where ``local_path`` is the path
        to the downloaded snapshot and ``model_id`` is the Hugging Face model
        identifier. ``None`` is returned for both values if no Gemma model is
        found.
    """
    api = HfApi()
    models = api.list_models(author="google", search="gemma-")
    gemma_models = [m for m in models if m.modelId.startswith("google/gemma-")]
    if not gemma_models:
        return None, None

    latest = max(gemma_models, key=lambda m: m.lastModified)
    repo_id = latest.modelId
    local_path = snapshot_download(repo_id=repo_id, cache_dir=cache_dir)
    return local_path, repo_id
