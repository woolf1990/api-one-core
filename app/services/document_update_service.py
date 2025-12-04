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
    Actualiza un análisis de documento existente.
    
    Args:
        analysis_id: ID del análisis a actualizar
        classification: Clasificación del documento ("FACTURA" o "INFORMACION")
        client_name: Nombre del cliente (para facturas)
        client_address: Dirección del cliente (para facturas)
        provider_name: Nombre del proveedor (para facturas)
        provider_address: Dirección del proveedor (para facturas)
        invoice_number: Número de factura (para facturas)
        invoice_date: Fecha de factura (para facturas)
        total_amount: Monto total (para facturas)
        products: Lista de productos (para facturas)
        description: Descripción (para información)
        summary: Resumen (para información)
        sentiment: Sentimiento ("positivo", "negativo", "neutral") (para información)
    
    Returns:
        Dict con el análisis actualizado
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
    Obtiene un análisis de documento por su ID.
    
    Args:
        analysis_id: ID del análisis
    
    Returns:
        Dict con el análisis o None si no existe
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

