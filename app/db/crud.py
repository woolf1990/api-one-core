from sqlalchemy.orm import Session
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, role: str = "uploader"):
    hashed = pwd_context.hash(password)
    u = User(username=username, password_hash=hashed, role=role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def verify_password(plain_password: str, hashed: str):
    return pwd_context.verify(plain_password, hashed)
