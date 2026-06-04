from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.database import Base
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class LeadStage(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    DEMO = "Demo"
    ENROLLED = "Enrolled"
    LOST = "Lost"

@dataclass
class Lead:
    name: str
    phone: str
    source: str = "Unknown"
    stage: LeadStage = LeadStage.NEW
    notes: Optional[str] = ""
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    source = Column(String)
    stage = Column(String, index=True, nullable=False)
    notes = Column(String)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
