from .session import engine, SessionLocal
from .base import init_db
# create tables
init_db(engine)
# create demo users if not exist
from app.services.auth_service import ensure_demo_user
ensure_demo_user()
print('Database initialized and demo users ensured.')
