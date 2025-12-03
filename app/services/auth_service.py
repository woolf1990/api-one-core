from app.db import crud
from app.db.session import SessionLocal
from contextlib import closing

def ensure_demo_user():
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, 'uploader')
        if not user:
            crud.create_user(db, 'uploader', 'password', role='uploader')
        user2 = crud.get_user_by_username(db, 'viewer')
        if not user2:
            crud.create_user(db, 'viewer', 'password', role='viewer')
    finally:
        db.close()
