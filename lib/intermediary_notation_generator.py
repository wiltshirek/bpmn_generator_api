def generate_intermediary_notation(parsed_elements: dict) -> dict:
    elements = []
    sequence_flows = []
    
    def add_element(element_type, name, element_id=None, additional_attributes=None):
        if not element_id:
            element_id = f"{element_type}_{len([e for e in elements if e['type'].startswith(element_type)]) + 1}"
        element = {
            "id": element_id,
            "type": element_type,
            "name": name
        }
        if additional_attributes:
            element.update(additional_attributes)
        elements.append(element)
        return element_id

    def process_parallel_tasks(parallel_flow):
        # Create parallel gateway pair
        start_gateway_id = add_element('parallelGateway', 'Split', parallel_flow['start_gateway_id'])
        end_gateway_id = add_element('parallelGateway', 'Join', parallel_flow['end_gateway_id'])
        
        # Add sequence flows from start gateway to tasks
        for task_id in parallel_flow['parallel_tasks']:
            sequence_flows.append({
                "id": f"Flow_{len(sequence_flows) + 1}",
                "sourceRef": start_gateway_id,
                "targetRef": task_id
            })
            # Add sequence flow from task to end gateway
            sequence_flows.append({
                "id": f"Flow_{len(sequence_flows) + 1}",
                "sourceRef": task_id,
                "targetRef": end_gateway_id
            })
        
        return start_gateway_id, end_gateway_id

    # Process elements
    for element in parsed_elements['elements']:
        if element['type'] == 'subProcess':
            subprocess_id = add_element('subProcess', element['name'], element['id'])
            for nested_element in element['elements']:
                add_element(
                    nested_element['type'],
                    nested_element['name'],
                    nested_element['id'],
                    {'parent': subprocess_id}
                )
        else:
            add_element(
                element['type'],
                element['name'],
                element['id'],
                {'taskType': element.get('taskType'), 'performer': element.get('performer')}
            )

    # Process parallel flows
    for parallel_flow in parsed_elements.get('parallel_flows', []):
        process_parallel_tasks(parallel_flow)

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

