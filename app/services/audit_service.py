"""
Servicio de auditoría para registrar eventos del sistema.
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.utils.logger import logger


class EventType:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Clase con constantes para tipos de eventos de auditoría predefinidos
    Parámetros de entrada: None (clase con constantes)
    Retorno esperado: None (clase con constantes de tipo de evento)
    """
    DOCUMENT_UPLOAD = "Carga de documento"
    AI_ANALYSIS = "IA"
    USER_INTERACTION = "Interacción del usuario"
    LOGIN = "Interacción del usuario"  # Login es una interacción del usuario
    TOKEN_REFRESH = "Interacción del usuario"  # Refresh token también


def log_event(
    event_type: str,
    description: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Registra un evento de auditoría en la base de datos SQL Server
    Parámetros de entrada:
        - event_type: str - Tipo de evento (usar EventType.DOCUMENT_UPLOAD, EventType.AI_ANALYSIS, etc.)
        - description: str - Descripción detallada del evento
        - user_id: str | None - ID del usuario que generó el evento (opcional)
        - metadata: dict | None - Diccionario con información adicional del evento (opcional, se serializa a JSON)
    Retorno esperado: None (función que registra el evento en la BD)
    """
    db = SessionLocal()
    try:
        # Convertir metadata a JSON string si existe
        metadata_json = None
        if metadata:
            try:
                metadata_json = json.dumps(metadata, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.warning(f"Error serializando metadata para auditoría: {e}")
                metadata_json = str(metadata)
        
        audit_log = AuditLog(
            event_type=event_type,
            description=description,
            user_id=user_id,
            event_metadata=metadata_json
        )
        
        db.add(audit_log)
        db.commit()
        logger.info(f"Evento de auditoría registrado: {event_type} - {description}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar evento de auditoría: {e}")
        # No lanzamos la excepción para no interrumpir el flujo principal
    finally:
        db.close()


def get_audit_logs(
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Consulta eventos de auditoría desde la base de datos con filtros opcionales y paginación
    Parámetros de entrada:
        - event_type: str | None - Filtrar por tipo de evento (opcional)
        - user_id: str | None - Filtrar por ID de usuario (opcional)
        - start_date: datetime | None - Fecha de inicio para filtrar eventos (inclusive, opcional)
        - end_date: datetime | None - Fecha de fin para filtrar eventos (inclusive, opcional)
        - limit: int - Número máximo de registros a retornar (default: 100)
        - offset: int - Número de registros a saltar para paginación (default: 0)
    Retorno esperado: dict - {"total": int, "limit": int, "offset": int, "logs": list} donde logs es una lista de diccionarios con los eventos de auditoría (id, event_type, description, user_id, event_date, metadata)
    """
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        
        # Aplicar filtros
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.event_date >= start_date)
        if end_date:
            query = query.filter(AuditLog.event_date <= end_date)
        
        # Obtener total antes de aplicar limit/offset
        total = query.count()
        
        # Aplicar ordenamiento (más recientes primero) y paginación
        logs = query.order_by(AuditLog.event_date.desc()).offset(offset).limit(limit).all()
        
        # Convertir a diccionarios
        logs_data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "event_type": log.event_type,
                "description": log.description,
                "user_id": log.user_id,
                "event_date": log.event_date.isoformat() if log.event_date else None,
                "metadata": None
            }
            
            # Parsear event_metadata si existe
            if log.event_metadata:
                try:
                    log_dict["metadata"] = json.loads(log.event_metadata)
                except (json.JSONDecodeError, TypeError):
                    log_dict["metadata"] = log.event_metadata
            
            logs_data.append(log_dict)
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": logs_data
        }
        
    except Exception as e:
        logger.error(f"Error al consultar eventos de auditoría: {e}")
        raise
    finally:
        db.close()

