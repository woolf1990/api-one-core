from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.base_class import Base

class FileValidation(Base):
    __tablename__ = 'file_validations'
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=True)
    row_number = Column(Integer, nullable=True)
    column_name = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
