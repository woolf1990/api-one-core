from .session import engine, SessionLocal
from .base import init_db as _init_db


def init_db():
    """
    Inicializa la base de datos y crea usuarios demo.
    Se llama explícitamente (por ejemplo, desde scripts o tests),
    en lugar de ejecutarse al importar el módulo.
    """
    from app.services.auth_service import ensure_demo_user

    _init_db(engine)
    ensure_demo_user()
    print("Database initialized and demo users ensured.")
