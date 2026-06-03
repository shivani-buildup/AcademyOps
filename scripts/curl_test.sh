#!/bin/bash

# Base URL for the AcademyOps API
API_URL="http://localhost:5000/api/v1/leads"

echo "=== AcademyOps API Curl Tests ==="

echo -e "\n1. Create a new lead (POST)"
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice Wonderland", "phone": "555-9999", "source": "Website", "notes": "Interested in engineering"}'

echo -e "\n\n2. List all leads (GET)"
curl -X GET $API_URL

echo -e "\n\n3. List leads with filters (GET)"
curl -X GET "$API_URL?stage=New&source=Website&page=1&limit=10"

# Note: For PATCH and DELETE, you need a specific Lead ID.
# For example:
# curl -X PATCH http://localhost:5000/api/v1/leads/1/stage -H "Content-Type: application/json" -d '{"stage": "Contacted"}'
# curl -X DELETE http://localhost:5000/api/v1/leads/1

echo -e "\n\nDone."
