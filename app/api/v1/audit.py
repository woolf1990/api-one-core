from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import Optional
from app.core.security import verify_token, TokenError
from app.services.audit_service import get_audit_logs, EventType

router = APIRouter()
security = HTTPBearer()


def require_authenticated_user(token: str):
    """Verifica que el token sea válido y retorna el payload."""
    try:
        payload = verify_token(token)
        return payload
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@router.get("/logs")
def get_audit_logs_endpoint(
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    user_id: Optional[str] = Query(None, description="Filtrar por ID de usuario"),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Consulta eventos de auditoría con filtros opcionales.
    Requiere autenticación JWT.
    """
    # Verificar autenticación
    payload = require_authenticated_user(creds.credentials)
    
    # Parsear fechas si se proporcionan
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            # Intentar parsear con hora
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Intentar parsear solo fecha
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha inválido para start_date. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS"
                )
    
    if end_date:
        try:
            # Intentar parsear con hora
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Intentar parsear solo fecha
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # Ajustar a fin del día
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha inválido para end_date. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS"
                )
    
    # Validar tipos de evento
    valid_event_types = [
        EventType.DOCUMENT_UPLOAD,
        EventType.AI_ANALYSIS,
        EventType.USER_INTERACTION,
        EventType.LOGIN,
        EventType.TOKEN_REFRESH
    ]
    
    if event_type and event_type not in valid_event_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de evento inválido. Tipos válidos: {', '.join(set(valid_event_types))}"
        )
    
    try:
        result = get_audit_logs(
            event_type=event_type,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar auditoría: {str(e)}"
        )


@router.get("/event-types")
def get_event_types(creds: HTTPAuthorizationCredentials = Depends(security)):
    """
    Retorna la lista de tipos de eventos disponibles.
    Requiere autenticación JWT.
    """
    require_authenticated_user(creds.credentials)
    
    return {
        "event_types": [
            {"value": EventType.DOCUMENT_UPLOAD, "label": "Carga de documento"},
            {"value": EventType.AI_ANALYSIS, "label": "IA"},
            {"value": EventType.USER_INTERACTION, "label": "Interacción del usuario"},
        ],
        "note": "Los eventos de login y refresh token se registran como 'Interacción del usuario'"
    }

