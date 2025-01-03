from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    context = Column(JSON, nullable=True)  # Store conversation context/state
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with messages
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(String, nullable=False)
    moderation_result = Column(JSON, nullable=True)  # Store OpenAI moderation results
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")
