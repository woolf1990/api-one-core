from app.db import crud
from app.db.session import SessionLocal
from contextlib import closing

def ensure_demo_user():
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Asegura que existan usuarios demo (uploader y viewer) en la base de datos. Si no existen, los crea.
    Parámetros de entrada: None
    Retorno esperado: None (función que crea usuarios si no existen)
    """
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, 'uploader')
        if not user:
            crud.create_user(db, 'uploader', 'demo1234', role='uploader')
        user2 = crud.get_user_by_username(db, 'viewer')
        if not user2:
            crud.create_user(db, 'viewer', 'demo1234', role='viewer')
    finally:
        db.close()
