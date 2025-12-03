from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.base_class import Base

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())
