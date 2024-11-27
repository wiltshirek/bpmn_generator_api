#!/bin/bash

# Set up test environment
BASE_URL="http://localhost:8000/api"

# Function to validate JSON response
validate_response() {
    local response=$1
    local step=$2
    
    if ! echo "$response" | jq -e '.bpmn_xml' > /dev/null; then
        echo "Error: $step failed"
        echo "Response: $response"
        exit 1
    fi
}

# 1. Initial BPMN Generation
echo "=== Step 1: Initial BPMN Generation ==="
INITIAL_PROMPT=$(cat <<'EOF'
Create a BPMN process for medical credentialing:
1. Start with application receipt
2. Initial screening
3. Parallel document verification and background check
4. Committee review
5. Director approval
6. End with welcome packet or rejection
EOF
)

# Escape newlines and quotes for JSON
INITIAL_PROMPT_ESCAPED=$(echo "$INITIAL_PROMPT" | jq -R -s '.')

RESPONSE=$(curl -s -X POST "$BASE_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": ${INITIAL_PROMPT_ESCAPED},
    \"chat_history\": [{
      \"role\": \"user\",
      \"content\": ${INITIAL_PROMPT_ESCAPED}
    }]
  }")

validate_response "$RESPONSE" "Initial BPMN generation"
BPMN_XML=$(echo "$RESPONSE" | jq -r '.bpmn_xml')
echo "Initial BPMN XML generated successfully (${#BPMN_XML} characters)"

# 2. Layout Update
echo -e "\n=== Step 2: Layout Update ==="
LAYOUT_PROMPT="Align the document verification and background check horizontally"

LAYOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"$LAYOUT_PROMPT\",
    \"chat_history\": [{
      \"role\": \"user\",
      \"content\": \"$LAYOUT_PROMPT\"
    }],
    \"existing_bpmn_xml\": $(echo "$BPMN_XML" | jq -R -s '.')
  }")

validate_response "$LAYOUT_RESPONSE" "Layout update"
BPMN_XML=$(echo "$LAYOUT_RESPONSE" | jq -r '.bpmn_xml')
echo "Layout updated successfully"

# 3. Process Update
echo -e "\n=== Step 3: Process Update ==="
UPDATE_PROMPT="Add a drug screening step after background check"

UPDATE_RESPONSE=$(curl -s -X POST "$BASE_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"$UPDATE_PROMPT\",
    \"chat_history\": [{
      \"role\": \"user\",
      \"content\": \"$UPDATE_PROMPT\"
    }],
    \"existing_bpmn_xml\": $(echo "$BPMN_XML" | jq -R -s '.')
  }")

validate_response "$UPDATE_RESPONSE" "Process update"
BPMN_XML=$(echo "$UPDATE_RESPONSE" | jq -r '.bpmn_xml')
echo "Process updated successfully"

# 4. Beautification
echo -e "\n=== Step 4: Beautification ==="
BEAUTIFY_PROMPT="Optimize the layout for better readability"

BEAUTIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/bpmn" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"$BEAUTIFY_PROMPT\",
    \"chat_history\": [{
      \"role\": \"user\",
      \"content\": \"$BEAUTIFY_PROMPT\"
    }],
    \"existing_bpmn_xml\": $(echo "$BPMN_XML" | jq -R -s '.')
  }")

validate_response "$BEAUTIFY_RESPONSE" "Beautification"
FINAL_XML=$(echo "$BEAUTIFY_RESPONSE" | jq -r '.bpmn_xml')

# Create output directory if it doesn't exist
mkdir -p test_outputs

# Save final output
echo "$FINAL_XML" > test_outputs/final_bpmn.xml
echo "Final BPMN XML saved to test_outputs/final_bpmn.xml"
echo -e "\n=== Test Completed Successfully ==="