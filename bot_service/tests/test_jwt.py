"""Unit tests for JWT validation in Bot Service."""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def _make_token(sub: str = "1", role: str = "user", exp_minutes: int = 60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def test_valid_token():
    token = _make_token(sub="42", role="admin")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_invalid_token():
    try:
        decode_and_validate("garbage.token.string")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_expired_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    try:
        decode_and_validate(token)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_token_missing_sub():
    now = datetime.now(timezone.utc)
    payload = {
        "role": "user",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    try:
        decode_and_validate(token)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "sub" in str(e)
