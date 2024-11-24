import xml.etree.ElementTree as ET
import uuid
import re
from typing import Dict, List

def create_subprocess_element(process: ET.Element, subprocess_data: Dict, elements: List[Dict], flows: List[Dict]) -> ET.Element:
    subprocess = ET.SubElement(process, "bpmn:subProcess", {
        "id": subprocess_data["subprocess_id"],
        "name": subprocess_data["name"]
    })
    
    # Create subprocess elements
    subprocess_elements = [e for e in elements if e.get("subprocess_id") == subprocess_data["subprocess_id"]]
    subprocess_flows = [f for f in flows if f.get("subprocess_id") == subprocess_data["subprocess_id"]]
    
    # Add elements to subprocess
    element_map = {}
    for element in subprocess_elements:
        if element["type"] == "task":
            task = ET.SubElement(subprocess, f"bpmn:{element['taskType']}Task", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
        elif element["type"] == "event":
            event_type = "startEvent" if element["name"] == "Start" else "endEvent"
            event = ET.SubElement(subprocess, f"bpmn:{event_type}", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
        elif "Gateway" in element["type"]:
            gateway = ET.SubElement(subprocess, f"bpmn:{element['type']}", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
    
    # Add flows to subprocess
    for flow in subprocess_flows:
        sequence_flow = ET.SubElement(subprocess, "bpmn:sequenceFlow", {
            "id": f"Flow_{str(uuid.uuid4())}",
            "sourceRef": element_map[flow["source"]],
            "targetRef": element_map[flow["target"]]
        })
        if flow["condition"]:
            condition_expression = ET.SubElement(sequence_flow, "bpmn:conditionExpression")
            condition_expression.text = flow["condition"]
    
    return subprocess

def generate_bpmn_xml(intermediary_notation: dict) -> str:
    # Register namespaces
    ET.register_namespace('bpmn', "http://www.omg.org/spec/BPMN/20100524/MODEL")
    ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
    ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
    ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")
    
    # Create XML declaration and root element
    root = ET.Element("{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions", {
        "xmlns:bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
        "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
        "xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
        "xmlns:di": "http://www.omg.org/spec/DD/20100524/DI",
        "targetNamespace": "http://bpmn.io/schema/bpmn",
        "id": f"Definitions_{str(uuid.uuid4())}"
    })
    
    # Create document tree
    tree = ET.ElementTree(root)
    
    process = ET.SubElement(tree.getroot(), "bpmn:process", {"id": f"Process_{str(uuid.uuid4())}"})
    
    # Initialize global element map
    element_map = {}
    
    # Create all elements first to build complete element map
    for element in intermediary_notation["elements"]:
        if element["type"] == "task":
            task = ET.SubElement(process, f"bpmn:{element['taskType']}Task", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
        elif element["type"] == "event":
            event_type = "startEvent" if element["name"] == "Start" else "endEvent"
            event = ET.SubElement(process, f"bpmn:{event_type}", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
        elif "Gateway" in element["type"]:
            gateway = ET.SubElement(process, f"bpmn:{element['type']}", {
                "id": element["id"],
                "name": element["name"]
            })
            element_map[element["name"]] = element["id"]
    
    # Create subprocesses
    subprocess_ids = set(e.get("subprocess_id") for e in intermediary_notation["elements"] if e.get("subprocess_id"))
    for subprocess_id in subprocess_ids:
        subprocess_data = {
            "subprocess_id": subprocess_id,
            "name": next(e["name"] for e in intermediary_notation["elements"] 
                        if e.get("subprocess_id") == subprocess_id and '[sub]' in e["name"])
        }
        create_subprocess_element(process, subprocess_data, 
                                intermediary_notation["elements"],
                                intermediary_notation["flows"])
    
    # Add sequence flows for main process
    main_flows = [f for f in intermediary_notation["flows"] if not f.get("subprocess_id")]
    for flow in main_flows:
        sequence_flow = ET.SubElement(process, "bpmn:sequenceFlow", {
            "id": f"Flow_{str(uuid.uuid4())}",
            "sourceRef": element_map[flow["source"]],
            "targetRef": element_map[flow["target"]]
        })
        if flow["condition"]:
            condition_expression = ET.SubElement(sequence_flow, "bpmn:conditionExpression")
            condition_expression.text = flow["condition"]

    # Add BPMNDiagram element
    bpmn_diagram = ET.SubElement(tree.getroot(), "bpmndi:BPMNDiagram", {
        "id": f"BPMNDiagram_{str(uuid.uuid4())}"
    })
    bpmn_plane = ET.SubElement(bpmn_diagram, "bpmndi:BPMNPlane", {
        "id": f"BPMNPlane_{str(uuid.uuid4())}",
        "bpmnElement": process.get("id")
    })

    def clean_xml(xml_string):
        xml_string = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', xml_string)
        return xml_string.strip()

    # Return properly formatted XML
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree.getroot(), encoding='unicode')