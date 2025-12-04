import json
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.core.aws import upload_bytes_to_s3
from app.db.session import SessionLocal
from app.models.document import Document, DocumentAnalysis
from app.services.ai_client import analyze_document, AIServiceError


async def analyze_and_store_document(
    upload_file: UploadFile,
    uploaded_by: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Orquesta el flujo completo de análisis de documentos: guarda el archivo en S3/local, intenta análisis con IA Gemini, y guarda el documento y análisis en SQL Server. Si la IA falla, solo guarda el documento con estado "ai_failed"
    Parámetros de entrada:
        - upload_file: UploadFile - Archivo a analizar (PDF, JPG, PNG)
        - uploaded_by: str | None - ID del usuario que subió el archivo (opcional)
    Retorno esperado: dict - {"document_id": int, "analysis_id": int | None, "storage_path": str, "ai_status": str, "ai_error": str | None, "analysis": dict | None} donde ai_status puede ser "analyzed" o "ai_failed", y analysis contiene los datos extraídos si el análisis fue exitoso
    """
    contents = await upload_file.read()

    # 1) Guardar archivo en S3 o local (fallback ya manejado en upload_bytes_to_s3)
    key = f"documents/{upload_file.filename}"
    storage_path = upload_bytes_to_s3(contents, key)

    db = SessionLocal()
    try:
        # 2) Crear registro base del documento
        doc = Document(
            filename=upload_file.filename,
            storage_path=storage_path,
            content_type=upload_file.content_type,
            uploaded_by=uploaded_by,
            ai_status="pending",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        analysis_payload: Dict[str, Any] | None = None

        # 3) Intentar análisis con IA
        try:
            analysis_payload = analyze_document(
                contents,
                filename=upload_file.filename,
                content_type=upload_file.content_type,
            )
            doc.ai_status = "analyzed"
        except AIServiceError as e:
            # Fallback: solo guardamos el archivo y marcamos el error
            doc.ai_status = "ai_failed"
            doc.ai_error = str(e)
            analysis_payload = None

        # 4) Guardar análisis estructurado si lo hay
        analysis_id = None
        if analysis_payload:
            products = analysis_payload.get("products") or []
            products_json = json.dumps(products, ensure_ascii=False)

            analysis = DocumentAnalysis(
                document_id=doc.id,
                classification=analysis_payload.get("classification"),
                client_name=analysis_payload.get("client_name"),
                client_address=analysis_payload.get("client_address"),
                provider_name=analysis_payload.get("provider_name"),
                provider_address=analysis_payload.get("provider_address"),
                invoice_number=analysis_payload.get("invoice_number"),
                invoice_date=analysis_payload.get("invoice_date"),
                total_amount=analysis_payload.get("total_amount"),
                products_json=products_json,
                description=analysis_payload.get("description"),
                summary=analysis_payload.get("summary"),
                sentiment=analysis_payload.get("sentiment"),
            )
            db.add(analysis)
            db.flush()  # Para obtener el ID sin hacer commit
            analysis_id = analysis.id

        db.commit()

        return {
            "document_id": doc.id,
            "analysis_id": analysis_id,  # ID del análisis para poder modificarlo después
            "storage_path": doc.storage_path,
            "ai_status": doc.ai_status,
            "ai_error": doc.ai_error,
            "analysis": analysis_payload,
        }
    finally:
        db.close()




