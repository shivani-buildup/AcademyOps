from flask import Flask, request, jsonify
import logging
import sqlite3

from .models import Lead, LeadStage
from .repository import LeadRepository
from .exceptions import LeadError, LeadNotFound, DuplicatePhoneError, InvalidStageError

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Helper to get repo per request
def get_repo():
    return LeadRepository("data/academyops.db")

# --- Error Handlers ---

@app.errorhandler(LeadNotFound)
def handle_not_found(e):
    return jsonify({"error": str(e)}), 404

@app.errorhandler(DuplicatePhoneError)
def handle_duplicate(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(InvalidStageError)
def handle_invalid_stage(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(LeadError)
def handle_domain_error(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(404)
def handle_404_error(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def handle_500_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


# --- Endpoints ---

@app.route('/api/v1/leads', methods=['GET'])
def list_leads():
    stage = request.args.get('stage')
    source = request.args.get('source')
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        if page < 1 or limit < 1:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "Page and limit must be positive integers"}), 400
        
    repo = get_repo()
    leads = repo.list(stage=stage, source=source, limit=limit, offset=(page - 1) * limit)
    
    # Return as JSON (Lead dataclass can be converted to dict easily if needed, but we will construct explicitly or use asdict)
    import dataclasses
    return jsonify({
        "data": [dataclasses.asdict(l) for l in leads],
        "meta": {
            "page": page,
            "limit": limit
        }
    }), 200

@app.route('/api/v1/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    repo = get_repo()
    lead = repo.get(lead_id)
    import dataclasses
    return jsonify(dataclasses.asdict(lead)), 200

@app.route('/api/v1/leads', methods=['POST'])
def create_lead():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    name = data.get("name")
    phone = data.get("phone")
    if not name or not phone:
        return jsonify({"error": "name and phone are required fields"}), 400
        
    source = data.get("source", "Unknown")
    notes = data.get("notes", "")
    
    lead = Lead(name=name, phone=phone, source=source, notes=notes)
    repo = get_repo()
    
    # create() sets the ID and created_at/updated_at
    created_lead = repo.create(lead)
    
    import dataclasses
    return jsonify(dataclasses.asdict(created_lead)), 201

@app.route('/api/v1/leads/<int:lead_id>/stage', methods=['PATCH'])
def update_stage(lead_id):
    data = request.get_json()
    if not data or "stage" not in data:
        return jsonify({"error": "stage field is required"}), 400
        
    stage = data.get("stage")
    repo = get_repo()
    
    updated_lead = repo.update_stage(lead_id, stage)
    
    import dataclasses
    return jsonify(dataclasses.asdict(updated_lead)), 200

@app.route('/api/v1/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    repo = get_repo()
    repo.delete(lead_id)
    return '', 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
