from typing import Dict, Any, List
from xml.dom import minidom
from core.logger import logger
from .constants import BPMN_TYPES, GATEWAY_PAIRS
from .exceptions import ValidationError

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
    required_fields = ['process_id', 'process_name', 'elements', 'sequence_flows']
    if not all(key in notation for key in required_keys):
        missing_keys = [key for key in required_keys if key not in notation]
        raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")
    
    # Validate gateway pairs
    validate_gateway_pairs(notation['elements'])



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


def validate_gateway_pairs(elements: List[Dict[str, Any]]) -> None:
    """Validate that gateway pairs are properly matched"""
    gateway_stack = []
    
    for element in elements:
        if element['type'] in GATEWAY_PAIRS:
            if GATEWAY_PAIRS[element['type']] == 'start':
                gateway_stack.append(element)
            elif GATEWAY_PAIRS[element['type']] == 'end':
                if not gateway_stack:
                    raise ValidationError(f"Found end gateway '{element['id']}' without matching start gateway")
                gateway_stack.pop()
    
    if gateway_stack:
        unmatched = [g['id'] for g in gateway_stack]
        raise ValidationError(f"Unmatched start gateways: {', '.join(unmatched)}")
