from app.db.base_class import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_demo_user():
    db = SessionLocal()
    try:
        # 1. Revisar si ya existe
        user = db.query(User).filter(User.username == "demo").first()
        if user:
            print("El usuario 'demo' ya existe.")
            return user

        # 2. Crear usuario nuevo
        hashed_password = pwd_context.hash("demo1234")

        new_user = User(
            username="demo",
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("Usuario demo creado correctamente.")
        return new_user

    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()
