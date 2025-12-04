from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.security import verify_token, TokenError
from app.services.file_service import handle_upload
from app.services.document_service import analyze_and_store_document
from app.services.document_update_service import update_document_analysis, get_document_analysis
from app.services.audit_service import log_event, EventType

router = APIRouter()
security = HTTPBearer()


def require_role(token: str, required_role: str):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Función helper para verificar que un token JWT sea válido y que el usuario tenga el rol requerido
    Parámetros de entrada:
        - token: str - Token JWT a verificar
        - required_role: str - Rol requerido (ej: "uploader")
    Retorno esperado: dict - Payload del token decodificado con los datos del usuario (sub, rol)
    Excepciones: HTTPException 401 si el token es inválido o expirado, HTTPException 403 si el usuario no tiene el rol requerido
    """
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
    Generado por IA - Fecha: 2024-12-19
    Descripción: Endpoint unificado para carga de archivos. Clasifica automáticamente el tipo de archivo: CSV/Excel requiere parametro1 y parametro2 y procesa con validaciones, mientras que PDF/JPG/PNG se analiza con IA Gemini. Registra eventos de auditoría para cada tipo de carga
    Parámetros de entrada:
        - file: UploadFile - Archivo a subir (CSV, Excel, PDF, JPG, PNG)
        - parametro1: str | None - Primer parámetro requerido para CSV/Excel (opcional para documentos)
        - parametro2: str | None - Segundo parámetro requerido para CSV/Excel (opcional para documentos)
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - Para CSV/Excel: {"file_id": int, "s3_path": str, "rows_saved": int, "validations": list}. Para documentos: {"document_id": int, "analysis_id": int | None, "storage_path": str, "ai_status": str, "ai_error": str | None, "analysis": dict | None}
    Excepciones: HTTPException 400 si faltan parametro1/parametro2 para CSV/Excel, HTTPException 401/403 si no está autenticado o no tiene rol "uploader"
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


class DocumentAnalysisUpdate(BaseModel):
    """Modelo para actualizar análisis de documento."""
    classification: Optional[str] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    provider_name: Optional[str] = None
    provider_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    products: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None


@router.get("/analysis/{analysis_id}")
def get_analysis(
    analysis_id: int,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Obtiene un análisis de documento por su ID desde la base de datos. Requiere autenticación JWT y rol "uploader"
    Parámetros de entrada:
        - analysis_id: int - ID del análisis a obtener (path parameter)
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - Diccionario con el análisis completo (id, document_id, classification, client_name, provider_name, invoice_number, total_amount, products, description, summary, sentiment)
    Excepciones: HTTPException 404 si el análisis no existe, HTTPException 401/403 si no está autenticado o no tiene rol "uploader"
    """
    payload = require_role(creds.credentials, "uploader")
    
    try:
        analysis = get_document_analysis(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Análisis con ID {analysis_id} no encontrado"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener análisis: {str(e)}"
        )


@router.put("/analysis/{analysis_id}")
def update_analysis(
    analysis_id: int,
    update_data: DocumentAnalysisUpdate = Body(...),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Actualiza un análisis de documento existente. Solo actualiza los campos proporcionados en el body (actualización parcial). Requiere autenticación JWT y rol "uploader". Registra evento de auditoría para la actualización
    Parámetros de entrada:
        - analysis_id: int - ID del análisis a actualizar (path parameter)
        - update_data: DocumentAnalysisUpdate - Objeto con los campos a actualizar (classification, client_name, provider_name, invoice_number, total_amount, products, description, summary, sentiment)
        - creds: HTTPAuthorizationCredentials - Credenciales HTTP con token Bearer (inyectado por FastAPI)
    Retorno esperado: dict - Diccionario con el análisis actualizado incluyendo todos los campos
    Excepciones: HTTPException 404 si el análisis no existe, HTTPException 401/403 si no está autenticado o no tiene rol "uploader", HTTPException 500 si ocurre un error al actualizar
    """
    payload = require_role(creds.credentials, "uploader")
    user_id = payload.get("sub")
    
    try:
        # Convertir el modelo Pydantic a dict y filtrar None
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Actualizar el análisis
        updated_analysis = update_document_analysis(
            analysis_id=analysis_id,
            **update_dict
        )
        
        # Registrar evento de auditoría
        log_event(
            event_type=EventType.USER_INTERACTION,
            description=f"Análisis de documento actualizado: ID {analysis_id}",
            user_id=user_id,
            metadata={
                "analysis_id": analysis_id,
                "document_id": updated_analysis.get("document_id"),
                "updated_fields": list(update_dict.keys())
            }
        )
        
        return updated_analysis
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar análisis: {str(e)}"
        )
