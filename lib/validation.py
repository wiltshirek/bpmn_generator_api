from typing import Dict, Any
from dataclasses import dataclass
from xml.dom import minidom
import json
from .constants import BPMN_TYPES

@dataclass
class ValidationError(Exception):
    message: str
    details: Dict[str, Any] = None

def validate_element(element: Dict[str, Any]) -> None:
    """Validate a single BPMN element."""
    required_fields = ['id', 'type', 'name']
    if not all(field in element for field in required_fields):
        raise ValidationError(f"Element missing required fields: {element}")
    
    element_type = element['type']
    if element_type not in BPMN_TYPES:
        raise ValidationError(f"Invalid element type: {element_type}")
    
    expected_prefix = BPMN_TYPES[element_type]['id_prefix']
    if not element['id'].startswith(f"{expected_prefix}_"):
        raise ValidationError(f"Invalid ID format: {element['id']}")
    
    # Validate subprocess structure
    if element['type'] == 'sub_process':
        if not ('elements' in element or 'tasks' in element):
            raise ValidationError(
                f"Subprocess '{element.get('name', 'Unknown')}' (ID: {element['id']}) "
                "must contain either 'elements' or 'tasks' array"
            )
        
        if 'elements' in element and not element['elements']:
            raise ValidationError(
                f"Subprocess '{element.get('name', 'Unknown')}' (ID: {element['id']}) "
                "contains empty elements array"
            )
        
        if 'tasks' in element and not element['tasks']:
            raise ValidationError(
                f"Subprocess '{element.get('name', 'Unknown')}' (ID: {element['id']}) "
                "contains empty tasks array"
            )
        
        if 'elements' in element:
            for nested_element in element['elements']:
                validate_element(nested_element)
        if 'tasks' in element:
            for task in element['tasks']:
                validate_element(task)

def validate_sequence_flow(flow: Dict[str, Any]) -> None:
    """Validate a sequence flow."""
    required_fields = ['id', 'sourceRef', 'targetRef']
    if not all(field in flow for field in required_fields):
        raise ValidationError(f"Sequence flow missing required fields: {flow}")
    
    # Validate flow ID format
    if not flow['id'].startswith('Flow_'):
        raise ValidationError(f"Invalid flow ID format: {flow['id']}")

def validate_intermediary_notation(notation: Dict[str, Any]) -> None:
    """Validate the intermediary notation structure."""
    required_keys = ['process_id', 'process_name', 'elements', 'sequence_flows']
    
    if not all(key in notation for key in required_keys):
        missing_keys = [key for key in required_keys if key not in notation]
        raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")
    
    if not notation['elements']:
        raise ValidationError("Elements array cannot be empty")
    
    # Validate all elements
    for element in notation['elements']:
        validate_element(element)
    
    # Validate sequence flows
    for flow in notation['sequence_flows']:
        validate_sequence_flow(flow)
    
    # Verify start and end events exist using snake_case
    has_start = any(e['type'] == 'start_event' for e in notation['elements'])
    has_end = any(e['type'] == 'end_event' for e in notation['elements'])
    if not (has_start and has_end):
        raise ValidationError("Missing start_event or end_event in elements")

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

def validate_json_structure(parsed_elements: Dict[str, Any]) -> None:
    """Validates the JSON structure meets all BPMN requirements."""
    required_keys = ['process_id', 'process_name', 'elements', 'sequence_flows']
    if not all(key in parsed_elements for key in required_keys):
        raise ValueError("Missing required keys in OpenAI response")
    
    # Validate elements array has start and end events
    elements = parsed_elements['elements']
    has_start = any(e.get('type') == 'start_event' for e in elements)
    has_end = any(e.get('type') == 'end_event' for e in elements)
    if not (has_start and has_end):
        raise ValueError("Missing start_event or end_event in elements")
    
    # Validate element structure
    for element in elements:
        if not all(key in element for key in ['id', 'type', 'name']):
            raise ValueError(f"Element missing required fields: {element}")
    
    # Validate sequence flows
    for flow in parsed_elements['sequence_flows']:
        if not all(key in flow for key in ['id', 'sourceRef', 'targetRef']):
            raise ValueError(f"Sequence flow missing required fields: {flow}")