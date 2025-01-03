from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # pending, paid, completed, cancelled
    items = Column(JSON, nullable=False)  # List of ordered items with quantities
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # cocktail, beer, wine, spirit, etc.
    alcohol_content = Column(Float, nullable=True)
    flavor_profile = Column(JSON, nullable=True)  # List of flavor tags
    ingredients = Column(JSON, nullable=True)  # List of ingredients
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
