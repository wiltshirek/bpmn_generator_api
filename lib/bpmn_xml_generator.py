from xml.dom import minidom
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from .validation import validate_intermediary_notation, validate_bpmn_xml
from .constants import BPMN_TYPES, LAYOUT_SETTINGS
import re
import logging
import xml.etree.ElementTree as ET
import json

logger = logging.getLogger(__name__)

@dataclass
class Position:
    x: int
    y: int

class BPMNXMLGenerator:
    def __init__(self):
        self.doc = minidom.Document()
        self.x = 100
        self.y = 100
        self.lane_height = 200

    def generate_bpmn_xml(self, intermediary: dict) -> str:
        """Generate BPMN XML from intermediary notation."""
        try:
            logger.debug("Starting BPMN XML generation")
            logger.debug(f"Input intermediary notation: {json.dumps(intermediary, indent=2)}")
            
            self.doc = minidom.Document()
            self._current_elements = intermediary['elements']
            
            logger.debug("Validating intermediary notation")
            validate_intermediary_notation(intermediary)
            
            logger.debug("Creating BPMN definitions")
            definitions = self._create_definitions()
            
            logger.debug("Creating main process")
            process = self._create_process(definitions, intermediary)
            
            logger.debug("Creating BPMN elements")
            self._create_all_elements(process, intermediary)
            
            logger.debug("Creating sequence flows")
            self._create_sequence_flows(process, intermediary)
            
            logger.debug("Creating diagram layout")
            self._create_and_append_diagram(definitions, intermediary)

            xml_str = self.doc.toxml(encoding="UTF-8").decode('utf-8')
            xml_str = xml_str.replace('\n', '').replace('\r', '')
            
            logger.debug("Validating final BPMN XML")
            validate_bpmn_xml(xml_str)
            
            logger.debug(f"Successfully generated BPMN XML (length: {len(xml_str)})")
            return xml_str
            
        except Exception as e:
            logger.error(f"Failed to generate BPMN XML: {str(e)}")
            raise

    def _clean_xml_output(self, xml_str: str) -> str:
        """Clean up the XML output by removing escape sequences and extra whitespace."""
        # First split into lines
        lines = xml_str.split('\n')
        
        # Clean each line individually
        cleaned_lines = []
        for line in lines:
            if line.strip():  # Only process non-empty lines
                # Remove escaped quotes and other escape sequences
                line = line.replace('\\"', '"')
                line = line.replace('\\r', '')
                line = line.replace('\\t', '')
                line = line.replace('\\n', '')
                cleaned_lines.append(line.strip())  # strip whitespace from each line
        
        # Join all lines into a single string with no newlines
        result = ''.join(cleaned_lines)
        
        # Log the XML string before and after cleaning
        logger.debug(f"Original XML string (first 100 chars): {xml_str[:100]}")
        logger.debug(f"Cleaned XML output (first 100 chars): {result[:100]}")
        
        return result

    def _create_definitions(self) -> minidom.Element:
        """Create and configure the BPMN definitions element."""
        definitions = self.doc.createElement('bpmn:definitions')
        namespaces = {
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'xmlns:bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'xmlns:dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'xmlns:di': 'http://www.omg.org/spec/DD/20100524/DI',
            'xmlns:camunda': 'http://camunda.org/schema/1.0/bpmn',
            'id': 'Definitions_1',
            'targetNamespace': 'http://bpmn.io/schema/bpmn'
        }
        for key, value in namespaces.items():
            definitions.setAttribute(key, value)
        self.doc.appendChild(definitions)
        return definitions

    def _create_process(self, definitions: minidom.Element, 
                       intermediary: dict) -> minidom.Element:
        process = self.doc.createElement('bpmn:process')
        process.setAttribute('id', intermediary['process_id'])
        process.setAttribute('name', intermediary['process_name'])
        process.setAttribute('isExecutable', 'true')
        definitions.appendChild(process)
        return process

    def _create_all_elements(self, process: minidom.Element,
                           intermediary: dict) -> None:
        for element in intermediary['elements']:
            self._create_element(process, element)

    def _create_element(self, parent_element: minidom.Element, element: Dict[str, Any]) -> Optional[minidom.Element]:
        """Create a BPMN element based on its type."""
        xml_type = BPMN_TYPES[element['type']]['xml_type']
        bpmn_element = self.doc.createElement(f"bpmn:{xml_type}")
        bpmn_element.setAttribute('id', element['id'])
        bpmn_element.setAttribute('name', element.get('name', ''))
        
        if element['type'] == 'subProcess':
            bpmn_element.setAttribute('triggeredByEvent', 'false')
            parent_element.appendChild(bpmn_element)
            
            # Create nested elements within the subprocess
            if 'elements' in element:
                for nested_element in element['elements']:
                    if nested_element['type'] == 'sequenceFlow':
                        # Handle sequence flows within subprocess
                        seq_flow = self.doc.createElement('bpmn:sequenceFlow')
                        seq_flow.setAttribute('id', nested_element['id'])
                        seq_flow.setAttribute('sourceRef', nested_element['sourceRef'])
                        seq_flow.setAttribute('targetRef', nested_element['targetRef'])
                        bpmn_element.appendChild(seq_flow)
                    else:
                        # Create regular nested element
                        nested_bpmn = self._create_element(bpmn_element, nested_element)
        else:
            if element.get('taskType'):
                bpmn_element.setAttribute('camunda:assignee', element.get('performer', ''))
            parent_element.appendChild(bpmn_element)
        
        return bpmn_element

    def _create_bounds(self, position: Position, element_type: str) -> minidom.Element:
        dimensions = BPMN_TYPES[element_type]['dimensions']
        bounds = self.doc.createElement('dc:Bounds')
        bounds.setAttribute('x', str(position.x))
        bounds.setAttribute('y', str(position.y))
        bounds.setAttribute('width', str(dimensions['width']))
        bounds.setAttribute('height', str(dimensions['height']))
        return bounds

    def _create_sequence_flows(self, process: minidom.Element, 
                             intermediary: dict) -> None:
        for flow in intermediary['sequence_flows']:
            seq_flow = self.doc.createElement('bpmn:sequenceFlow')
            seq_flow.setAttribute('id', flow['id'])
            seq_flow.setAttribute('sourceRef', flow['sourceRef'])
            seq_flow.setAttribute('targetRef', flow['targetRef'])
            
            if 'conditionExpression' in flow:
                condition = self.doc.createElement('bpmn:conditionExpression')
                condition.setAttribute('xsi:type', 'bpmn:tFormalExpression')
                condition_text = str(flow['conditionExpression'])
                condition.appendChild(self.doc.createTextNode(condition_text))
                seq_flow.appendChild(condition)
            
            process.appendChild(seq_flow)

    def _create_and_append_diagram(self, definitions: minidom.Element, 
                                 intermediary: dict) -> None:
        diagram = self.doc.createElement('bpmndi:BPMNDiagram')
        diagram.setAttribute('id', 'BPMNDiagram_1')
        
        plane = self.doc.createElement('bpmndi:BPMNPlane')
        plane.setAttribute('id', 'BPMNPlane_1')
        plane.setAttribute('bpmnElement', intermediary['process_id'])
        
        self._add_shapes_and_edges(plane, intermediary)
        
        diagram.appendChild(plane)
        definitions.appendChild(diagram)

    def _add_shapes_and_edges(self, plane: minidom.Element, 
                            intermediary: dict) -> None:
        x, y = 100, 100
        
        # First create all shapes
        for element in intermediary['elements']:
            shape = self._create_shape(element, x, y)
            plane.appendChild(shape)
            
            # Handle subprocess internal elements
            if element['type'] == 'subProcess' and 'elements' in element:
                subprocess_x = x + 50  # Start internal elements with offset
                subprocess_y = y + 50
                
                for internal_element in element['elements']:
                    if internal_element['type'] != 'sequenceFlow':
                        internal_shape = self._create_shape(internal_element, subprocess_x, subprocess_y)
                        plane.appendChild(internal_shape)
                        subprocess_x += 120  # Space between internal elements
            
            x += LAYOUT_SETTINGS['element_spacing']  # Increased spacing between main elements
        
        # Create edges for main sequence flows
        self._create_sequence_flow_edges(plane, intermediary['sequence_flows'], y)
        
        # Create edges for subprocess sequence flows
        for element in intermediary['elements']:
            if element['type'] == 'subProcess' and 'elements' in element:
                subprocess_flows = [e for e in element['elements'] 
                                  if e['type'] == 'sequenceFlow']
                self._create_sequence_flow_edges(plane, subprocess_flows, y + 50)

    def _create_sequence_flow_edges(self, plane: minidom.Element, 
                              flows: List[Dict[str, Any]], y: int) -> None:
        for flow in flows:
            edge = self.doc.createElement('bpmndi:BPMNEdge')
            edge.setAttribute('id', f"{flow['id']}_di")
            edge.setAttribute('bpmnElement', flow['id'])
            
            # Create waypoints
            waypoint1 = self.doc.createElement('di:waypoint')
            waypoint2 = self.doc.createElement('di:waypoint')
            
            # Calculate positions based on source and target elements
            source_x = self._get_element_x_position(flow['sourceRef'])
            target_x = self._get_element_x_position(flow['targetRef'])
            
            waypoint1.setAttribute('x', str(source_x + 100))
            waypoint1.setAttribute('y', str(y + 40))
            waypoint2.setAttribute('x', str(target_x))
            waypoint2.setAttribute('y', str(y + 40))
            
            edge.appendChild(waypoint1)
            edge.appendChild(waypoint2)
            plane.appendChild(edge)

    def _get_element_index(self, element_id: str, intermediary: dict) -> int:
        """Helper method to find the index of an element in the elements array."""
        for i, element in enumerate(intermediary['elements']):
            if element['id'] == element_id:
                return i
        return 0

    def _create_shape(self, element: Dict[str, Any], x: int, y: int) -> minidom.Element:
        """Create a BPMN shape with proper bounds."""
        shape = self.doc.createElement('bpmndi:BPMNShape')
        shape.setAttribute('id', f"{element['id']}_di")
        shape.setAttribute('bpmnElement', element['id'])
        
        if element['type'] == 'subProcess':
            shape.setAttribute('isExpanded', 'true')
        
        bounds = self._create_bounds(Position(x, y), element['type'])
        shape.appendChild(bounds)
        return shape

    def _get_element_x_position(self, element_id: str) -> int:
        """Calculate x position for an element based on its ID."""
        # Base x position
        x = self.x
        
        # Check if this is a subprocess element
        if '_substep_' in element_id:
            # Extract subprocess base position and add offset
            subprocess_id = element_id.split('_substep_')[0]
            step_number = int(element_id.split('_substep_')[1])
            return x + (step_number * 120) + 50  # 120px spacing between elements, 50px initial offset
        
        # Check if this is a start/end event in subprocess
        elif '_start' in element_id or '_end' in element_id:
            subprocess_id = element_id.split('_')[0]
            if '_end' in element_id:
                # Place end event at the right side of subprocess
                return x + 300  # Assuming subprocess width is 350
            return x + 50  # Start event offset
        
        # For main process elements
        else:
            element_index = 0
            for element in self._current_elements:
                if element['id'] == element_id:
                    break
                element_index += 1
            return x + (element_index * 200)  # 200px spacing between main elements

# Create a singleton instance
_generator = BPMNXMLGenerator()

def generate_bpmn_xml(intermediary: dict) -> str:
    """Generate BPMN XML from intermediary notation using the singleton generator."""
    return _generator.generate_bpmn_xml(intermediary)

