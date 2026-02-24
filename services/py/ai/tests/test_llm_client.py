import json

import httpx
import pytest
from unittest.mock import AsyncMock, patch

from common.errors import AppError
from app.repositories.llm_client import GeminiClient, GEMINI_API_URL


def _make_gemini_response(text: str, tokens_in: int = 10, tokens_out: int = 20) -> dict:
    return {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
        "usageMetadata": {
            "promptTokenCount": tokens_in,
            "candidatesTokenCount": tokens_out,
        },
    }


async def test_generate_success():
    mock_response = httpx.Response(200, json=_make_gemini_response("Hello world"))
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.return_value = mock_response

    client = GeminiClient(http, "test-key", "gemini-2.0-flash-lite")
    text, tokens_in, tokens_out = await client.generate("test prompt")

    assert text == "Hello world"
    assert tokens_in == 10
    assert tokens_out == 20
    http.post.assert_called_once()
    call_args = http.post.call_args
    assert "test-key" in str(call_args)


async def test_generate_sends_correct_payload():
    mock_response = httpx.Response(200, json=_make_gemini_response("result"))
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.return_value = mock_response

    client = GeminiClient(http, "key123", "gemini-2.0-flash-lite")
    await client.generate("my prompt")

    call_kwargs = http.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert payload["contents"][0]["parts"][0]["text"] == "my prompt"
    assert payload["generationConfig"]["temperature"] == 0.3


@patch("app.repositories.llm_client.asyncio.sleep", new_callable=AsyncMock)
async def test_generate_retries_on_429(mock_sleep):
    error_resp = httpx.Response(429, json={"error": "rate limited"})
    success_resp = httpx.Response(200, json=_make_gemini_response("ok"))
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.side_effect = [error_resp, success_resp]

    client = GeminiClient(http, "key", "gemini-2.0-flash-lite")
    text, _, _ = await client.generate("test")

    assert text == "ok"
    assert http.post.call_count == 2
    mock_sleep.assert_called_once_with(1)


@patch("app.repositories.llm_client.asyncio.sleep", new_callable=AsyncMock)
async def test_generate_retries_on_500(mock_sleep):
    error_resp = httpx.Response(500, json={"error": "internal"})
    success_resp = httpx.Response(200, json=_make_gemini_response("recovered"))
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.side_effect = [error_resp, success_resp]

    client = GeminiClient(http, "key", "gemini-2.0-flash-lite")
    text, _, _ = await client.generate("test")

    assert text == "recovered"
    assert http.post.call_count == 2


@patch("app.repositories.llm_client.asyncio.sleep", new_callable=AsyncMock)
async def test_generate_fails_after_3_retries(mock_sleep):
    error_resp = httpx.Response(429, json={"error": "rate limited"})
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.return_value = error_resp

    client = GeminiClient(http, "key", "gemini-2.0-flash-lite")
    with pytest.raises(AppError) as exc_info:
        await client.generate("test")

    assert exc_info.value.status_code == 502
    assert http.post.call_count == 3


async def test_generate_raises_on_400():
    error_resp = httpx.Response(400, text="Bad request")
    http = AsyncMock(spec=httpx.AsyncClient)
    http.post.return_value = error_resp

    client = GeminiClient(http, "key", "gemini-2.0-flash-lite")
    with pytest.raises(AppError) as exc_info:
        await client.generate("test")

    assert exc_info.value.status_code == 502


async def test_model_name():
    http = AsyncMock(spec=httpx.AsyncClient)
    client = GeminiClient(http, "key", "gemini-2.0-flash-lite")
    assert client.model_name == "gemini-2.0-flash-lite"
