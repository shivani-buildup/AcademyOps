def test_create_lead_api(test_client):
    payload = {"name": "API User", "phone": "123-4567", "source": "Website"}
    response = test_client.post('/api/v1/leads', json=payload)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "API User"
    assert data["id"] is not None

def test_create_lead_validation_error(test_client):
    payload = {"name": "No Phone"}
    response = test_client.post('/api/v1/leads', json=payload)
    
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_duplicate_lead_api(test_client):
    payload = {"name": "Duplicate", "phone": "999"}
    test_client.post('/api/v1/leads', json=payload)
    response = test_client.post('/api/v1/leads', json=payload)
    
    assert response.status_code == 400
    assert "already exists" in response.get_json()["error"]

def test_get_lead_api(test_client):
    post_res = test_client.post('/api/v1/leads', json={"name": "Get Me", "phone": "000"})
    lead_id = post_res.get_json()["id"]
    
    response = test_client.get(f'/api/v1/leads/{lead_id}')
    assert response.status_code == 200
    assert response.get_json()["name"] == "Get Me"

def test_get_nonexistent_lead_api(test_client):
    response = test_client.get('/api/v1/leads/999')
    assert response.status_code == 404

def test_list_leads_api(test_client):
    test_client.post('/api/v1/leads', json={"name": "L1", "phone": "111"})
    test_client.post('/api/v1/leads', json={"name": "L2", "phone": "222"})
    
    response = test_client.get('/api/v1/leads')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 2
    assert data["meta"]["page"] == 1

def test_update_stage_api(test_client):
    post_res = test_client.post('/api/v1/leads', json={"name": "Patch Me", "phone": "333"})
    lead_id = post_res.get_json()["id"]
    
    response = test_client.patch(f'/api/v1/leads/{lead_id}/stage', json={"stage": "Demo"})
    assert response.status_code == 200
    assert response.get_json()["stage"] == "Demo"

def test_update_invalid_stage_api(test_client):
    post_res = test_client.post('/api/v1/leads', json={"name": "Patch Me", "phone": "444"})
    lead_id = post_res.get_json()["id"]
    
    response = test_client.patch(f'/api/v1/leads/{lead_id}/stage', json={"stage": "Invalid"})
    assert response.status_code == 400

def test_delete_lead_api(test_client):
    post_res = test_client.post('/api/v1/leads', json={"name": "Del Me", "phone": "555"})
    lead_id = post_res.get_json()["id"]
    
    del_res = test_client.delete(f'/api/v1/leads/{lead_id}')
    assert del_res.status_code == 204
    
    get_res = test_client.get(f'/api/v1/leads/{lead_id}')
    assert get_res.status_code == 404
