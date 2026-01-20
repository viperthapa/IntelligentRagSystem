from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pgvector.sqlalchemy import Vector

from app.config import settings
from app.database import Base

class Document(Base):
    """
    Represents an uploaded document.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_type = Column(String(10), nullable=False)  # pdf, txt, md
    content = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationship to chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))
    chunk_index = Column(Integer)
    document = relationship("Document", back_populates="chunks")