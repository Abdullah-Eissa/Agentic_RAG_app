from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid

class ChatHistory(SQLAlchemyBase):

    __tablename__ = "chat_history"

    chat_history_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_history_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    query = Column(String, nullable=False)
    answer = Column(String, nullable=True)
    
    
    chat_project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    # ondelete="CASCADE": to remove chat history if project is removed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    project = relationship("Project", back_populates="chat_history")

    __table_args__ = (
        Index('ix_chat_project_id', chat_project_id), # make an index for chat_project_id
    )

