import pytest

from backend.services.ai.llm_service import LLMService
from backend.services.ai.providers.google_provider import GoogleProvider

@pytest.mark.asyncio
async def test_stream_chat_response_uses_provider(monkeypatch):
    service = LLMService(db_path=":memory:")
    assert service.set_active_model("google-gemini-pro")

    provider = GoogleProvider(api_key="test")

    def fake_stream(messages, model_id, params, timeout=60):
        yield "foo"
        yield "bar"

    monkeypatch.setattr(service, "_get_provider_instance", lambda name: provider)
    provider.stream_chat_completion = fake_stream

    chunks = []
    async for chunk in service.stream_chat_response([{"role": "user", "content": "hi"}]):
        chunks.append(chunk)

    assert chunks == ["foo", "bar"]
