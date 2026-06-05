import requests
import time
import threading
from src.main import app

def run_server():
    app.run(port=5000, debug=False, use_reloader=False)

# Start server in a background thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# Give it a second to start
time.sleep(2)

base_url = "http://localhost:5000/api/v1/leads"

print("1. Testing GET /leads")
r = requests.get(base_url)
print(r.status_code, r.json())

print("\n2. Testing POST /leads (Valid)")
payload = {"name": "API Test", "phone": "555-8888", "source": "Website"}
r = requests.post(base_url, json=payload)
print(r.status_code, r.json())
lead_id = r.json().get('id')

print("\n3. Testing POST /leads (Duplicate)")
r = requests.post(base_url, json=payload)
print(r.status_code, r.json())

print(f"\n4. Testing GET /leads/{lead_id}")
r = requests.get(f"{base_url}/{lead_id}")
print(r.status_code, r.json())

print(f"\n5. Testing PATCH /leads/{lead_id}/stage (Valid)")
r = requests.patch(f"{base_url}/{lead_id}/stage", json={"stage": "Contacted"})
print(r.status_code, r.json())

print(f"\n6. Testing PATCH /leads/{lead_id}/stage (Invalid)")
r = requests.patch(f"{base_url}/{lead_id}/stage", json={"stage": "FakeStage"})
print(r.status_code, r.json())

print(f"\n7. Testing DELETE /leads/{lead_id}")
r = requests.delete(f"{base_url}/{lead_id}")
print(r.status_code)

print(f"\n8. Testing GET /leads/{lead_id} after delete")
r = requests.get(f"{base_url}/{lead_id}")
print(r.status_code, r.json())

print("\nDone.")
