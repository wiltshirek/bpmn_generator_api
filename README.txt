BPMN Generator API Documentation

1. DOCKER SETUP
--------------
# Build the container
docker build -t bpmn-generator .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here bpmn-generator

# The API will be available at http://localhost:8000

2. API ENDPOINTS
---------------
Base URL: http://localhost:8000/api/v1

A. Generate New BPMN Process
---------------------------
Endpoint: POST /bpmn
Description: Creates a new BPMN process from natural language description

curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple approval process with three steps: submit request, review request, and approve/reject",
    "chat_history": [],
    "existing_bpmn_xml": null
  }'

B. Update BPMN Layout
--------------------
Endpoint: POST /bpmn
Description: Modifies only the layout of existing BPMN XML

curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Move the approval task to the right of the review task",
    "chat_history": [],
    "existing_bpmn_xml": "<paste your existing BPMN XML here>"
  }'

3. TEST SCENARIOS
----------------

A. Generate New Process
----------------------
# Basic process
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple process where a user submits a form, then an admin reviews it, and finally sends an approval email",
    "chat_history": [],
    "existing_bpmn_xml": null
  }'

# Process with conditions
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a process where after form submission, if the amount is over $1000, get manager approval, otherwise auto-approve",
    "chat_history": [],
    "existing_bpmn_xml": null
  }'

B. Layout Updates
----------------
# Save the generated BPMN XML to a file first
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple approval process",
    "chat_history": [],
    "existing_bpmn_xml": null
  }' | jq -r '.bpmn_xml' > current_process.xml

# Then modify its layout
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Arrange all tasks in a vertical layout\",
    \"chat_history\": [],
    \"existing_bpmn_xml\": \"$(cat current_process.xml | sed 's/"/\\"/g')\"
  }"

C. Conversation Context
----------------------
# First message
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a process for employee onboarding",
    "chat_history": [],
    "existing_bpmn_xml": null
  }' | jq -r '.bpmn_xml' > onboarding.xml

# Follow-up modification
curl -X POST http://localhost:8000/api/v1/bpmn \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Add a background check step after the initial registration\",
    \"chat_history\": [
      {
        \"role\": \"user\",
        \"content\": \"Create a process for employee onboarding\"
      },
      {
        \"role\": \"assistant\",
        \"content\": \"I've created a basic employee onboarding process with registration, documentation, and orientation steps.\"
      }
    ],
    \"existing_bpmn_xml\": \"$(cat onboarding.xml | sed 's/"/\\"/g')\"
  }"

4. TROUBLESHOOTING
-----------------
- If you get a 400 error when updating layout, ensure you've included existing_bpmn_xml
- If you get a 500 error, check the Docker logs: docker logs <container_id>
- For XML validation errors, verify the BPMN XML structure matches the schema

5. ENVIRONMENT VARIABLES
----------------------
OPENAI_API_KEY: Your OpenAI API key (required)
PORT: API port (default: 8000)
LOG_LEVEL: Logging level (default: INFO)

6. HEALTH CHECK
--------------
curl http://localhost:8000/health

Expected response:
{
  "status": "healthy",
  "version": "1.0.0"
}

