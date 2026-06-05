from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class LeadBase(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=5)
    source: Optional[str] = "Unknown"
    notes: Optional[str] = ""

class LeadCreate(LeadBase):
    pass

class LeadUpdateStage(BaseModel):
    stage: str = Field(...)

class LeadResponse(LeadBase):
    id: int
    stage: str
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)

class LeadListResponse(BaseModel):
    items: List[LeadResponse]
    total: int

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    intent: str
    suggested_stage: str
    reply: str
