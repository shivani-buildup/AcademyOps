from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db, engine, Base
from src.models import LeadModel
from src.schemas import LeadCreate, LeadUpdateStage, LeadResponse, MessageRequest, MessageResponse
from src.classifier import RuleBasedClassifier
from sqlalchemy.exc import IntegrityError
import logging

# Initialize DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AcademyOps API", version="1.0.0")
classifier_instance = RuleBasedClassifier()

logging.basicConfig(filename='academyops.log', level=logging.INFO)

@app.get("/api/v1/leads", response_model=List[LeadResponse])
def list_leads(
    stage: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(LeadModel)
    if stage:
        query = query.filter(LeadModel.stage == stage)
    if source:
        query = query.filter(LeadModel.source == source)
    
    offset = (page - 1) * limit
    leads = query.offset(offset).limit(limit).all()
    return leads

@app.get("/api/v1/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/api/v1/leads", response_model=LeadResponse, status_code=201)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = LeadModel(
        name=lead.name,
        phone=lead.phone,
        source=lead.source,
        stage="New",
        notes=lead.notes
    )
    db.add(db_lead)
    try:
        db.commit()
        db.refresh(db_lead)
        logging.info(f"Created lead: {db_lead.phone}")
        return db_lead
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone number already exists")

@app.patch("/api/v1/leads/{lead_id}/stage", response_model=LeadResponse)
def update_lead_stage(lead_id: int, stage_update: LeadUpdateStage, db: Session = Depends(get_db)):
    valid_stages = ["New", "Contacted", "Qualified", "Demo", "Enrolled", "Lost"]
    if stage_update.stage not in valid_stages:
        raise HTTPException(status_code=400, detail="Invalid stage")
        
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.stage = stage_update.stage
    db.commit()
    db.refresh(lead)
    logging.info(f"Updated lead {lead_id} to stage {stage_update.stage}")
    return lead

@app.delete("/api/v1/leads/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    logging.info(f"Deleted lead {lead_id}")
    return None

@app.post("/api/v1/leads/{lead_id}/message", response_model=MessageResponse)
def classify_message(lead_id: int, msg: MessageRequest, db: Session = Depends(get_db)):
    # Verify lead exists
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    result = classifier_instance.classify(msg.message)
    return result
