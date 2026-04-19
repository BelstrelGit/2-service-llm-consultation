from jose import JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG]
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e

    if "sub" not in payload:
        raise ValueError("Token missing 'sub' claim")

    return payload
