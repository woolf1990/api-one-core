from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token, TokenError
from app.services.file_service import handle_upload
from app.services.document_service import analyze_and_store_document

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
async def upload_file(
    file: UploadFile = File(...),
    parametro1: str | None = Form(None),
    parametro2: str | None = Form(None),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Endpoint unificado para:
    - CSV: carga y validación con parámetros adicionales (parametro1, parametro2).
    - Documentos (PDF/JPG/PNG, etc.): análisis por IA y guardado del resultado.

    La lógica se clasifica automáticamente según el tipo/nombre del archivo.
    """
    payload = require_role(creds.credentials, "uploader")
    user_id = payload.get("sub")

    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()

    is_csv = (
        "csv" in content_type
        or filename.endswith(".csv")
        or "excel" in content_type
    )

    # Flujo CSV: requiere parametro1 y parametro2 como en la lógica existente
    if is_csv:
        if parametro1 is None or parametro2 is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="parametro1 and parametro2 are required for CSV uploads",
            )
        return await handle_upload(
            file,
            parametro1,
            parametro2,
            uploaded_by=user_id,
        )

    # Flujo documento (PDF/JPG/PNG, etc.): análisis IA + guardado
    return await analyze_and_store_document(
        file,
        uploaded_by=user_id,
    )
