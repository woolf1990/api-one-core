import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import ensure_demo_user

client = TestClient(app)

def setup_module(module):
    ensure_demo_user()

def test_login_success():
    resp = client.post('/api/v1/auth/login', json={'username':'uploader','password':'password'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data
