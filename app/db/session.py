from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from typing import Generator

# Usamos directamente tu cadena ya generada en database.py
from app.db.base_class import engine, SessionLocal as BaseSessionLocal

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Sobrescribimos con el SessionLocal definido en base_class para tener un solo origen
SessionLocal = BaseSessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
