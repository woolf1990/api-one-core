from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import create_access_token, verify_token, TokenError
from app.services.audit_service import log_event, EventType

router = APIRouter()
security = HTTPBearer()

@router.post("/refresh")
def refresh(creds: HTTPAuthorizationCredentials = Depends(security)):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Endpoint para refrescar un token JWT. Verifica el token actual y genera uno nuevo con el mismo usuario y rol. Registra eventos de auditoría para refresh exitoso y fallido
    Parámetros de entrada:
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con el token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - {"access_token": str, "expires_in": int} con el nuevo token JWT y tiempo de expiración en segundos
    Excepciones: HTTPException 401 si el token es inválido o está expirado
    """
    token = creds.credentials
    try:
        payload = verify_token(token)
    except TokenError as e:
        # Registrar intento de refresh fallido
        log_event(
            event_type=EventType.TOKEN_REFRESH,
            description=f"Intento de refresh token fallido: {str(e)}",
            user_id=None,
            metadata={"success": False, "error": str(e)}
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    # token is valid and not expired -> issue new one
    user_id = payload.get("sub")
    new = create_access_token({"sub": user_id, "rol": payload.get("rol")})
    
    # Registrar refresh exitoso
    log_event(
        event_type=EventType.TOKEN_REFRESH,
        description="Refresh token exitoso",
        user_id=user_id,
        metadata={"success": True}
    )
    
    return {"access_token": new, "expires_in": 15*60}
