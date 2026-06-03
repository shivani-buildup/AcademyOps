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
    source: Optional[str] = None
    stage: LeadStage = LeadStage.NEW
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
