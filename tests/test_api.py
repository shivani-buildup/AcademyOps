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
