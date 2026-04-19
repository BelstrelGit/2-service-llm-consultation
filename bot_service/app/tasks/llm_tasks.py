import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter_sync


def _send_telegram_message_sync(chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    with httpx.Client(timeout=30.0) as client:
        client.post(url, json={"chat_id": chat_id, "text": text})


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    try:
        answer = call_openrouter_sync(prompt)
    except Exception as e:
        answer = f"Error calling LLM: {e}"

    _send_telegram_message_sync(tg_chat_id, answer)
    return answer
