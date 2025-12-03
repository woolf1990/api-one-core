from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings

class TokenError(Exception):
    pass

def create_access_token(data: dict, expires_minutes: int | None = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": int(expire.timestamp())})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def create_jwt(data: dict, minutes: int | None = None):
    return create_access_token(data, minutes)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise TokenError("Token expired")
    except JWTError as e:
        raise TokenError("Invalid token: " + str(e))
