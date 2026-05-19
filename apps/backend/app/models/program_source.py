from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ProgramSource(Base):
    __tablename__ = "program_sources"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)
    
    source_url = Column(Text, nullable=False)
    source_type = Column(String, nullable=False)  # html, pdf, manual, other
    
    title = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    
    published_at = Column(Date, nullable=True)
    last_modified_at = Column(Date, nullable=True)
    fetched_at = Column(DateTime, nullable=True)
    checked_at = Column(DateTime, nullable=True)
    
    raw_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    program = relationship("SupportProgram", back_populates="sources")
