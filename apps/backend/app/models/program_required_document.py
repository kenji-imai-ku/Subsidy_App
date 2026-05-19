from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ProgramRequiredDocument(Base):
    __tablename__ = "program_required_documents"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)
    
    document_name = Column(String, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    program = relationship("SupportProgram", back_populates="required_document_items")
