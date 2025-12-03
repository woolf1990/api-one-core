from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True, nullable=False) # Corregido por Edgar Nieto
    password_hash = Column(String(255), nullable=False) # Corregido por Edgar Nieto
    role = Column(String, nullable=False, default="usuario")
    created_at = Column(DateTime, server_default=func.now())
