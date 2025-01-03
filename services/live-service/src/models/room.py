from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    channel_name = Column(String, unique=True, nullable=False)
    owner_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    room_type = Column(String, nullable=False)  # voice, video
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RoomParticipant(Base):
    __tablename__ = "room_participants"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False)  # host, participant
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)

    # Relationship with room
    room = relationship("Room", backref="participants")

class Message(Base):
    __tablename__ = "room_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    message_type = Column(String, nullable=False)  # text, system
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with room
    room = relationship("Room", backref="messages")
