"""
Pruebas unitarias para el servicio de análisis de documentos.
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.services.document_service import analyze_and_store_document
from app.services.ai_client import AIServiceError


class TestDocumentService:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para el servicio de análisis de documentos
    """
    
    @pytest.mark.asyncio
    async def test_analyze_and_store_document_success_factura(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que analyze_and_store_document procese correctamente una factura
        Parámetros de entrada:
            - upload_file: Mock de UploadFile con contenido PDF
            - uploaded_by: "1"
        Retorno esperado: Dict con document_id, analysis_id, ai_status="analyzed", analysis con datos de factura
        """
        mock_file = Mock()
        mock_file.filename = "factura.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"fake pdf content")
        
        mock_analysis = {
            "classification": "FACTURA",
            "client_name": "Cliente ABC",
            "provider_name": "Proveedor XYZ",
            "invoice_number": "FAC-001",
            "total_amount": 1000.0,
            "products": [],
            "description": None,
            "summary": None,
            "sentiment": None
        }
        
        with patch('app.services.document_service.upload_bytes_to_s3', return_value="s3://bucket/factura.pdf"):
            with patch('app.services.document_service.analyze_document', return_value=mock_analysis):
                with patch('app.services.document_service.SessionLocal') as mock_session_class:
                    mock_db = MagicMock()
                    mock_session_class.return_value = mock_db
                    
                    # Simular que db.add() asigna IDs a los objetos después de agregarlos
                    doc_obj = None
                    analysis_obj = None
                    
                    def add_side_effect(obj):
                        nonlocal doc_obj, analysis_obj
                        # Detectar si es Document o DocumentAnalysis por el nombre de la clase
                        class_name = obj.__class__.__name__
                        if class_name == 'Document':
                            obj.id = 1
                            obj.storage_path = "s3://bucket/factura.pdf"
                            obj.ai_status = "analyzed"
                            obj.ai_error = None
                            doc_obj = obj
                        elif class_name == 'DocumentAnalysis':
                            obj.id = 5
                            analysis_obj = obj
                    
                    mock_db.add.side_effect = add_side_effect
                    mock_db.commit = Mock()
                    
                    def refresh_side_effect(obj):
                        # Simular refresh - no hace nada porque el ID ya está asignado
                        pass
                    
                    mock_db.refresh = Mock(side_effect=refresh_side_effect)
                    
                    def flush_side_effect():
                        # Simular flush - asegurar que analysis_obj tiene ID
                        if analysis_obj:
                            analysis_obj.id = 5
                    
                    mock_db.flush = Mock(side_effect=flush_side_effect)
                    mock_db.close = Mock()
                    
                    result = await analyze_and_store_document(mock_file, "1")
                    
                    assert result["document_id"] is not None
                    assert result["analysis_id"] is not None
                    assert result["ai_status"] == "analyzed"
                    assert result["analysis"] == mock_analysis
    
    @pytest.mark.asyncio
    async def test_analyze_and_store_document_success_informacion(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que analyze_and_store_document procese correctamente un documento informativo
        Parámetros de entrada:
            - upload_file: Mock de UploadFile con contenido PNG
            - uploaded_by: "1"
        Retorno esperado: Dict con document_id, analysis_id, ai_status="analyzed", analysis con description, summary, sentiment
        """
        mock_file = Mock()
        mock_file.filename = "informacion.png"
        mock_file.content_type = "image/png"
        mock_file.read = AsyncMock(return_value=b"fake image content")
        
        mock_analysis = {
            "classification": "INFORMACION",
            "description": "Descripción del contenido",
            "summary": "Resumen breve",
            "sentiment": "positivo",
            "client_name": None,
            "provider_name": None,
            "invoice_number": None,
            "total_amount": None,
            "products": []
        }
        
        with patch('app.services.document_service.upload_bytes_to_s3', return_value="s3://bucket/informacion.png"):
            with patch('app.services.document_service.analyze_document', return_value=mock_analysis):
                with patch('app.services.document_service.SessionLocal') as mock_session_class:
                    mock_db = MagicMock()
                    mock_session_class.return_value = mock_db
                    
                    # Simular que db.add() asigna IDs a los objetos después de agregarlos
                    doc_obj = None
                    analysis_obj = None
                    
                    def add_side_effect(obj):
                        nonlocal doc_obj, analysis_obj
                        class_name = obj.__class__.__name__
                        if class_name == 'Document':
                            obj.id = 2
                            obj.storage_path = "s3://bucket/informacion.png"
                            obj.ai_status = "analyzed"
                            obj.ai_error = None
                            doc_obj = obj
                        elif class_name == 'DocumentAnalysis':
                            obj.id = 6
                            analysis_obj = obj
                    
                    mock_db.add.side_effect = add_side_effect
                    mock_db.commit = Mock()
                    
                    def refresh_side_effect(obj):
                        pass
                    
                    mock_db.refresh = Mock(side_effect=refresh_side_effect)
                    
                    def flush_side_effect():
                        if analysis_obj:
                            analysis_obj.id = 6
                    
                    mock_db.flush = Mock(side_effect=flush_side_effect)
                    mock_db.close = Mock()
                    
                    result = await analyze_and_store_document(mock_file, "1")
                    
                    assert result["document_id"] is not None
                    assert result["analysis_id"] is not None
                    assert result["ai_status"] == "analyzed"
                    assert result["analysis"]["classification"] == "INFORMACION"
                    assert result["analysis"]["description"] is not None
                    assert result["analysis"]["summary"] is not None
                    assert result["analysis"]["sentiment"] is not None
    
    @pytest.mark.asyncio
    async def test_analyze_and_store_document_ai_failed(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que analyze_and_store_document maneje correctamente cuando la IA falla
        Parámetros de entrada:
            - upload_file: Mock de UploadFile
            - uploaded_by: "1"
        Retorno esperado: Dict con document_id, analysis_id=None, ai_status="ai_failed", ai_error con mensaje, analysis=None
        """
        mock_file = Mock()
        mock_file.filename = "documento.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"fake content")
        
        with patch('app.services.document_service.upload_bytes_to_s3', return_value="s3://bucket/documento.pdf"):
            with patch('app.services.document_service.analyze_document', side_effect=AIServiceError("IA no disponible")):
                with patch('app.services.document_service.SessionLocal') as mock_session_class:
                    mock_db = MagicMock()
                    mock_session_class.return_value = mock_db
                    
                    # Simular que db.add() asigna IDs a los objetos después de agregarlos
                    doc_obj = None
                    
                    def add_side_effect(obj):
                        nonlocal doc_obj
                        class_name = obj.__class__.__name__
                        if class_name == 'Document':
                            obj.id = 3
                            obj.storage_path = "s3://bucket/documento.pdf"
                            obj.ai_status = "ai_failed"
                            obj.ai_error = "IA no disponible"
                            doc_obj = obj
                    
                    mock_db.add.side_effect = add_side_effect
                    mock_db.commit = Mock()
                    
                    def refresh_side_effect(obj):
                        pass
                    
                    mock_db.refresh = Mock(side_effect=refresh_side_effect)
                    mock_db.close = Mock()
                    
                    result = await analyze_and_store_document(mock_file, "1")
                    
                    assert result["document_id"] is not None
                    assert result["analysis_id"] is None
                    assert result["ai_status"] == "ai_failed"
                    assert result["ai_error"] is not None
                    assert result["analysis"] is None

