"""
Pruebas unitarias para el servicio de auditoría.
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.audit_service import log_event, get_audit_logs, EventType


class TestAuditService:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para el servicio de auditoría
    """
    
    def test_log_event_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que log_event registre correctamente un evento de auditoría
        Parámetros de entrada:
            - event_type: EventType.DOCUMENT_UPLOAD
            - description: "Carga de archivo test.csv"
            - user_id: "1"
            - metadata: {"filename": "test.csv", "file_id": 1}
        Retorno esperado: None (función no retorna valor, solo registra en BD)
        """
        with patch('app.services.audit_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.close = Mock()
            
            log_event(
                event_type=EventType.DOCUMENT_UPLOAD,
                description="Carga de archivo test.csv",
                user_id="1",
                metadata={"filename": "test.csv", "file_id": 1}
            )
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()
    
    def test_log_event_without_metadata(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que log_event funcione correctamente sin metadata
        Parámetros de entrada:
            - event_type: EventType.USER_INTERACTION
            - description: "Login exitoso"
            - user_id: "2"
            - metadata: None
        Retorno esperado: None (función registra evento sin metadata)
        """
        with patch('app.services.audit_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.close = Mock()
            
            log_event(
                event_type=EventType.USER_INTERACTION,
                description="Login exitoso",
                user_id="2",
                metadata=None
            )
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()
    
    def test_get_audit_logs_no_filters(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que get_audit_logs retorne todos los eventos sin filtros
        Parámetros de entrada:
            - event_type: None
            - user_id: None
            - start_date: None
            - end_date: None
            - limit: 100
            - offset: 0
        Retorno esperado: Dict con total, limit, offset, logs (array de eventos)
        """
        with patch('app.services.audit_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_log = MagicMock()
            mock_log.id = 1
            mock_log.event_type = EventType.DOCUMENT_UPLOAD
            mock_log.description = "Test event"
            mock_log.user_id = "1"
            mock_log.event_date = datetime.now()
            mock_log.event_metadata = '{"filename": "test.csv"}'
            
            # Configurar la cadena de métodos de query
            mock_query = MagicMock()
            mock_query.count.return_value = 1
            mock_order_by = MagicMock()
            mock_offset = MagicMock()
            mock_limit = MagicMock()
            mock_limit.all.return_value = [mock_log]
            mock_offset.limit.return_value = mock_limit
            mock_order_by.offset.return_value = mock_offset
            mock_query.order_by.return_value = mock_order_by
            mock_db.query.return_value = mock_query
            
            result = get_audit_logs()
            
            assert result["total"] == 1
            assert result["limit"] == 100
            assert result["offset"] == 0
            assert len(result["logs"]) == 1
            assert result["logs"][0]["id"] == 1
    
    def test_get_audit_logs_with_filters(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que get_audit_logs aplique correctamente los filtros
        Parámetros de entrada:
            - event_type: EventType.DOCUMENT_UPLOAD
            - user_id: "1"
            - start_date: datetime(2024, 1, 1)
            - end_date: datetime(2024, 12, 31)
            - limit: 50
            - offset: 0
        Retorno esperado: Dict con logs filtrados según los parámetros
        """
        with patch('app.services.audit_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_log = MagicMock()
            mock_log.id = 1
            mock_log.event_type = EventType.DOCUMENT_UPLOAD
            mock_log.description = "Test event"
            mock_log.user_id = "1"
            mock_log.event_date = datetime(2024, 6, 15)
            mock_log.event_metadata = None
            
            # Configurar la cadena de métodos de query con filtros
            mock_query = MagicMock()
            mock_filtered_query = MagicMock()
            mock_query.filter.return_value = mock_filtered_query
            mock_filtered_query.filter.return_value = mock_filtered_query  # Para múltiples filtros
            mock_filtered_query.count.return_value = 1
            
            mock_order_by = MagicMock()
            mock_offset = MagicMock()
            mock_limit = MagicMock()
            mock_limit.all.return_value = [mock_log]
            mock_offset.limit.return_value = mock_limit
            mock_order_by.offset.return_value = mock_offset
            mock_filtered_query.order_by.return_value = mock_order_by
            
            mock_db.query.return_value = mock_query
            
            result = get_audit_logs(
                event_type=EventType.DOCUMENT_UPLOAD,
                user_id="1",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                limit=50,
                offset=0
            )
            
            assert result["total"] == 1
            assert result["limit"] == 50
            assert len(result["logs"]) == 1
    
    def test_get_audit_logs_with_metadata_parsing(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que get_audit_logs parsee correctamente el metadata JSON
        Parámetros de entrada:
            - event_type: None
            - user_id: None
            - start_date: None
            - end_date: None
            - limit: 100
            - offset: 0
        Retorno esperado: Dict con logs donde metadata es un objeto parseado desde JSON
        """
        with patch('app.services.audit_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_log = MagicMock()
            mock_log.id = 1
            mock_log.event_type = EventType.AI_ANALYSIS
            mock_log.description = "Análisis completado"
            mock_log.user_id = "1"
            mock_log.event_date = datetime.now()
            mock_log.event_metadata = '{"document_id": 1, "classification": "FACTURA"}'
            
            # Configurar la cadena de métodos de query
            mock_query = MagicMock()
            mock_query.count.return_value = 1
            mock_order_by = MagicMock()
            mock_offset = MagicMock()
            mock_limit = MagicMock()
            mock_limit.all.return_value = [mock_log]
            mock_offset.limit.return_value = mock_limit
            mock_order_by.offset.return_value = mock_offset
            mock_query.order_by.return_value = mock_order_by
            mock_db.query.return_value = mock_query
            
            result = get_audit_logs()
            
            assert len(result["logs"]) > 0, "Debe haber al menos un log"
            assert result["logs"][0]["metadata"] is not None
            assert isinstance(result["logs"][0]["metadata"], dict)
            assert result["logs"][0]["metadata"]["document_id"] == 1

