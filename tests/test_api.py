import pytest

def test_create_lead_fastapi(test_client):
    payload = {
        "name": "Jane Doe",
        "phone": "555-0001",
        "source": "Website",
        "notes": "Testing FastAPI"
    }
    response = test_client.post("/api/v1/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["stage"] == "New"
    assert "id" in data

def test_get_lead_fastapi(test_client):
    # Create first
    payload = {"name": "Bob", "phone": "555-0002", "source": "Google"}
    create_resp = test_client.post("/api/v1/leads", json=payload)
    lead_id = create_resp.json()["id"]

    # Get it
    response = test_client.get(f"/api/v1/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Bob"

def test_update_stage_fastapi(test_client):
    payload = {"name": "Alice", "phone": "555-0003"}
    create_resp = test_client.post("/api/v1/leads", json=payload)
    lead_id = create_resp.json()["id"]

    update_payload = {"stage": "Contacted"}
    response = test_client.patch(f"/api/v1/leads/{lead_id}/stage", json=update_payload)
    assert response.status_code == 200
    assert response.json()["stage"] == "Contacted"

def test_delete_lead_fastapi(test_client):
    payload = {"name": "Eve", "phone": "555-0004"}
    create_resp = test_client.post("/api/v1/leads", json=payload)
    lead_id = create_resp.json()["id"]

    del_resp = test_client.delete(f"/api/v1/leads/{lead_id}")
    assert del_resp.status_code == 204

    get_resp = test_client.get(f"/api/v1/leads/{lead_id}")
    assert get_resp.status_code == 404

def test_create_lead_invalid_payload(test_client):
    payload = {"phone": "555-0005"}  # Missing name
    response = test_client.post("/api/v1/leads", json=payload)
    assert response.status_code == 422

def test_list_pagination(test_client):
    for i in range(5):
        test_client.post("/api/v1/leads", json={"name": f"User {i}", "phone": f"555-100{i}"})
    
    response = test_client.get("/api/v1/leads?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5

def test_list_combined_filters(test_client):
    test_client.post("/api/v1/leads", json={"name": "Alice Filter", "phone": "555-2001", "source": "LinkedIn"})
    
    resp = test_client.post("/api/v1/leads", json={"name": "Bob Filter", "phone": "555-2002", "source": "LinkedIn"})
    lead_id = resp.json()["id"]
    test_client.patch(f"/api/v1/leads/{lead_id}/stage", json={"stage": "Contacted"})
    
    response = test_client.get("/api/v1/leads?source=LinkedIn&stage=Contacted")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Bob Filter"

def test_get_nonexistent_404(test_client):
    response = test_client.get("/api/v1/leads/999999")
    assert response.status_code == 404
