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
    
    element_ids = set()
    for element in notation['elements']:
        if not all(key in element for key in ['id', 'type', 'name']):
            raise ValidationError(f"Invalid element structure: {json.dumps(element)}")
        if element['id'] in element_ids:
            raise ValidationError(f"Duplicate element ID: {element['id']}")
        element_ids.add(element['id'])
    
    for flow in notation['sequence_flows']:
        if not all(key in flow for key in ['id', 'sourceRef', 'targetRef']):
            raise ValidationError(f"Invalid flow structure: {json.dumps(flow)}")
        if flow['sourceRef'] not in element_ids:
            raise ValidationError(f"Invalid sourceRef: {flow['sourceRef']}")
        if flow['targetRef'] not in element_ids:
            raise ValidationError(f"Invalid targetRef: {flow['targetRef']}")

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