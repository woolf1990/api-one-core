import json
from google import genai
from google.genai import types as genai_types
from app.core.config import settings
from app.utils.logger import logger


class AIServiceError(Exception):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Excepción personalizada para errores relacionados con el servicio de IA (Gemini)
    Parámetros de entrada: None (clase de excepción)
    Retorno esperado: None (clase de excepción)
    """
    pass


def _normalize_analysis_response(parsed: dict) -> dict:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Normaliza la respuesta de la IA para asegurar que todos los campos esperados estén presentes, estableciendo valores por defecto (None o []) para campos faltantes
    Parámetros de entrada:
        - parsed: dict - Diccionario con la respuesta parseada de la IA (debe contener al menos "classification")
    Retorno esperado: dict - Diccionario normalizado con todos los campos: classification, client_name, client_address, provider_name, provider_address, invoice_number, invoice_date, total_amount, products, description, summary, sentiment
    """
    classification = parsed.get("classification", "").upper()
    
    # Estructura base con todos los campos
    normalized = {
        "classification": classification,
        "client_name": None,
        "client_address": None,
        "provider_name": None,
        "provider_address": None,
        "invoice_number": None,
        "invoice_date": None,
        "total_amount": None,
        "products": [],
        "description": None,
        "summary": None,
        "sentiment": None,
    }
    
    # Actualizar con los valores de la respuesta parseada
    if classification == "FACTURA":
        normalized.update({
            "client_name": parsed.get("client_name"),
            "client_address": parsed.get("client_address"),
            "provider_name": parsed.get("provider_name"),
            "provider_address": parsed.get("provider_address"),
            "invoice_number": parsed.get("invoice_number"),
            "invoice_date": parsed.get("invoice_date"),
            "total_amount": parsed.get("total_amount"),
            "products": parsed.get("products", []),
        })
    elif classification == "INFORMACION":
        normalized.update({
            "description": parsed.get("description"),
            "summary": parsed.get("summary"),
            "sentiment": parsed.get("sentiment"),
        })
    
    return normalized


def _detect_file_type(content_type: str | None, filename: str) -> str:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Detecta el tipo de archivo basándose en el content_type y/o la extensión del nombre de archivo
    Parámetros de entrada:
        - content_type: str | None - Tipo MIME del archivo (ej: "application/pdf", "image/png")
        - filename: str - Nombre del archivo con extensión (ej: "documento.pdf", "imagen.png")
    Retorno esperado: str - Tipo de archivo detectado: "pdf" o "image"
    Excepciones: AIServiceError si el tipo de archivo no es reconocido
    """
    filename_lower = filename.lower()

    if content_type:
        if "pdf" in content_type:
            return "pdf"
        if "jpeg" in content_type or "jpg" in content_type or "png" in content_type:
            return "image"

    if filename_lower.endswith(".pdf"):
        return "pdf"
    if filename_lower.endswith((".jpg", ".jpeg", ".png")):
        return "image"

    raise AIServiceError(f"No se reconoce el tipo de archivo: {filename}")


def _build_analysis_prompt() -> str:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Construye el prompt de análisis para la IA Gemini, especificando el formato JSON esperado para FACTURA e INFORMACION
    Parámetros de entrada: None
    Retorno esperado: str - Prompt completo con instrucciones para clasificar y extraer datos del documento
    """
    return (
        "Analiza el documento. Primero clasifica como FACTURA o INFORMACION.\n\n"
        "Si es FACTURA, responde SOLO este JSON (sin texto adicional, sin markdown):\n"
        "{\n"
        '  "classification": "FACTURA",\n'
        '  "provider_name": "nombre del proveedor o null si no existe",\n'
        '  "provider_address": "dirección del proveedor o null si no existe",\n'
        '  "client_name": "nombre del cliente o null si no existe",\n'
        '  "client_address": "dirección del cliente o null si no existe",\n'
        '  "invoice_number": "número de factura o null si no existe",\n'
        '  "invoice_date": "fecha de factura o null si no existe",\n'
        '  "total_amount": número decimal del total o null si no existe,\n'
        '  "products": [\n'
        '    {"name": "nombre del producto", "quantity": cantidad (número) o null, "unit_price": precio unitario (número) o null, "total": total del producto (número) o null}\n'
        "  ],\n"
        '  "description": null,\n'
        '  "summary": null,\n'
        '  "sentiment": null\n'
        "}\n\n"
        "Si es INFORMACION, responde SOLO este JSON (sin texto adicional, sin markdown):\n"
        "{\n"
        '  "classification": "INFORMACION",\n'
        '  "description": "descripción detallada del contenido del documento",\n'
        '  "summary": "resumen breve del contenido",\n'
        '  "sentiment": "positivo" o "negativo" o "neutral" (basado en el tono del texto),\n'
        '  "client_name": null,\n'
        '  "client_address": null,\n'
        '  "provider_name": null,\n'
        '  "provider_address": null,\n'
        '  "invoice_number": null,\n'
        '  "invoice_date": null,\n'
        '  "total_amount": null,\n'
        '  "products": []\n'
        "}\n\n"
        "IMPORTANTE: Responde SOLO con el JSON válido, sin markdown, sin código, sin explicaciones. El JSON debe ser válido y parseable."
    )


def analyze_document(bytes_data: bytes, filename: str, content_type: str | None = None):
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Analiza un documento (PDF, JPG, PNG) usando la API de Gemini para clasificarlo y extraer información estructurada
    Parámetros de entrada:
        - bytes_data: bytes - Contenido del archivo en bytes
        - filename: str - Nombre del archivo (usado para detectar tipo)
        - content_type: str | None - Tipo MIME del archivo (opcional, usado para detectar tipo)
    Retorno esperado: dict - Diccionario normalizado con la clasificación y datos extraídos (classification, client_name, provider_name, invoice_number, etc. para FACTURA o description, summary, sentiment para INFORMACION)
    Excepciones: AIServiceError si GEMINI_API_KEY no está configurado o si ocurre un error al analizar el documento
    """
    if not settings.GEMINI_API_KEY:
        raise AIServiceError("GEMINI_API_KEY no está configurado")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        _detect_file_type(content_type, filename)
        prompt = _build_analysis_prompt()

        # Convertir bytes a formato Gemini
        file_input = genai_types.Part.from_bytes(
            mime_type=content_type or "application/octet-stream",
            data=bytes_data
        )

        # 🔥 Modelo correcto para la API v1beta
        result = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=[prompt, file_input]
        )

        text = result.text.strip()

        # Limpiar ` ```json `
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Parsear JSON
        parsed = json.loads(text)
        
        # Normalizar respuesta para asegurar que todos los campos estén presentes
        return _normalize_analysis_response(parsed)

    except Exception as e:
        logger.error(f"Error al analizar documento con Gemini: {e}")
        raise AIServiceError(f"Error al analizar documento con Gemini: {e}")
