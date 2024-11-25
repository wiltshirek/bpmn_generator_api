def generate_intermediary_notation(parsed_elements: dict) -> dict:
    elements = []
    sequence_flows = []
    
    def add_element(type_name: str, name: str, element_id: str, additional_props: dict = None) -> str:
        element = {
            "id": element_id,
            "type": type_name,
            "name": name
        }
        if additional_props:
            element.update(additional_props)
        elements.append(element)
        return element_id

    # Process elements
    for element in parsed_elements['elements']:
        if element['type'] == 'subProcess':
            # Keep as subProcess but mark as collapsed
            add_element('subProcess', element['name'], element['id'], {
                'isExpanded': False
            })
        else:
            add_element(
                element['type'],
                element['name'],
                element['id'],
                {'taskType': element.get('taskType'), 'performer': element.get('performer')}
            )

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

