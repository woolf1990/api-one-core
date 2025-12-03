from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, files, token
from app.db import base  # ensures models are created

app = FastAPI(title="FastAPI Test Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(token.router, prefix="/api/v1/token", tags=["Token"])

@app.get("/health")
def health():
    return {"status": "ok"}
