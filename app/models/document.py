from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, func
from app.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    uploaded_by = Column(String, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())

    # Estado del análisis por IA
    ai_status = Column(String, nullable=True)  # e.g. "pending", "analyzed", "ai_failed"
    ai_error = Column(String, nullable=True)


class DocumentAnalysis(Base):
    """
    Resultado estructurado del análisis del documento.
    Se cubren ambos tipos:
    - Factura: datos económicos/financieros.
    - Información: resumen, descripción, sentimiento.
    """

    __tablename__ = "document_analyses"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Clasificación general: "FACTURA" o "INFORMACION"
    classification = Column(String, nullable=True)

    # Datos de factura
    client_name = Column(String, nullable=True)
    client_address = Column(String, nullable=True)
    provider_name = Column(String, nullable=True)
    provider_address = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)

    # Para simplificar, guardamos los productos como JSON serializado
    products_json = Column(Text, nullable=True)

    # Datos de información general
    description = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)  # "positivo", "negativo", "neutral"

    created_at = Column(DateTime, server_default=func.now())



