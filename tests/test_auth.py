"""
Pruebas unitarias para endpoints de autenticación (versión actualizada).
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import ensure_demo_user

client = TestClient(app)

def setup_module(module):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Configuración del módulo de pruebas, asegura que existan usuarios demo
    Parámetros de entrada:
        - module: Módulo de pytest
    Retorno esperado: None (crea usuarios demo si no existen)
    """
    ensure_demo_user()

def test_login_success():
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Verifica que el login sea exitoso con credenciales válidas
    Parámetros de entrada:
        - POST /api/v1/auth/login
        - Body: {"username": "uploader", "password": "demo1234"}
    Retorno esperado: 200 OK con access_token en la respuesta
    """
    resp = client.post('/api/v1/auth/login', json={'username':'uploader','password':'demo1234'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data
