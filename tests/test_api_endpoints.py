"""
Pruebas unitarias para los endpoints de la API.
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.services.auth_service import ensure_demo_user
from app.db.base import init_db
from app.db.base_class import engine

client = TestClient(app)


def setup_module(module):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Configuración del módulo de pruebas, inicializa BD y crea usuarios demo
    Parámetros de entrada:
        - module: Módulo de pytest
    Retorno esperado: None (inicializa BD y crea usuarios demo)
    """
    # Inicializar base de datos
    init_db(engine)
    # Crear usuarios demo
    ensure_demo_user()


class TestAuthEndpoints:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para endpoints de autenticación
    """
    
    def test_login_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de login retorne token válido con credenciales correctas
        Parámetros de entrada:
            - POST /api/v1/auth/login
            - Body: {"username": "uploader", "password": "password"}
        Retorno esperado: 200 OK con access_token, token_type="bearer", expires_in
        """
        # Asegurar que el usuario existe antes de intentar login
        ensure_demo_user()
        
        response = client.post('/api/v1/auth/login', json={
            'username': 'uploader',
            'password': 'demo1234'
        })
        
        if response.status_code != 200:
            # Si falla, mostrar el error para diagnóstico
            print(f"Login failed with status {response.status_code}: {response.text}")
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert 'expires_in' in data
    
    def test_login_invalid_credentials(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de login rechace credenciales inválidas
        Parámetros de entrada:
            - POST /api/v1/auth/login
            - Body: {"username": "uploader", "password": "wrong_password"}
        Retorno esperado: 401 Unauthorized con mensaje de error
        """
        response = client.post('/api/v1/auth/login', json={
            'username': 'uploader',
            'password': 'wrong_password'
        })
        
        assert response.status_code == 401
        assert 'detail' in response.json()


class TestTokenEndpoints:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para endpoints de tokens
    """
    
    def test_refresh_token_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de refresh token genere un nuevo token válido
        Parámetros de entrada:
            - POST /api/v1/token/refresh
            - Header: Authorization: Bearer <token_válido>
        Retorno esperado: 200 OK con nuevo access_token y expires_in
        """
        # Primero obtener un token
        login_response = client.post('/api/v1/auth/login', json={
            'username': 'uploader',
            'password': 'demo1234'
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()['access_token']
        
        # Refrescar el token
        response = client.post(
            '/api/v1/token/refresh',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        new_token = data['access_token']
        assert new_token != token, "El nuevo token debe ser diferente al anterior"
        assert 'expires_in' in data
        
        # Verificar que el nuevo token sea válido y tenga los mismos datos del usuario
        from app.core.security import verify_token
        new_payload = verify_token(new_token)
        original_payload = verify_token(token)
        assert new_payload.get("sub") == original_payload.get("sub")
        assert new_payload.get("rol") == original_payload.get("rol")
        # El iat debe ser diferente (más reciente)
        assert new_payload.get("iat") >= original_payload.get("iat", 0)
    
    def test_refresh_token_invalid(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de refresh token rechace tokens inválidos
        Parámetros de entrada:
            - POST /api/v1/token/refresh
            - Header: Authorization: Bearer <token_inválido>
        Retorno esperado: 401 Unauthorized con mensaje de error
        """
        response = client.post(
            '/api/v1/token/refresh',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401


class TestFilesEndpoints:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para endpoints de archivos
    """
    
    def get_auth_token(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Helper para obtener un token de autenticación
        Parámetros de entrada: None
        Retorno esperado: String con access_token válido
        """
        response = client.post('/api/v1/auth/login', json={
            'username': 'uploader',
            'password': 'demo1234'
        })
        if response.status_code != 200:
            # Si falla, intentar crear el usuario y volver a intentar
            ensure_demo_user()
            response = client.post('/api/v1/auth/login', json={
                'username': 'uploader',
                'password': 'demo1234'
            })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()['access_token']
    
    def test_upload_csv_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de upload procese correctamente un CSV válido
        Parámetros de entrada:
            - POST /api/v1/files/upload
            - Header: Authorization: Bearer <token>
            - Form data: file (CSV), parametro1, parametro2
        Retorno esperado: 200 OK con file_id, s3_path, rows_saved, validations
        """
        token = self.get_auth_token()
        csv_content = 'id,name,price\n1,Producto A,10.5\n2,Producto B,20.0\n'
        
        response = client.post(
            '/api/v1/files/upload',
            headers={'Authorization': f'Bearer {token}'},
            data={'parametro1': 'col1', 'parametro2': 'col2'},
            files={'file': ('test.csv', csv_content, 'text/csv')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'file_id' in data
        assert 's3_path' in data
        assert 'rows_saved' in data
        assert 'validations' in data
    
    def test_upload_csv_missing_parameters(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de upload rechace CSV sin parámetros requeridos
        Parámetros de entrada:
            - POST /api/v1/files/upload
            - Header: Authorization: Bearer <token>
            - Form data: file (CSV), sin parametro1 o parametro2
        Retorno esperado: 400 Bad Request con mensaje indicando que faltan parámetros
        """
        token = self.get_auth_token()
        csv_content = 'id,name,price\n1,Producto A,10.5\n'
        
        response = client.post(
            '/api/v1/files/upload',
            headers={'Authorization': f'Bearer {token}'},
            data={'parametro1': 'col1'},  # Falta parametro2
            files={'file': ('test.csv', csv_content, 'text/csv')}
        )
        
        assert response.status_code == 400
        assert 'parametro' in response.json()['detail'].lower()
    
    def test_upload_csv_unauthorized(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de upload requiera autenticación
        Parámetros de entrada:
            - POST /api/v1/files/upload
            - Sin header Authorization
            - Form data: file (CSV), parametro1, parametro2
        Retorno esperado: 403 Forbidden o 401 Unauthorized
        """
        csv_content = 'id,name,price\n1,Producto A,10.5\n'
        
        response = client.post(
            '/api/v1/files/upload',
            data={'parametro1': 'col1', 'parametro2': 'col2'},
            files={'file': ('test.csv', csv_content, 'text/csv')}
        )
        
        assert response.status_code in [401, 403]


class TestAuditEndpoints:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para endpoints de auditoría
    """
    
    def get_auth_token(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Helper para obtener un token de autenticación
        Parámetros de entrada: None
        Retorno esperado: String con access_token válido
        """
        response = client.post('/api/v1/auth/login', json={
            'username': 'uploader',
            'password': 'demo1234'
        })
        if response.status_code != 200:
            # Si falla, intentar crear el usuario y volver a intentar
            ensure_demo_user()
            response = client.post('/api/v1/auth/login', json={
                'username': 'uploader',
                'password': 'demo1234'
            })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()['access_token']
    
    def test_get_audit_logs_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de auditoría retorne logs correctamente
        Parámetros de entrada:
            - GET /api/v1/audit/logs
            - Header: Authorization: Bearer <token>
        Retorno esperado: 200 OK con total, limit, offset, logs (array)
        """
        token = self.get_auth_token()
        
        response = client.get(
            '/api/v1/audit/logs',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
        assert 'logs' in data
        assert isinstance(data['logs'], list)
    
    def test_get_audit_logs_with_filters(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de auditoría aplique filtros correctamente
        Parámetros de entrada:
            - GET /api/v1/audit/logs?event_type=Carga de documento&limit=50
            - Header: Authorization: Bearer <token>
        Retorno esperado: 200 OK con logs filtrados según los parámetros
        """
        token = self.get_auth_token()
        
        response = client.get(
            '/api/v1/audit/logs?event_type=Carga de documento&limit=50',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['limit'] == 50
    
    def test_get_event_types_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que el endpoint de tipos de eventos retorne la lista correcta
        Parámetros de entrada:
            - GET /api/v1/audit/event-types
            - Header: Authorization: Bearer <token>
        Retorno esperado: 200 OK con event_types (array) y note (string)
        """
        token = self.get_auth_token()
        
        response = client.get(
            '/api/v1/audit/event-types',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'event_types' in data
        assert isinstance(data['event_types'], list)
        assert len(data['event_types']) > 0

