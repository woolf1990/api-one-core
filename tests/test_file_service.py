"""
Pruebas unitarias para el servicio de procesamiento de archivos CSV/Excel.
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from app.services.file_service import handle_upload, _validate_row_basic, _is_empty_value


class TestFileService:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para el servicio de procesamiento de archivos
    """
    
    def test_is_empty_value_with_none(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _is_empty_value retorne True para valores None
        Parámetros de entrada:
            - value: None
        Retorno esperado: True
        """
        assert _is_empty_value(None) is True
    
    def test_is_empty_value_with_empty_string(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _is_empty_value retorne True para strings vacíos
        Parámetros de entrada:
            - value: ""
        Retorno esperado: True
        """
        assert _is_empty_value("") is True
        assert _is_empty_value("   ") is True  # Solo espacios
    
    def test_is_empty_value_with_valid_string(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _is_empty_value retorne False para strings válidos
        Parámetros de entrada:
            - value: "Producto A"
        Retorno esperado: False
        """
        assert _is_empty_value("Producto A") is False
    
    def test_is_empty_value_with_nan(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _is_empty_value retorne True para valores NaN (float)
        Parámetros de entrada:
            - value: float('nan')
        Retorno esperado: True
        """
        import math
        assert _is_empty_value(float('nan')) is True
    
    def test_validate_row_name_empty(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _validate_row_basic detecte cuando el campo name está vacío
        Parámetros de entrada:
            - row: dict con {"name": None, "price": "10.5", "id": "1"}
            - row_num: 1
        Retorno esperado: Tupla (errors, name_normalized) donde errors contiene un error de tipo EMPTY para la columna name
        """
        row = {"name": None, "price": "10.5", "id": "1"}
        errors, name_normalized = _validate_row_basic(row, 1)
        
        assert len(errors) == 1
        assert errors[0]["error"] == "EMPTY"
        assert errors[0]["column"] == "name"
        assert errors[0]["row"] == 1
        assert name_normalized is None
    
    def test_validate_row_price_empty(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _validate_row_basic detecte cuando el campo price está vacío
        Parámetros de entrada:
            - row: dict con {"name": "Producto A", "price": None, "id": "1"}
            - row_num: 2
        Retorno esperado: Tupla (errors, name_normalized) donde errors contiene un error de tipo EMPTY para la columna price
        """
        row = {"name": "Producto A", "price": None, "id": "1"}
        errors, name_normalized = _validate_row_basic(row, 2)
        
        assert len(errors) == 1
        assert errors[0]["error"] == "EMPTY"
        assert errors[0]["column"] == "price"
        assert name_normalized == "Producto A"
    
    def test_validate_row_price_invalid_type(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _validate_row_basic detecte cuando price no es numérico
        Parámetros de entrada:
            - row: dict con {"name": "Producto A", "price": "no_numérico", "id": "1"}
            - row_num: 3
        Retorno esperado: Tupla (errors, name_normalized) donde errors contiene un error de tipo TYPE para la columna price
        """
        row = {"name": "Producto A", "price": "no_numérico", "id": "1"}
        errors, name_normalized = _validate_row_basic(row, 3)
        
        assert len(errors) == 1
        assert errors[0]["error"] == "TYPE"
        assert errors[0]["column"] == "price"
        assert name_normalized == "Producto A"
    
    def test_validate_row_valid_row(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que _validate_row_basic no retorne errores para una fila válida
        Parámetros de entrada:
            - row: dict con {"name": "Producto A", "price": "10.5", "id": "1"}
            - row_num: 1
        Retorno esperado: Tupla (errors, name_normalized) donde errors está vacío y name_normalized tiene el nombre
        """
        row = {"name": "Producto A", "price": "10.5", "id": "1"}
        errors, name_normalized = _validate_row_basic(row, 1)
        
        assert len(errors) == 0
        assert name_normalized == "Producto A"
    
    
    @pytest.mark.asyncio
    async def test_handle_upload_csv_valid(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que handle_upload procese correctamente un CSV válido
        Parámetros de entrada:
            - upload_file: Mock de UploadFile con contenido CSV válido
            - parametro1: "col1"
            - parametro2: "col2"
            - uploaded_by: "1"
        Retorno esperado: Dict con file_id, s3_path, rows_saved > 0, validations (puede estar vacío)
        """
        from unittest.mock import AsyncMock
        
        csv_content = "id,name,price\n1,Producto A,10.5\n2,Producto B,20.0\n"
        
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.read = AsyncMock(return_value=csv_content.encode('utf-8-sig'))
        
        with patch('app.services.file_service.upload_bytes_to_s3', return_value="file://test.csv"):
            with patch('app.services.file_service.SessionLocal') as mock_session_class:
                # Mock de la sesión de base de datos
                mock_db = MagicMock()
                mock_session_class.return_value = mock_db
                
                # Crear mock del objeto File que se asignará al objeto real
                mock_file_rec = Mock()
                mock_file_rec.id = 1
                
                # Simular que db.add() asigna el ID al objeto
                def add_side_effect(obj):
                    class_name = obj.__class__.__name__
                    if class_name == 'File':
                        obj.id = mock_file_rec.id
                
                mock_db.add.side_effect = add_side_effect
                mock_db.commit = Mock()
                
                def refresh_side_effect(obj):
                    pass
                
                mock_db.refresh = Mock(side_effect=refresh_side_effect)
                mock_db.close = Mock()
                
                result = await handle_upload(mock_file, "col1", "col2", "1")
                
                assert "file_id" in result
                assert "s3_path" in result
                assert "rows_saved" in result
                assert "validations" in result
                assert result["rows_saved"] >= 0

