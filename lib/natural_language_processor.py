from typing import Dict, Any, Optional
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError
from core.config import settings
from core.logger import logger
import json
import traceback
from lib.validation import validate_intermediary_notation, ValidationError
from lib.constants import BPMN_TYPES

def build_system_prompt() -> str:
    """Build system prompt dynamically using constants."""
    # Example elements using correct ID prefixes from constants
    example_elements = [
        {
            "id": f"{BPMN_TYPES['start_event']['id_prefix']}_1",
            "type": "start_event",
            "name": "Start"
        },
        {
            "id": f"{BPMN_TYPES['exclusive_gateway']['id_prefix']}_1",
            "type": "exclusive_gateway",
            "name": "Decision"
        },
        {
            "id": f"{BPMN_TYPES['sub_process']['id_prefix']}_1",
            "type": "sub_process",
            "name": "Document Verification",
            "elements": [
                {
                    "id": f"{BPMN_TYPES['user_task']['id_prefix']}_1",
                    "type": "user_task",
                    "name": "Verify Document"
                }
            ]
        }
    ]

    example_json = {
        "process_id": "Process_1",
        "process_name": "Business Process",
        "elements": example_elements,
        "sequence_flows": [
            {
                "id": "Flow_1",
                "sourceRef": "string",
                "targetRef": "string"
            }
        ]
    }

    return f"""You are a BPMN expert. Convert business process descriptions into JSON format.
    You must ALWAYS respond with valid JSON only, no other text.
    The JSON must follow this structure:
    {json.dumps(example_json, indent=2)}
    
    Valid element types are: {', '.join(BPMN_TYPES.keys())}
    Note: sub_process elements MUST contain an 'elements' array with at least one task."""

def process_text(description: str) -> Dict[str, Any]:
    """Process natural language input using OpenAI's GPT model."""
    try:
        # Input validation
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Description must be a non-empty string")
            
        # API call
        response: ChatCompletion = settings.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": description.strip()}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Get response content
        if not response.choices or not response.choices[0].message:
            logger.error("No valid response from OpenAI")
            raise ValueError("No valid response received from OpenAI")
            
        result = response.choices[0].message.content.strip()
        if not result:
            logger.error("Empty response content from OpenAI")
            raise ValueError("Empty response from OpenAI")
            
        logger.debug(f"OpenAI Response: {result}")
            
        # Parse and validate JSON
        try:
            parsed_elements = json.loads(result)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Raw content that failed parsing: {result}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during JSON parsing: {str(e)}")
            logger.error(f"Raw content that failed parsing: {result}")
            logger.error("Full traceback:", exc_info=True)
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
            
        # Validate the structure
        validate_intermediary_notation(parsed_elements)
        return parsed_elements
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}", exc_info=True)
        raise

