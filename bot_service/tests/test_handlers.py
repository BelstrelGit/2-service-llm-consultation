"""Mock tests for Telegram bot handlers."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.core.config import settings


def _make_token(sub: str = "1", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def _make_message(text: str, user_id: int = 111, chat_id: int = 222) -> MagicMock:
    message = AsyncMock()
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.chat = MagicMock()
    message.chat.id = chat_id
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_token_command_saves_to_redis(fake_redis):
    token = _make_token(sub="42")

    with patch("app.bot.handlers.get_redis", return_value=fake_redis):
        from app.bot.handlers import cmd_token

        message = _make_message(f"/token {token}", user_id=111)
        await cmd_token(message)

    stored = await fake_redis.get("token:111")
    assert stored == token
    message.answer.assert_called_once_with("Токен сохранён. Теперь можно отправлять запросы модели.")


@pytest.mark.asyncio
async def test_token_command_invalid_jwt(fake_redis):
    with patch("app.bot.handlers.get_redis", return_value=fake_redis):
        from app.bot.handlers import cmd_token

        message = _make_message("/token garbage_token", user_id=111)
        await cmd_token(message)

    stored = await fake_redis.get("token:111")
    assert stored is None
    message.answer.assert_called_once()
    assert "невалиден" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_text_without_token_denied(fake_redis):
    with patch("app.bot.handlers.get_redis", return_value=fake_redis):
        from app.bot.handlers import handle_text

        message = _make_message("Привет, расскажи про Python", user_id=111)
        await handle_text(message)

    message.answer.assert_called_once()
    assert "нет токена" in message.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_text_with_valid_token_calls_celery(fake_redis):
    token = _make_token(sub="42")
    await fake_redis.set("token:111", token)

    with (
        patch("app.bot.handlers.get_redis", return_value=fake_redis),
        patch("app.bot.handlers.llm_request") as mock_task,
    ):
        mock_task.delay = MagicMock()
        from app.bot.handlers import handle_text

        message = _make_message("Расскажи про Толстого", user_id=111, chat_id=222)
        await handle_text(message)

    mock_task.delay.assert_called_once_with(222, "Расскажи про Толстого")
    message.answer.assert_called_once()
    assert "принят" in message.answer.call_args[0][0].lower()
