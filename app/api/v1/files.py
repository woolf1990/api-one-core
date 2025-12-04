from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token, TokenError
from app.services.file_service import handle_upload
from app.services.document_service import analyze_and_store_document
from app.services.audit_service import log_event, EventType

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

    # Detectar archivos tabulares (CSV y Excel)
    is_tabular = (
        "csv" in content_type
        or filename.endswith(".csv")
        or filename.endswith(".xlsx")
        or filename.endswith(".xls")
        or "excel" in content_type
        or "spreadsheet" in content_type
    )

    # Flujo CSV/Excel: requiere parametro1 y parametro2 como en la lógica existente
    if is_tabular:
        if parametro1 is None or parametro2 is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="parametro1 and parametro2 are required for CSV/Excel uploads",
            )
        result = await handle_upload(
            file,
            parametro1,
            parametro2,
            uploaded_by=user_id,
        )
        
        # Registrar evento de auditoría para carga de CSV/Excel
        log_event(
            event_type=EventType.DOCUMENT_UPLOAD,
            description=f"Carga de archivo CSV/Excel: {file.filename}",
            user_id=user_id,
            metadata={
                "filename": file.filename,
                "file_id": result.get("file_id"),
                "rows_saved": result.get("rows_saved"),
                "validations_count": len(result.get("validations", [])),
                "file_type": "CSV/Excel"
            }
        )
        
        return result

    # Flujo documento (PDF/JPG/PNG, etc.): análisis IA + guardado
    result = await analyze_and_store_document(
        file,
        uploaded_by=user_id,
    )
    
    # Registrar evento de auditoría para carga de documento
    log_event(
        event_type=EventType.DOCUMENT_UPLOAD,
        description=f"Carga de documento: {file.filename}",
        user_id=user_id,
        metadata={
            "filename": file.filename,
            "document_id": result.get("document_id"),
            "ai_status": result.get("ai_status"),
            "file_type": "Documento"
        }
    )
    
    # Si se analizó con IA, registrar evento adicional
    if result.get("ai_status") == "analyzed":
        log_event(
            event_type=EventType.AI_ANALYSIS,
            description=f"Análisis IA completado para documento: {file.filename}",
            user_id=user_id,
            metadata={
                "filename": file.filename,
                "document_id": result.get("document_id"),
                "classification": result.get("analysis", {}).get("classification") if result.get("analysis") else None
            }
        )
    
    return result
