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
    Orquesta el flujo de:
    - Guardar el archivo (S3 o local).
    - Intentar análisis con IA.
    - Guardar en SQL Server:
        - Documento.
        - Resultado de análisis (si existe).
    Si la IA falla, solo se guarda el documento.
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

        db.commit()

        return {
            "document_id": doc.id,
            "storage_path": doc.storage_path,
            "ai_status": doc.ai_status,
            "ai_error": doc.ai_error,
            "analysis": analysis_payload,
        }
    finally:
        db.close()




