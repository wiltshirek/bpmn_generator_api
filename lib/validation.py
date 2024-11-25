from typing import Dict, Any
from dataclasses import dataclass
from xml.dom import minidom
import json

@dataclass
class ValidationError(Exception):
    message: str
    details: Dict[str, Any] = None

def validate_intermediary_notation(notation: Dict[str, Any]) -> None:
    """Validate the intermediary notation structure."""
    required_keys = ['process_id', 'process_name', 'elements', 'sequence_flows']
    
    if not all(key in notation for key in required_keys):
        missing_keys = [key for key in required_keys if key not in notation]
        raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")
    
    if not notation['elements']:
        raise ValidationError("Elements array cannot be empty")
    
    def validate_element(element):
        if 'type' not in element:
            raise ValidationError(f"Missing type in element: {element}")
        if element['type'] == 'subProcess':
            if element.get('isExpanded', True) and 'elements' not in element:
                raise ValidationError(f"Expanded subprocess missing elements array: {element}")
            if 'elements' in element:
                for nested_element in element['elements']:
                    validate_element(nested_element)
    
    # Validate all elements including nested ones
    for element in notation['elements']:
        validate_element(element)

def validate_bpmn_xml(xml_str: str) -> None:
    """Validate the generated BPMN XML."""
    try:

        # Parse and validate the cleaned XML
        doc = minidom.parseString(xml_str)
        required_elements = [
            'bpmn:definitions',
            'bpmn:process',
            'bpmndi:BPMNDiagram',
            'bpmndi:BPMNPlane'
        ]
        
        for element in required_elements:
            if not doc.getElementsByTagName(element):
                raise ValidationError(f"Missing required element: {element}")
    except Exception as e:
        raise ValidationError(f"Invalid BPMN XML: {str(e)}") 

def validate_element(element: Dict[str, Any]) -> None:
    """Validate a single BPMN element."""
    required_fields = ['id', 'type', 'name']
    for field in required_fields:
        if field not in element:
            raise ValidationError(f"Missing required field {field} in element: {element}")