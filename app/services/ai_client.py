import json
from google import genai
from google.genai import types as genai_types
from app.core.config import settings
from app.utils.logger import logger


class AIServiceError(Exception):
    pass


def _detect_file_type(content_type: str | None, filename: str) -> str:
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
    return (
        "Analiza el documento. Primero clasifica como FACTURA o INFORMACION.\n\n"
        "Si es FACTURA, responde SOLO este JSON:\n"
        "{\n"
        '  "classification": "FACTURA",\n'
        '  "provider_name": "",\n'
        '  "provider_address": "",\n'
        '  "client_name": "",\n'
        '  "client_address": "",\n'
        '  "invoice_number": "",\n'
        '  "invoice_date": "",\n'
        '  "total_amount": 0,\n'
        '  "products": [\n'
        '    {"name": "", "quantity": 0, "price": 0}\n'
        "  ]\n"
        "}\n\n"
        "Si es INFORMACION, responde solo:\n"
        '{ "classification": "INFORMACION" }'
    )


def analyze_document(bytes_data: bytes, filename: str, content_type: str | None = None):
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

        return json.loads(text)

    except Exception as e:
        logger.error(f"Error al analizar documento con Gemini: {e}")
        raise AIServiceError(f"Error al analizar documento con Gemini: {e}")
