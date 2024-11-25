def generate_intermediary_notation(parsed_elements: dict) -> dict:
    elements = []
    sequence_flows = []
    
    def process_element(element: dict) -> dict:
        """Recursively process elements and their substeps"""
        if element['type'] == 'subProcess':
            subprocess_element = {
                "id": element['id'],
                "type": "subProcess",
                "name": element['name'],
                "isExpanded": False,
                "elements": []
            }
            
            if 'substeps' in element:
                # Add start event
                start_id = f"{element['id']}_start"
                subprocess_element['elements'].append({
                    "id": start_id,
                    "type": "startEvent",
                    "name": "Start"
                })
                
                prev_id = start_id
                for idx, substep in enumerate(element['substeps']):
                    # Recursively process substep in case it has its own substeps
                    substep_id = f"{element['id']}_substep_{idx}"
                    substep['id'] = substep_id  # Set the ID before processing
                    processed_substep = process_element(substep)  # Recursive call
                    subprocess_element['elements'].append(processed_substep)
                    
                    # Create sequence flow
                    subprocess_element['elements'].append({
                        "id": f"{element['id']}_flow_{idx}",
                        "type": "sequenceFlow",
                        "sourceRef": prev_id,
                        "targetRef": substep_id
                    })
                    prev_id = substep_id
                
                # Add end event and final flow
                end_id = f"{element['id']}_end"
                subprocess_element['elements'].append({
                    "id": end_id,
                    "type": "endEvent",
                    "name": "End"
                })
                subprocess_element['elements'].append({
                    "id": f"{element['id']}_flow_end",
                    "type": "sequenceFlow",
                    "sourceRef": prev_id,
                    "targetRef": end_id
                })
            
            return subprocess_element
        else:
            return {
                "id": element['id'],
                "type": element['type'],
                "name": element['name'],
                "taskType": element.get('taskType'),
                "performer": element.get('performer')
            }

    # Process all top-level elements
    for element in parsed_elements['elements']:
        elements.append(process_element(element))

    # Process sequence flows
    for flow in parsed_elements['sequence_flows']:
        sequence_flows.append({
            "id": flow['id'],
            "sourceRef": flow['sourceRef'],
            "targetRef": flow['targetRef'],
            "conditionExpression": flow.get('conditionExpression')
        })

    return {
        "process_id": parsed_elements['process_id'],
        "process_name": parsed_elements['process_name'],
        "elements": elements,
        "sequence_flows": sequence_flows
    }

