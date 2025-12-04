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
    """Tipos de eventos predefinidos."""
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
    Registra un evento de auditoría en la base de datos.
    
    Args:
        event_type: Tipo de evento (usar EventType.*)
        description: Descripción del evento
        user_id: ID del usuario que generó el evento (opcional)
        metadata: Diccionario con información adicional (opcional)
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
    Consulta eventos de auditoría con filtros opcionales.
    
    Args:
        event_type: Filtrar por tipo de evento
        user_id: Filtrar por ID de usuario
        start_date: Fecha de inicio (inclusive)
        end_date: Fecha de fin (inclusive)
        limit: Número máximo de registros a retornar
        offset: Número de registros a saltar (para paginación)
    
    Returns:
        Dict con 'total' (total de registros) y 'logs' (lista de eventos)
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

