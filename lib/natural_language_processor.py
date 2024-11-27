from typing import Dict, Any
from core.config import settings
from core.logger import logger
import json

def build_system_prompt() -> str:
    return """You are a BPMN process modeling expert. Convert natural language descriptions into structured process definitions.
    Output must be valid JSON only, no other text.
    The JSON must follow this structure:
    {
        "process_id": "unique_process_id",
        "process_name": "descriptive name",
        "elements": [
            {
                "id": "unique_element_id",
                "type": "start_event|end_event|user_task|service_task|exclusive_gateway|parallel_gateway|sub_process",
                "name": "element name"
            }
        ],
        "sequence_flows": [
            {
                "id": "Flow_id",
                "sourceRef": "source_element_id",
                "targetRef": "target_element_id"
            }
        ]
    }"""

def process_text(prompt: str) -> Dict[str, Any]:
    """Process natural language input into structured format"""
    try:
        logger.debug("Processing text with NLP")
        logger.debug(f"Input prompt: {prompt}")
        
        response = settings.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.debug(f"NLP Result: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process text: {str(e)}")
        raise

def process_layout_update(prompt: str, existing_bpmn: str, chat_history: list) -> Dict[str, Any]:
    """Process layout update requests"""
    system_message = """You are a BPMN XML layout expert. Your task is to modify the given BPMN XML based on the user's layout adjustment requests.
    
    You must ALWAYS respond with valid JSON only, no other text or explanations.
    The JSON response must follow this exact structure:
    {
        "modified_bpmn": "the complete modified BPMN XML string",
        "changes_made": ["list of specific coordinate changes made"],
        "layout_principles_applied": ["list of layout principles that were applied"],
        "validation_status": "success|failure",
        "validation_messages": ["any validation messages or warnings"]
    }
    
    Follow these layout principles:
    1. Maintain a primarily horizontal flow from left to right
    2. Prevent any element overlaps
    3. Subprocess Layout guidelines
    4. Connection Rules
    5. General Guidelines
    
    Only modify x and y coordinate attributes.
    Do not change any process logic, flows, or connections."""

    try:
        logger.debug("Processing layout update")
        response = settings.openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_message},
                *[{"role": m.role, "content": m.content} for m in chat_history],
                {"role": "user", "content": f"Current BPMN XML:\n{existing_bpmn}\n\nLayout request:\n{prompt}"}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.debug(f"Layout Update Result: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process layout update: {str(e)}")
        raise

