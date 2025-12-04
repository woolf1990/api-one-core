"""
Servicio para actualizar análisis de documentos.
"""
import json
from typing import Optional, Dict, Any, List

from app.db.session import SessionLocal
from app.models.document import DocumentAnalysis
from app.utils.logger import logger


def update_document_analysis(
    analysis_id: int,
    classification: Optional[str] = None,
    client_name: Optional[str] = None,
    client_address: Optional[str] = None,
    provider_name: Optional[str] = None,
    provider_address: Optional[str] = None,
    invoice_number: Optional[str] = None,
    invoice_date: Optional[str] = None,
    total_amount: Optional[float] = None,
    products: Optional[List[Dict[str, Any]]] = None,
    description: Optional[str] = None,
    summary: Optional[str] = None,
    sentiment: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Actualiza un análisis de documento existente en la base de datos. Solo actualiza los campos proporcionados (actualización parcial)
    Parámetros de entrada:
        - analysis_id: int - ID del análisis a actualizar
        - classification: str | None - Clasificación del documento ("FACTURA" o "INFORMACION", opcional)
        - client_name: str | None - Nombre del cliente para facturas (opcional)
        - client_address: str | None - Dirección del cliente para facturas (opcional)
        - provider_name: str | None - Nombre del proveedor para facturas (opcional)
        - provider_address: str | None - Dirección del proveedor para facturas (opcional)
        - invoice_number: str | None - Número de factura (opcional)
        - invoice_date: str | None - Fecha de factura (opcional)
        - total_amount: float | None - Monto total de la factura (opcional)
        - products: list[dict] | None - Lista de productos con name, quantity, unit_price, total (opcional)
        - description: str | None - Descripción del contenido para documentos informativos (opcional)
        - summary: str | None - Resumen del contenido (opcional)
        - sentiment: str | None - Sentimiento ("positivo", "negativo", "neutral") (opcional)
    Retorno esperado: dict - Diccionario con el análisis actualizado incluyendo todos los campos (id, document_id, classification, client_name, etc., con products parseado desde JSON)
    Excepciones: ValueError si el análisis no existe
    """
    db = SessionLocal()
    try:
        # Buscar el análisis
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.id == analysis_id).first()
        
        if not analysis:
            raise ValueError(f"Análisis con ID {analysis_id} no encontrado")
        
        # Actualizar campos si se proporcionan
        if classification is not None:
            analysis.classification = classification
        
        if client_name is not None:
            analysis.client_name = client_name
        if client_address is not None:
            analysis.client_address = client_address
        if provider_name is not None:
            analysis.provider_name = provider_name
        if provider_address is not None:
            analysis.provider_address = provider_address
        if invoice_number is not None:
            analysis.invoice_number = invoice_number
        if invoice_date is not None:
            analysis.invoice_date = invoice_date
        if total_amount is not None:
            analysis.total_amount = total_amount
        
        if products is not None:
            products_json = json.dumps(products, ensure_ascii=False)
            analysis.products_json = products_json
        
        if description is not None:
            analysis.description = description
        if summary is not None:
            analysis.summary = summary
        if sentiment is not None:
            analysis.sentiment = sentiment
        
        db.commit()
        db.refresh(analysis)
        
        # Parsear products_json si existe
        products_list = None
        if analysis.products_json:
            try:
                products_list = json.loads(analysis.products_json)
            except (json.JSONDecodeError, TypeError):
                products_list = []
        
        return {
            "id": analysis.id,
            "document_id": analysis.document_id,
            "classification": analysis.classification,
            "client_name": analysis.client_name,
            "client_address": analysis.client_address,
            "provider_name": analysis.provider_name,
            "provider_address": analysis.provider_address,
            "invoice_number": analysis.invoice_number,
            "invoice_date": analysis.invoice_date,
            "total_amount": analysis.total_amount,
            "products": products_list,
            "description": analysis.description,
            "summary": analysis.summary,
            "sentiment": analysis.sentiment,
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar análisis de documento: {e}")
        raise
    finally:
        db.close()


def get_document_analysis(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Obtiene un análisis de documento por su ID desde la base de datos
    Parámetros de entrada:
        - analysis_id: int - ID del análisis a obtener
    Retorno esperado: dict | None - Diccionario con el análisis completo (id, document_id, classification, client_name, provider_name, invoice_number, total_amount, products, description, summary, sentiment) o None si no existe. El campo products se parsea desde JSON
    """
    db = SessionLocal()
    try:
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.id == analysis_id).first()
        
        if not analysis:
            return None
        
        # Parsear products_json si existe
        products_list = None
        if analysis.products_json:
            try:
                products_list = json.loads(analysis.products_json)
            except (json.JSONDecodeError, TypeError):
                products_list = []
        
        return {
            "id": analysis.id,
            "document_id": analysis.document_id,
            "classification": analysis.classification,
            "client_name": analysis.client_name,
            "client_address": analysis.client_address,
            "provider_name": analysis.provider_name,
            "provider_address": analysis.provider_address,
            "invoice_number": analysis.invoice_number,
            "invoice_date": analysis.invoice_date,
            "total_amount": analysis.total_amount,
            "products": products_list,
            "description": analysis.description,
            "summary": analysis.summary,
            "sentiment": analysis.sentiment,
        }
        
    except Exception as e:
        logger.error(f"Error al obtener análisis de documento: {e}")
        raise
    finally:
        db.close()

