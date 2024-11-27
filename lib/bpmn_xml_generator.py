from typing import Dict, Any, List, Optional
from xml.dom import minidom
from dataclasses import dataclass
from core.logger import logger
from .constants import BPMN_TYPES, LAYOUT_SETTINGS
from .validation import validate_bpmn_xml
import json

@dataclass
class Position:
    x: int
    y: int

class BPMNXMLGenerator:
    def __init__(self):
        self.doc = minidom.Document()
        self.x = 100
        self.y = 100
        self.lane_height = LAYOUT_SETTINGS['lane_height']
        self._current_elements = []

    def generate_bpmn_xml(self, intermediary: dict) -> str:
        """Generate BPMN XML from intermediary notation."""
        try:
            logger.debug("Starting BPMN XML generation")
            logger.debug(f"Input intermediary notation: {json.dumps(intermediary, indent=2)}")
            
            self.doc = minidom.Document()
            self._current_elements = intermediary['elements']
            
            # Create base elements
            definitions = self._create_definitions()
            process = self._create_process(definitions, intermediary)
            
            # Create BPMN elements and flows
            self._create_all_elements(process, intermediary)
            self._create_sequence_flows(process, intermediary)
            self._create_and_append_diagram(definitions, intermediary)

            # Generate and validate XML
            xml_str = self._clean_xml_output(self.doc.toxml(encoding="UTF-8").decode('utf-8'))
            validate_bpmn_xml(xml_str)
            
            return xml_str
            
        except Exception as e:
            logger.error(f"Failed to generate BPMN XML: {str(e)}")
            raise

    def _clean_xml_output(self, xml_str: str) -> str:
        """Clean up the XML output."""
        xml_str = xml_str.replace('\\"', '"')
        xml_str = xml_str.replace('\\r', '')
        xml_str = xml_str.replace('\\t', '')
        xml_str = xml_str.replace('\\n', '')
        return ' '.join(xml_str.split())

    def _create_definitions(self) -> minidom.Element:
        """Create the base BPMN definitions element"""
        definitions = self.doc.createElement('bpmn:definitions')
        definitions.setAttribute('xmlns:bpmn', 'http://www.omg.org/spec/BPMN/20100524/MODEL')
        definitions.setAttribute('xmlns:bpmndi', 'http://www.omg.org/spec/BPMN/20100524/DI')
        definitions.setAttribute('xmlns:dc', 'http://www.omg.org/spec/DD/20100524/DC')
        definitions.setAttribute('xmlns:di', 'http://www.omg.org/spec/DD/20100524/DI')
        definitions.setAttribute('id', 'Definitions_1')
        definitions.setAttribute('targetNamespace', 'http://bpmn.io/schema/bpmn')
        self.doc.appendChild(definitions)
        return definitions

    def _create_process(self, definitions: minidom.Element, intermediary: dict) -> minidom.Element:
        """Create the main BPMN process element"""
        process = self.doc.createElement('bpmn:process')
        process.setAttribute('id', intermediary['process_id'])
        process.setAttribute('name', intermediary['process_name'])
        process.setAttribute('isExecutable', 'true')
        definitions.appendChild(process)
        return process

    def _create_all_elements(self, process: minidom.Element, intermediary: dict) -> None:
        """Create all BPMN elements"""
        for element in intermediary['elements']:
            self._create_element(process, element)

    def _create_sequence_flows(self, process: minidom.Element, intermediary: dict) -> None:
        """Create sequence flow connections"""
        for flow in intermediary['sequence_flows']:
            sequence_flow = self.doc.createElement('bpmn:sequenceFlow')
            sequence_flow.setAttribute('id', flow['id'])
            sequence_flow.setAttribute('sourceRef', flow['sourceRef'])
            sequence_flow.setAttribute('targetRef', flow['targetRef'])
            process.appendChild(sequence_flow)

    def _create_and_append_diagram(self, definitions: minidom.Element, intermediary: dict) -> None:
        """Create and append the BPMN diagram visualization"""
        diagram = self.doc.createElement('bpmndi:BPMNDiagram')
        diagram.setAttribute('id', 'BPMNDiagram_1')
        
        plane = self.doc.createElement('bpmndi:BPMNPlane')
        plane.setAttribute('id', 'BPMNPlane_1')
        plane.setAttribute('bpmnElement', intermediary['process_id'])
        
        # Create shapes for each element
        for element in intermediary['elements']:
            self._create_diagram_shape(plane, element)
        
        diagram.appendChild(plane)
        definitions.appendChild(diagram)

    def _create_element(self, process: minidom.Element, element: dict) -> minidom.Element:
        element_type = element['type']
        bpmn_element = self.doc.createElement(f'bpmn:{BPMN_TYPES[element_type]["xml_tag"]}')
        bpmn_element.setAttribute('id', element['id'])
        bpmn_element.setAttribute('name', element['name'])
        
        if element_type == 'sub_process':
            self._create_subprocess_contents(bpmn_element, element)
        
        process.appendChild(bpmn_element)
        return bpmn_element

    def _create_subprocess_contents(self, subprocess_element: minidom.Element, element: dict) -> None:
        if 'elements' in element:
            for nested_element in element['elements']:
                self._create_element(subprocess_element, nested_element)
        if 'tasks' in element:
            for task in element['tasks']:
                self._create_element(subprocess_element, task)

