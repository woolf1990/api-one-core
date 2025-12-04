from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import Optional
from app.core.security import verify_token, TokenError
from app.services.audit_service import get_audit_logs, EventType

router = APIRouter()
security = HTTPBearer()


def require_authenticated_user(token: str):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Función helper para verificar que un token JWT sea válido y retornar su payload
    Parámetros de entrada:
        - token: str - Token JWT a verificar
    Retorno esperado: dict - Payload del token decodificado con los datos del usuario (sub, rol, iat, exp, jti)
    Excepciones: HTTPException 401 si el token es inválido o expirado
    """
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
    Generado por IA - Fecha: 2024-12-19
    Descripción: Endpoint para consultar eventos de auditoría con filtros opcionales y paginación. Requiere autenticación JWT. Valida tipos de evento y parsea fechas en formato ISO o YYYY-MM-DD
    Parámetros de entrada:
        - event_type: str | None - Filtrar por tipo de evento (query parameter, opcional)
        - user_id: str | None - Filtrar por ID de usuario (query parameter, opcional)
        - start_date: str | None - Fecha de inicio en formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS (query parameter, opcional)
        - end_date: str | None - Fecha de fin en formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS (query parameter, opcional)
        - limit: int - Número máximo de registros a retornar (query parameter, default: 100, rango: 1-1000)
        - offset: int - Número de registros a saltar para paginación (query parameter, default: 0, mínimo: 0)
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - {"total": int, "limit": int, "offset": int, "logs": list} donde logs es una lista de eventos de auditoría con id, event_type, description, user_id, event_date, metadata
    Excepciones: HTTPException 400 si el formato de fecha es inválido o el tipo de evento no es válido, HTTPException 401 si no está autenticado, HTTPException 500 si ocurre un error al consultar
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
    Generado por IA - Fecha: 2024-12-19
    Descripción: Retorna la lista de tipos de eventos de auditoría disponibles. Requiere autenticación JWT
    Parámetros de entrada:
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - {"event_types": list, "note": str} donde event_types es una lista de objetos con "value" y "label" para cada tipo de evento disponible
    Excepciones: HTTPException 401 si no está autenticado
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

