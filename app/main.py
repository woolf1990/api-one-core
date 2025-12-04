from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, files, token, audit
from app.db.base import init_db
from app.db.base_class import engine
from app.services.auth_service import ensure_demo_user

app = FastAPI(title="FastAPI Test Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    Inicializa la base de datos y crea usuarios demo al arrancar la app.
    Evitamos efectos secundarios al importar módulos.
    """
    init_db(engine)
    ensure_demo_user()


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(token.router, prefix="/api/v1/token", tags=["Token"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])


@app.get("/health")
def health():
    return {"status": "ok"}
