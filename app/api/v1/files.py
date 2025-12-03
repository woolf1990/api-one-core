from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token, TokenError
from app.services.file_service import handle_upload
from app.services.document_service import analyze_and_store_document
from typing import List

router = APIRouter()
security = HTTPBearer()


def require_role(token: str, required_role: str):
    try:
        payload = verify_token(token)
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    if payload.get("rol") != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )
    return payload


@router.post("/upload")
async def upload_csv(
    parametro1: str = Form(...),
    parametro2: str = Form(...),
    file: UploadFile = File(...),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Endpoint existente para subir CSV con dos parámetros adicionales.
    """
    payload = require_role(creds.credentials, "uploader")
    result = await handle_upload(
        file,
        parametro1,
        parametro2,
        uploaded_by=payload.get("sub"),
    )
    return result


@router.post("/analyze-document")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Nuevo endpoint para análisis de documentos PDF/JPG/PNG.

    - Recibe un único archivo (campo `file`), compatible con una pantalla
      de carga de documentos.
    - Valida el token JWT y que el rol sea el adecuado.
    - Orquesta:
        - Guardar el archivo en S3 (si está configurado) o localmente.
        - Intentar análisis por IA (stub por ahora).
        - Guardar en SQL Server el documento y, si aplica, el análisis.
    - Si falla la conexión con la IA, solo se guarda el archivo.
    """
    payload = require_role(creds.credentials, "uploader")
    result = await analyze_and_store_document(
        file,
        uploaded_by=payload.get("sub"),
    )
    return result
