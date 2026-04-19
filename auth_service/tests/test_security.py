"""Unit tests for security functions: password hashing and JWT."""

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_not_equal_to_plain():
    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert hashed != plain


def test_verify_correct_password():
    plain = "mysecretpassword"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("correctpassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    token = create_access_token(sub="42", role="user")
    payload = decode_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_invalid_token():
    try:
        decode_token("invalid.token.here")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
