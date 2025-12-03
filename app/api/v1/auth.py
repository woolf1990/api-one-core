from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta
from app.core.security import create_access_token
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db import crud

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
    # For demo: check user in DB; otherwise create demo users
    user = crud.get_user_by_username(db, data.username)
    if not user or not crud.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id), "rol": user.role})
    return {"access_token": access_token, "expires_in": 15*60}
