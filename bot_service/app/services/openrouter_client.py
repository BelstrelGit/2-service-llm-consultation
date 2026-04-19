import httpx

from app.core.config import settings


def _build_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
        "Content-Type": "application/json",
    }


def _build_payload(prompt: str) -> dict:
    return {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }


def _parse_response(response: httpx.Response) -> str:
    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter returned {response.status_code}: {response.text}"
        )
    data = response.json()
    return data["choices"][0]["message"]["content"]


async def call_openrouter(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=_build_headers(),
                json=_build_payload(prompt),
            )
    except httpx.HTTPError as e:
        raise RuntimeError(f"OpenRouter request failed: {e}") from e

    return _parse_response(response)


def call_openrouter_sync(prompt: str) -> str:
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=_build_headers(),
                json=_build_payload(prompt),
            )
    except httpx.HTTPError as e:
        raise RuntimeError(f"OpenRouter request failed: {e}") from e

    return _parse_response(response)
