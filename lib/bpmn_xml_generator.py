from xml.dom import minidom
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from .validation import validate_intermediary_notation, validate_bpmn_xml
import re

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
        # Remove escaped quotes
        xml_str = xml_str.replace('\\"', '"')
        
        # Remove other common escape sequences
        xml_str = xml_str.replace('\\n', '')
        xml_str = xml_str.replace('\\r', '')
        xml_str = xml_str.replace('\\t', '')
        
        # Remove empty lines while preserving indentation
        lines = xml_str.split('\n')
        lines = [line for line in lines if line.strip()]
        xml_str = '\n'.join(lines)
        
        return xml_str

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
            self._create_element(element, process)

    def _create_element(self, element_data: Dict[str, Any], 
                       parent: minidom.Element, 
                       position: Optional[Position] = None) -> minidom.Element:
        element = self.doc.createElement(f"bpmn:{element_data['type']}")
        element.setAttribute('id', element_data['id'])
        element.setAttribute('name', element_data['name'])
        
        if element_data['type'] == 'subProcess':
            element.setAttribute('triggeredByEvent', 'false')
            for nested_element in element_data.get('elements', []):
                self._create_element(nested_element, element)
        elif 'taskType' in element_data:
            element.setAttribute('camunda:assignee', element_data.get('performer', ''))
        
        if 'conditions' in element_data:
            for condition in element_data['conditions']:
                condition_element = self.doc.createElement('bpmn:conditionExpression')
                condition_element.setAttribute('xsi:type', 'bpmn:tFormalExpression')
                condition_element.appendChild(self.doc.createTextNode(condition['condition']))
                element.appendChild(condition_element)
        
        if position:
            bounds = self._create_bounds(position)
            element.appendChild(bounds)
        
        parent.appendChild(element)
        return element

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
            
            if 'messageRef' in flow:
                seq_flow.setAttribute('messageRef', flow['messageRef'])
            
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
        
        for element in intermediary_notation['elements']:
            shape = self.doc.createElement('bpmndi:BPMNShape')
            shape.setAttribute('id', f"{element['id']}_di")
            shape.setAttribute('bpmnElement', element['id'])
            
            bounds = self._create_bounds(Position(x, y))
            shape.appendChild(bounds)
            plane.appendChild(shape)
            
            x += 150
        
        for flow in intermediary_notation['sequence_flows']:
            edge = self.doc.createElement('bpmndi:BPMNEdge')
            edge.setAttribute('id', f"{flow['id']}_di")
            edge.setAttribute('bpmnElement', flow['id'])
            plane.appendChild(edge)

# Create a singleton instance
_generator = BPMNXMLGenerator()

def generate_bpmn_xml(intermediary_notation: Dict[str, Any]) -> str:
    """Generate BPMN XML from intermediary notation using the singleton generator."""
    return _generator.generate_bpmn_xml(intermediary_notation)

