from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.base_class import Base

class DataRow(Base):
    __tablename__ = 'data_table'
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), index=True, nullable=True)
    name = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
