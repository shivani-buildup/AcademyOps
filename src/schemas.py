from pydantic import BaseModel, Field
from typing import Optional

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
    
    class Config:
        from_attributes = True

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    intent: str
    suggested_stage: str
    reply: str
