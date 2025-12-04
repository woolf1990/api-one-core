from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import secrets
from app.core.config import settings

class TokenError(Exception):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Excepción personalizada para errores relacionados con tokens JWT
    Parámetros de entrada: None (clase de excepción)
    Retorno esperado: None (clase de excepción)
    """
    pass

def create_access_token(data: dict, expires_minutes: int | None = None):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Crea un token JWT de acceso con los datos proporcionados y tiempo de expiración
    Parámetros de entrada:
        - data: dict con los datos a incluir en el token (ej: {"sub": "user_id", "rol": "role"})
        - expires_minutes: int | None - Minutos hasta la expiración (None usa el valor por defecto de configuración)
    Retorno esperado: str - Token JWT codificado como string
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + timedelta(minutes=expires_minutes)
    # Agregar campos estándar JWT para garantizar unicidad
    to_encode.update({
        "iat": int(now.timestamp()),  # Timestamp de emisión
        "exp": int(expire.timestamp()),  # Timestamp de expiración
        "jti": secrets.token_urlsafe(16)  # JWT ID único para cada token
    })
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def create_jwt(data: dict, minutes: int | None = None):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Alias para create_access_token, crea un token JWT
    Parámetros de entrada:
        - data: dict con los datos a incluir en el token
        - minutes: int | None - Minutos hasta la expiración (None usa el valor por defecto)
    Retorno esperado: str - Token JWT codificado como string
    """
    return create_access_token(data, minutes)

def verify_token(token: str):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Verifica y decodifica un token JWT, retornando su payload
    Parámetros de entrada:
        - token: str - Token JWT a verificar
    Retorno esperado: dict - Payload del token decodificado con los datos (sub, rol, iat, exp, jti)
    Excepciones: TokenError si el token está expirado o es inválido
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise TokenError("Token expired")
    except JWTError as e:
        raise TokenError("Invalid token: " + str(e))
