import asyncio

import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app


def _call_openrouter_sync(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter returned {response.status_code}: {response.text}"
        )
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _send_telegram_message_sync(chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    with httpx.Client(timeout=30.0) as client:
        client.post(url, json={"chat_id": chat_id, "text": text})


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    try:
        answer = _call_openrouter_sync(prompt)
    except Exception as e:
        answer = f"Error calling LLM: {e}"

    _send_telegram_message_sync(tg_chat_id, answer)
    return answer
