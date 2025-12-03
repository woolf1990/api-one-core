import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import ensure_demo_user
import io

client = TestClient(app)

def setup_module(module):
    ensure_demo_user()

def test_upload_csv():
    login = client.post('/api/v1/auth/login', json={'username':'uploader','password':'password'}).json()
    token = login['access_token']
    csv_content = 'id,name,price\n1,apple,1.5\n2,banana,2.0\n'
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    data = {'parametro1':'a','parametro2':'b'}
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/files/upload', data=data, files=files, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert 'rows_saved' in body
