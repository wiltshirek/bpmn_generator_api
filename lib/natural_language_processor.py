from typing import Dict
import openai
from core.config import settings
from core.logger import logger
import json
import traceback

def process_text(text: str) -> dict:
    """
    Process natural language text into structured BPMN elements
    """
    try:
        logger.info("Starting natural language processing")
        openai.api_key = settings.OPENAI_API_KEY

        prompt = """You are a BPMN expert. Convert this business process description into a structured JSON format.
        Follow these rules strictly:
        1. Always include process_id and process_name
        2. Always include elements array with at least start and end events
        3. Each task must have type, id, and name
        4. Include sequence flows connecting all elements
        5. Use proper BPMN types: startEvent, endEvent, userTask, serviceTask, manualTask, exclusiveGateway

        Required JSON structure:
        {
            "process_id": "Process_1",
            "process_name": "Business Process Name",
            "elements": [
                {
                    "id": "StartEvent_1",
                    "type": "startEvent",
                    "name": "Start"
                },
                {
                    "id": "Task_1",
                    "type": "userTask",
                    "name": "Submit Order",
                    "performer": "Customer"
                }
            ],
            "sequence_flows": [
                {
                    "id": "Flow_1",
                    "sourceRef": "StartEvent_1",
                    "targetRef": "Task_1"
                }
            ]
        }

        Convert the following process description to this exact JSON structure:"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2000
        )
        
        result = response.choices[0].message['content']
        logger.debug(f"OpenAI response: {result}")
        
        # Parse and validate the response
        try:
            parsed_elements = json.loads(result)
            required_keys = ['process_id', 'process_name', 'elements', 'sequence_flows']
            if not all(key in parsed_elements for key in required_keys):
                raise ValueError("Missing required keys in OpenAI response")
            return parsed_elements
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from OpenAI")
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise Exception(f"Error in NLP processing: {str(e)}")

