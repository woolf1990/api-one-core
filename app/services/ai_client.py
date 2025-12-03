"""
Cliente de IA de alto nivel para análisis de documentos.

Por ahora es un stub: la integración real con el servicio de IA
deberá implementarse aquí. El servicio de documentos asume que
esta función puede lanzar excepciones (por ejemplo, si falla la conexión),
y hace fallback a solo guardar el archivo de forma local.
"""

from typing import Any, Dict


class AIServiceError(Exception):
    pass


def analyze_document(bytes_data: bytes, filename: str, content_type: str | None = None) -> Dict[str, Any]:
    """
    Analiza el documento usando un servicio de IA externo.

    Debe devolver un diccionario con, por ejemplo:
    {
        "classification": "FACTURA" o "INFORMACION",
        "client_name": "...",
        "client_address": "...",
        "provider_name": "...",
        "provider_address": "...",
        "invoice_number": "...",
        "invoice_date": "...",
        "total_amount": 123.45,
        "products": [...],
        "description": "...",
        "summary": "...",
        "sentiment": "positivo|negativo|neutral"
    }

    Actualmente lanza una excepción para simular que la conexión
    con la IA aún no está configurada. Esto permite probar el fallback.
    """
    raise AIServiceError("AI integration not configured yet")


