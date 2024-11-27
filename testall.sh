#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api"
OUTPUT_DIR="test_outputs"
mkdir -p $OUTPUT_DIR

# Function to handle API errors
check_response() {
    if [ $? -ne 0 ]; then
        echo "=== ERROR === API call failed"
        exit 1
    fi
}

# Test Case 1: Generate new BPMN
echo "=== DEBUG === Test Case 1: Generating new BPMN process"
RESPONSE=$(curl -s -X POST "$API_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple approval process with: 1. Start event 2. Review task 3. Approval gateway 4. Approve task 5. Reject task 6. End events",
    "chat_history": []
  }')
check_response

# Save the BPMN XML
echo $RESPONSE | jq -r '.bpmn_xml' > "$OUTPUT_DIR/initial_bpmn.xml"

# Test Case 2: Update layout
echo "=== DEBUG === Test Case 2: Testing layout update"
UPDATE_RESPONSE=$(curl -s -X POST "$API_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Move the approval gateway closer to the review task\",
    \"chat_history\": [],
    \"existing_bpmn_xml\": $(cat "$OUTPUT_DIR/initial_bpmn.xml" | jq -R -s '.')
  }")
check_response

# Save the updated BPMN
echo $UPDATE_RESPONSE | jq -r '.bpmn_xml' > "$OUTPUT_DIR/updated_bpmn.xml"

echo "=== INFO === Test execution completed. Output files are in $OUTPUT_DIR/"