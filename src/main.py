from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db, engine, Base
from src.models import LeadModel
from src.schemas import LeadCreate, LeadUpdateStage, LeadResponse, LeadListResponse, MessageRequest, MessageResponse
from src.classifier import RuleBasedClassifier
from sqlalchemy.exc import IntegrityError
import logging

# Initialize DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AcademyOps API", version="1.0.0", docs_url=None, redoc_url=None)
classifier_instance = RuleBasedClassifier()

logging.basicConfig(filename='academyops.log', level=logging.INFO)

# --- Custom Premium UI HTML/CSS --- Loaded from templates
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(BASE_DIR, 'templates', 'landing.html'), 'r', encoding='utf-8') as f:
        ROOT_HTML = f.read()
    with open(os.path.join(BASE_DIR, 'templates', 'swagger.css'), 'r', encoding='utf-8') as f:
        SWAGGER_CUSTOM_CSS = f.read()
except Exception as e:
    ROOT_HTML = '<html><body><h1>API Active</h1></body></html>'
    SWAGGER_CUSTOM_CSS = ''
    logging.error(f'Failed to load templates: {e}')
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def get_root():
    return HTMLResponse(content=ROOT_HTML, status_code=200)

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_html():
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="AcademyOps API - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )
    
    # Decode base response and inject our custom dark CSS styles + JS fix for microlight inline colors
    html_content = response.body.decode("utf-8")

    # JS that aggressively re-colors all microlight inline spans on every render
    js_fix = """
<script>
(function() {
    // Determine if a color string is any shade of green/lime/teal
    function isGreenish(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === 'green' || c === 'lime' || c === '#008000' || c === '#00ff00' || c === '#0f0') return true;
        if (c === '#10b981' || c === '#059669' || c === '#00cc00' || c === '#34d399') return true;
        // rgb(...) patterns
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) {
            var r = +m[1], g = +m[2], b = +m[3];
            // Greenish: green channel dominant AND reasonably saturated
            if (g > 100 && g > r * 1.4 && g > b * 1.4) return true;
            // Pure/near-pure green
            if (r === 0 && g === 128 && b === 0) return true;
        }
        return false;
    }

    function isNavyBlue(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === '#000080') return true;
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) { var r=+m[1],g=+m[2],b=+m[3]; return r===0 && g===0 && b===128; }
        return false;
    }

    function isBrightBlue(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === 'blue' || c === '#0000ff' || c === '#00f') return true;
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) { var r=+m[1],g=+m[2],b=+m[3]; return r===0 && g===0 && b===255; }
        return false;
    }

    function fixSpan(el) {
        var raw = el.style.color;
        if (!raw) return;
        if (isGreenish(raw)) {
            el.style.setProperty('color', '#3730a3', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#3730a3', 'important');
        } else if (isNavyBlue(raw)) {
            el.style.setProperty('color', '#0369a1', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#0369a1', 'important');
        } else if (isBrightBlue(raw)) {
            el.style.setProperty('color', '#b45309', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#b45309', 'important');
        }
    }

    function fixAll() {
        document.querySelectorAll('pre.microlight span, pre.microlight').forEach(fixSpan);
    }

    // MutationObserver: fires on every DOM change (Swagger re-renders on expand)
    var observer = new MutationObserver(function(mutations) {
        for (var i = 0; i < mutations.length; i++) {
            if (mutations[i].addedNodes.length || mutations[i].type === 'attributes') {
                fixAll();
                return;
            }
        }
    });

    function init() {
        if (document.body) {
            observer.observe(document.body, {
                childList: true, subtree: true,
                attributes: true, attributeFilter: ['style']
            });
            fixAll();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Safety net: re-run at increasing intervals after page load
    [100, 300, 600, 1200, 2500, 5000].forEach(function(ms) {
        setTimeout(fixAll, ms);
    });
})();
</script>
"""

    injection = f"<style>{SWAGGER_CUSTOM_CSS}</style>{js_fix}</head>"
    html_content = html_content.replace("</head>", injection)
    
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="AcademyOps API - ReDoc Reference",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.77/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/api/v1/stats", include_in_schema=True)
def get_api_stats(db: Session = Depends(get_db)):
    total = db.query(LeadModel).count()
    
    active_stages = ["New", "Contacted", "Qualified", "Demo"]
    active = db.query(LeadModel).filter(LeadModel.stage.in_(active_stages)).count()
    
    enrolled = db.query(LeadModel).filter(LeadModel.stage == "Enrolled").count()
    lost = db.query(LeadModel).filter(LeadModel.stage == "Lost").count()
    
    conversion_rate = (enrolled / total * 100) if total > 0 else 0.0
    
    stages = ["New", "Contacted", "Qualified", "Demo", "Enrolled", "Lost"]
    stage_counts = {}
    for s in stages:
        stage_counts[s] = db.query(LeadModel).filter(LeadModel.stage == s).count()
        
    return {
        "total_leads": total,
        "active_pipeline": active,
        "enrolled_leads": enrolled,
        "lost_leads": lost,
        "conversion_rate": conversion_rate,
        "stage_distribution": stage_counts
    }

@app.get("/api/v1/leads", response_model=LeadListResponse)
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
    
    total = query.count()
    offset = (page - 1) * limit
    leads = query.offset(offset).limit(limit).all()
    return {"items": leads, "total": total}

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

