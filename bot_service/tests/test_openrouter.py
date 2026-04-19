"""Integration test for OpenRouter client using respx."""

import httpx
import pytest
import respx
from httpx import Response

from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_success():
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Лев Толстой — великий русский писатель."
                }
            }
        ]
    }

    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(200, json=mock_response)
    )

    result = await call_openrouter("Расскажи про Толстого")
    assert result == "Лев Толстой — великий русский писатель."


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_error():
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(500, text="Internal Server Error")
    )

    with pytest.raises(RuntimeError, match="500"):
        await call_openrouter("test prompt")


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_network_error():
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    with pytest.raises(RuntimeError, match="request failed"):
        await call_openrouter("test prompt")
