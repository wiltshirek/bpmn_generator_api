from .constants import BPMN_TYPES, BPMN_TYPE_VARIANTS

def generate_intermediary_notation(nlp_output: dict) -> dict:
    """Convert NLP output into a structured intermediary notation."""
    intermediary = {
        "process_id": nlp_output.get("process_id", "Process_1"),
        "process_name": nlp_output.get("process_name", "Business Process"),
        "elements": [],
        "sequence_flows": []
    }
    
    element_counts = {}
    
    try:
        for element in nlp_output.get("elements", []):
            element_type = element["type"]
            
            # Convert any variant to canonical snake_case type
            if element_type not in BPMN_TYPE_VARIANTS:
                raise ValueError(f"Invalid element type: {element_type}")
            
            canonical_type = BPMN_TYPE_VARIANTS[element_type]
            element_counts[canonical_type] = element_counts.get(canonical_type, 0) + 1
            
            node = {
                "id": f"{BPMN_TYPES[canonical_type]['id_prefix']}_{element_counts[canonical_type]}",
                "type": canonical_type,
                "name": element.get("name", f"{canonical_type}_{element_counts[canonical_type]}")
            }
            
            # Handle subprocess elements
            if canonical_type == 'sub_process' and 'elements' in element:
                node['elements'] = []
                for sub_element in element['elements']:
                    sub_type = BPMN_TYPE_VARIANTS[sub_element['type']]
                    element_counts[sub_type] = element_counts.get(sub_type, 0) + 1
                    sub_node = {
                        "id": f"{BPMN_TYPES[sub_type]['id_prefix']}_{element_counts[sub_type]}",
                        "type": sub_type,
                        "name": sub_element.get("name", f"{sub_type}_{element_counts[sub_type]}")
                    }
                    node['elements'].append(sub_node)
            
            intermediary["elements"].append(node)
            
    except Exception as e:
        logger.error(f"Error in generate_intermediary_notation: {str(e)}")
        raise
    
    # Convert sequence flows with proper IDs
    for i, flow in enumerate(nlp_output.get("sequence_flows", []), 1):
        edge = {
            "id": f"Flow_{i}",
            "sourceRef": flow.get("sourceRef", flow.get("from")),
            "targetRef": flow.get("targetRef", flow.get("to"))
        }
        intermediary["sequence_flows"].append(edge)
    
    return intermediary

