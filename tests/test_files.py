"""
Pruebas unitarias para endpoints de archivos (versión actualizada).
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import ensure_demo_user
from app.db.base import init_db
from app.db.base_class import engine
import io

client = TestClient(app)

def setup_module(module):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Configuración del módulo de pruebas, asegura que existan usuarios demo
    Parámetros de entrada:
        - module: Módulo de pytest
    Retorno esperado: None (crea usuarios demo si no existen)
    """
    init_db(engine)
    ensure_demo_user()

def test_upload_csv():
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Verifica que el endpoint de upload procese correctamente un archivo CSV
    Parámetros de entrada:
        - POST /api/v1/files/upload
        - Header: Authorization: Bearer <token>
        - Form data: file (CSV con id,name,price), parametro1='a', parametro2='b'
    Retorno esperado: 200 OK con rows_saved en el body de la respuesta
    """
    login_resp = client.post('/api/v1/auth/login', json={'username':'uploader','password':'demo1234'})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login = login_resp.json()
    assert 'access_token' in login, f"Login response missing access_token: {login}"
    token = login['access_token']
    csv_content = 'id,name,price\n1,apple,1.5\n2,banana,2.0\n'
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    data = {'parametro1':'a','parametro2':'b'}
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/files/upload', data=data, files=files, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 'rows_saved' in body
