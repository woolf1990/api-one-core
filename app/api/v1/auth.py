from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta
from app.core.security import create_access_token
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db import crud
from app.services.audit_service import log_event, EventType

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Endpoint para autenticación de usuarios. Verifica credenciales y retorna un token JWT de acceso. Registra eventos de auditoría para login exitoso y fallido
    Parámetros de entrada:
        - data: LoginRequest - Objeto con username y password
        - db: Session - Sesión de base de datos (inyectada por FastAPI)
    Retorno esperado: TokenResponse - {"access_token": str, "token_type": "bearer", "expires_in": int} con el token JWT y tiempo de expiración en segundos
    Excepciones: HTTPException 401 si las credenciales son inválidas
    """
    # For demo: check user in DB; otherwise create demo users
    user = crud.get_user_by_username(db, data.username)
    if not user or not crud.verify_password(data.password, user.password_hash):
        # Registrar intento de login fallido
        log_event(
            event_type=EventType.LOGIN,
            description=f"Intento de login fallido para usuario: {data.username}",
            user_id=None,
            metadata={"username": data.username, "success": False}
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id), "rol": user.role})
    
    # Registrar login exitoso
    log_event(
        event_type=EventType.LOGIN,
        description=f"Login exitoso para usuario: {data.username}",
        user_id=str(user.id),
        metadata={"username": data.username, "role": user.role, "success": True}
    )
    
    return {"access_token": access_token, "expires_in": 15*60}
