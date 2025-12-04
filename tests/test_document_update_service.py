"""
Pruebas unitarias para el servicio de actualización de análisis de documentos.
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.document_update_service import update_document_analysis, get_document_analysis


class TestDocumentUpdateService:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para el servicio de actualización de análisis
    """
    
    def test_update_document_analysis_partial_update(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que update_document_analysis actualice solo los campos proporcionados
        Parámetros de entrada:
            - analysis_id: 1
            - client_name: "Nuevo Cliente"
            - total_amount: 2000.0
        Retorno esperado: Dict con el análisis actualizado, incluyendo los campos modificados
        """
        with patch('app.services.document_update_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            # Crear un objeto mock con atributos mutables
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.document_id = 1
            mock_analysis.classification = "FACTURA"
            mock_analysis.client_name = "Cliente Original"
            mock_analysis.total_amount = 1000.0
            mock_analysis.products_json = "[]"
            mock_analysis.client_address = None
            mock_analysis.provider_name = None
            mock_analysis.provider_address = None
            mock_analysis.invoice_number = None
            mock_analysis.invoice_date = None
            mock_analysis.description = None
            mock_analysis.summary = None
            mock_analysis.sentiment = None
            
            # Configurar la cadena de query
            mock_query = MagicMock()
            mock_filter = MagicMock()
            mock_filter.first.return_value = mock_analysis
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            
            mock_db.commit = Mock()
            
            def refresh_side_effect(obj):
                # Simular refresh - no hace nada porque los valores ya están actualizados
                pass
            
            mock_db.refresh = Mock(side_effect=refresh_side_effect)
            mock_db.close = Mock()
            
            result = update_document_analysis(
                analysis_id=1,
                client_name="Nuevo Cliente",
                total_amount=2000.0
            )
            
            assert result["id"] == 1
            assert result["client_name"] == "Nuevo Cliente"
            assert result["total_amount"] == 2000.0
    
    def test_update_document_analysis_not_found(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que update_document_analysis lance ValueError cuando el análisis no existe
        Parámetros de entrada:
            - analysis_id: 999 (inexistente)
            - client_name: "Test"
        Retorno esperado: ValueError con mensaje indicando que el análisis no fue encontrado
        """
        with patch('app.services.document_update_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            # Configurar la cadena de query para retornar None
            mock_query = MagicMock()
            mock_filter = MagicMock()
            mock_filter.first.return_value = None
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            mock_db.close = Mock()
            
            with pytest.raises(ValueError) as exc_info:
                update_document_analysis(analysis_id=999, client_name="Test")
            
            assert "no encontrado" in str(exc_info.value).lower()
    
    def test_update_document_analysis_products(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que update_document_analysis actualice correctamente la lista de productos
        Parámetros de entrada:
            - analysis_id: 1
            - products: [{"name": "Producto A", "quantity": 2, "unit_price": 100.0, "total": 200.0}]
        Retorno esperado: Dict con products actualizado como array parseado desde JSON
        """
        with patch('app.services.document_update_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.document_id = 1
            mock_analysis.classification = "FACTURA"
            mock_analysis.products_json = "[]"
            mock_analysis.client_name = None
            mock_analysis.client_address = None
            mock_analysis.provider_name = None
            mock_analysis.provider_address = None
            mock_analysis.invoice_number = None
            mock_analysis.invoice_date = None
            mock_analysis.total_amount = None
            mock_analysis.description = None
            mock_analysis.summary = None
            mock_analysis.sentiment = None
            
            # Configurar la cadena de query
            mock_query = MagicMock()
            mock_filter = MagicMock()
            mock_filter.first.return_value = mock_analysis
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            
            mock_db.commit = Mock()
            
            def refresh_side_effect(obj):
                pass
            
            mock_db.refresh = Mock(side_effect=refresh_side_effect)
            mock_db.close = Mock()
            
            products = [{"name": "Producto A", "quantity": 2, "unit_price": 100.0, "total": 200.0}]
            result = update_document_analysis(analysis_id=1, products=products)
            
            assert result["products"] == products
    
    def test_get_document_analysis_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que get_document_analysis retorne correctamente un análisis existente
        Parámetros de entrada:
            - analysis_id: 1
        Retorno esperado: Dict con todos los campos del análisis, incluyendo products parseado desde JSON
        """
        with patch('app.services.document_update_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            mock_analysis = Mock()
            mock_analysis.id = 1
            mock_analysis.document_id = 1
            mock_analysis.classification = "FACTURA"
            mock_analysis.client_name = "Cliente Test"
            mock_analysis.client_address = None
            mock_analysis.provider_name = None
            mock_analysis.provider_address = None
            mock_analysis.invoice_number = None
            mock_analysis.invoice_date = None
            mock_analysis.total_amount = 1000.0
            mock_analysis.products_json = '[{"name": "Producto A", "quantity": 1, "unit_price": 1000.0, "total": 1000.0}]'
            mock_analysis.description = None
            mock_analysis.summary = None
            mock_analysis.sentiment = None
            
            # Configurar la cadena de query
            mock_query = MagicMock()
            mock_filter = MagicMock()
            mock_filter.first.return_value = mock_analysis
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            mock_db.close = Mock()
            
            result = get_document_analysis(analysis_id=1)
            
            assert result is not None
            assert result["id"] == 1
            assert result["classification"] == "FACTURA"
            assert isinstance(result["products"], list)
            assert len(result["products"]) == 1
    
    def test_get_document_analysis_not_found(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que get_document_analysis retorne None cuando el análisis no existe
        Parámetros de entrada:
            - analysis_id: 999 (inexistente)
        Retorno esperado: None
        """
        with patch('app.services.document_update_service.SessionLocal') as mock_session_class:
            mock_db = MagicMock()
            mock_session_class.return_value = mock_db
            
            # Configurar la cadena de query para retornar None
            mock_query = MagicMock()
            mock_filter = MagicMock()
            mock_filter.first.return_value = None
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            mock_db.close = Mock()
            
            result = get_document_analysis(analysis_id=999)
            
            assert result is None

