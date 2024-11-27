from typing import Dict, Any
from core.logger import logger
from .validation import validate_intermediary_notation
import json

def generate_intermediary_notation(nlp_result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert NLP output into intermediary BPMN notation"""
    try:
        logger.debug("Generating intermediary notation")
        logger.debug(f"Input NLP result: {json.dumps(nlp_result, indent=2)}")
        
        # Validate and return the NLP result as-is since it should already be in correct format
        validate_intermediary_notation(nlp_result)
        return nlp_result
        
    except Exception as e:
        logger.error(f"Failed to generate intermediary notation: {str(e)}")
        raise

