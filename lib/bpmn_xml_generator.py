from xml.dom import minidom
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from .validation import validate_intermediary_notation, validate_bpmn_xml
import re
import logging

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

    def generate_bpmn_xml(self, intermediary_notation: Dict[str, Any]) -> str:
        """Generate BPMN XML from intermediary notation."""
        try:
            # Create a new document instance for each generation
            self.doc = minidom.Document()
            # Store current elements for position calculations
            self._current_elements = intermediary_notation['elements']
            
            validate_intermediary_notation(intermediary_notation)
            
            definitions = self._create_definitions()
            process = self._create_process(definitions, intermediary_notation)
            self._create_all_elements(process, intermediary_notation)
            self._create_sequence_flows(process, intermediary_notation)
            self._create_and_append_diagram(definitions, intermediary_notation)

            # Generate XML with proper indentation
            xml_str = self.doc.toprettyxml(indent="  ", encoding="UTF-8")
            xml_str = xml_str.decode('utf-8')
            
            # Clean up the XML string
            xml_str = self._clean_xml_output(xml_str)
            
            validate_bpmn_xml(xml_str)
            
            return xml_str
            
        except Exception as e:
            raise Exception(f"Failed to generate BPMN XML: {str(e)}")

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
                       intermediary_notation: Dict[str, Any]) -> minidom.Element:
        process = self.doc.createElement('bpmn:process')
        process.setAttribute('id', intermediary_notation['process_id'])
        process.setAttribute('name', intermediary_notation['process_name'])
        process.setAttribute('isExecutable', 'true')
        definitions.appendChild(process)
        return process

    def _create_all_elements(self, process: minidom.Element,
                           intermediary_notation: Dict[str, Any]) -> None:
        for element in intermediary_notation['elements']:
            self._create_element(process, element)

    def _create_element(self, parent_element: minidom.Element, element: Dict[str, Any]) -> Optional[minidom.Element]:
        """Create a BPMN element based on its type."""
        bpmn_element = self.doc.createElement(f"bpmn:{element['type']}")
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

    def _create_bounds(self, position: Position) -> minidom.Element:
        bounds = self.doc.createElement('dc:Bounds')
        bounds.setAttribute('x', str(position.x))
        bounds.setAttribute('y', str(position.y))
        bounds.setAttribute('width', '100')
        bounds.setAttribute('height', '80')
        return bounds

    def _create_sequence_flows(self, process: minidom.Element, 
                             intermediary_notation: Dict[str, Any]) -> None:
        for flow in intermediary_notation['sequence_flows']:
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
                                 intermediary_notation: Dict[str, Any]) -> None:
        diagram = self.doc.createElement('bpmndi:BPMNDiagram')
        diagram.setAttribute('id', 'BPMNDiagram_1')
        
        plane = self.doc.createElement('bpmndi:BPMNPlane')
        plane.setAttribute('id', 'BPMNPlane_1')
        plane.setAttribute('bpmnElement', intermediary_notation['process_id'])
        
        self._add_shapes_and_edges(plane, intermediary_notation)
        
        diagram.appendChild(plane)
        definitions.appendChild(diagram)

    def _add_shapes_and_edges(self, plane: minidom.Element, 
                            intermediary_notation: Dict[str, Any]) -> None:
        x, y = 100, 100
        
        # First create all shapes
        for element in intermediary_notation['elements']:
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
            
            x += 200  # Increased spacing between main elements
        
        # Create edges for main sequence flows
        self._create_sequence_flow_edges(plane, intermediary_notation['sequence_flows'], y)
        
        # Create edges for subprocess sequence flows
        for element in intermediary_notation['elements']:
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

    def _get_element_index(self, element_id: str, intermediary_notation: Dict[str, Any]) -> int:
        """Helper method to find the index of an element in the elements array."""
        for i, element in enumerate(intermediary_notation['elements']):
            if element['id'] == element_id:
                return i
        return 0

    def _create_shape(self, element: Dict[str, Any], x: int, y: int) -> minidom.Element:
        """Create a BPMN shape with proper bounds."""
        shape = self.doc.createElement('bpmndi:BPMNShape')
        shape.setAttribute('id', f"{element['id']}_di")
        shape.setAttribute('bpmnElement', element['id'])
        
        if element['type'] == 'subProcess':
            # Set expanded state in the diagram
            shape.setAttribute('isExpanded', 'true')
            
            # Create larger bounds for subprocess
            bounds = self.doc.createElement('dc:Bounds')
            bounds.setAttribute('x', str(x))
            bounds.setAttribute('y', str(y))
            bounds.setAttribute('width', '350')  # Wider to accommodate internal elements
            bounds.setAttribute('height', '200')  # Taller to accommodate internal elements
        else:
            bounds = self.doc.createElement('dc:Bounds')
            bounds.setAttribute('x', str(x))
            bounds.setAttribute('y', str(y))
            bounds.setAttribute('width', '100')
            bounds.setAttribute('height', '80')
        
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

def generate_bpmn_xml(intermediary_notation: Dict[str, Any]) -> str:
    """Generate BPMN XML from intermediary notation using the singleton generator."""
    return _generator.generate_bpmn_xml(intermediary_notation)

