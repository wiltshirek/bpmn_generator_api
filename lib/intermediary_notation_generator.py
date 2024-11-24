import uuid
from typing import Dict, List
import re

def parse_actors(actors_line: str) -> List[str]:
    return [actor.strip() for actor in actors_line.split(':')[1].split(',')]

def parse_parallel_activities(activities: str) -> List[str]:
    return [act.strip() for act in activities.split('||')]

def parse_subprocess(subprocess_str: str) -> Dict:
    """Parse subprocess definition and clean names"""
    try:
        # Remove any actor annotations in parentheses
        subprocess_str = re.sub(r'\([^)]*\)', '', subprocess_str)
        
        # Split on colon if present
        if ':' in subprocess_str:
            name_part, flow_part = subprocess_str.split(':', 1)
            name = clean_element_name(name_part.replace('[sub]', '').strip())
            flow = flow_part.strip()
        else:
            name = clean_element_name(subprocess_str.replace('[sub]', '').strip())
            flow = ""
        
        return {
            "name": name,
            "flow": flow,
            "id": str(uuid.uuid4())
        }
    except Exception as e:
        logger.error(f"Error parsing subprocess: {subprocess_str}")
        raise

def clean_element_name(name: str) -> str:
    """Remove special characters and standardize element names"""
    # Keep alphanumeric and underscore, convert to camelCase
    cleaned = ''.join(c for c in name if c.isalnum() or c == '_')
    # Preserve XOR, AND, OR prefixes and Start/End
    if any(prefix in name for prefix in ['XOR', 'AND', 'OR']) or name in ['Start', 'End']:
        return name
    return cleaned

def parse_element_name(element: str) -> tuple:
    """Parse element name and task type from string like 'SubmitOrder(service)'"""
    # Handle subprocess references
    if '[sub]' in element:
        subprocess_data = parse_subprocess(element)
        return subprocess_data["name"], None
        
    element_name = element
    task_type = 'user'  # default
    
    if '(' in element and ')' in element:
        # Check if it's a task type (at the end)
        if element.endswith(')'):
            name_part = element[:element.rindex('(')]
            type_part = element[element.rindex('(')+1:-1]
            element_name = clean_element_name(name_part)
            task_type = type_part.strip()
        else:
            # It's a condition, just clean the name
            element_name = clean_element_name(element[:element.index('(')])
    else:
        element_name = clean_element_name(element)
    
    return element_name, task_type

def parse_flow(flow: str, parent_id: str = None) -> List[Dict]:
    elements = flow.split('->')
    parsed_flow = []
    current_subprocess = None
    
    for i in range(len(elements) - 1):
        source = elements[i].strip()
        target = elements[i + 1].strip()
        
        # Handle subprocess
        if '[sub]' in source:
            current_subprocess = parse_subprocess(source)
            source = current_subprocess["name"]
        
        # Clean names and extract conditions/task types
        source_name, _ = parse_element_name(source)
        target_name, _ = parse_element_name(target)
        
        # Extract condition if present
        condition = None
        if '(' in source and ')' in source and not source.endswith(')'):
            condition_start = source.find('(')
            condition_end = source.find(')')
            condition = source[condition_start + 1:condition_end]
            source_name = clean_element_name(source[:condition_start])
        
        parsed_flow.append({
            "source": source_name,
            "target": target_name,
            "subprocess_id": current_subprocess["id"] if current_subprocess else parent_id,
            "condition": condition
        })
    
    return parsed_flow

def parse_actor_mapping(mapping: str) -> Dict[str, List[str]]:
    actor_map = {}
    for line in mapping.split('\n'):
        if ':' in line:
            actor, activities = line.split(':')
            activities = activities.strip()[1:-1].split(',')
            actor_map[actor.strip()] = [act.strip() for act in activities]
    return actor_map

def generate_intermediary_notation(nlp_output: str) -> Dict:
    lines = nlp_output.split('\n')
    actors_line = next(line for line in lines if line.startswith('Actors:'))
    actors = parse_actors(actors_line)
    
    # Find main flow and subprocesses
    flows = []
    current_flow = []
    subprocess_flows = []
    
    for line in lines:
        if '->' in line:
            if line.strip().startswith(' '):  # Subprocess
                subprocess_flows.append(line.strip())
            else:  # Main flow
                current_flow.append(line.strip())
    
    main_flow = ' '.join(current_flow)
    parsed_flows = parse_flow(main_flow)
    
    # Find actor mapping
    mapping_start = next(i for i, line in enumerate(lines) if ':' in line and '->' not in line)
    actor_mapping = '\n'.join(lines[mapping_start:])
    actor_map = parse_actor_mapping(actor_mapping)
    
    # Generate elements list
    elements = []
    element_names = set()
    
    # First pass: collect all elements including subprocesses
    for flow in parsed_flows:
        for element in [flow['source'], flow['target']]:
            if element not in element_names:
                element_names.add(element)
                element_type = 'task'
                task_type = 'user'  # default
                
                element_name, parsed_task_type = parse_element_name(element)
                
                if '[sub]' in element:
                    element_type = 'subprocess'
                    subprocess_data = parse_subprocess(element)
                    elements.append({
                        "id": subprocess_data["id"],
                        "name": subprocess_data["name"],
                        "type": element_type,
                        "taskType": None,
                        "subprocess_id": None
                    })
                    continue
                
                if element.startswith('XOR'):
                    element_type = 'exclusiveGateway'
                elif element.startswith('AND'):
                    element_type = 'parallelGateway'
                elif element.startswith('OR'):
                    element_type = 'inclusiveGateway'
                elif element in ['Start', 'End']:
                    element_type = 'event'
                else:
                    task_type = parsed_task_type
                
                elements.append({
                    "id": str(uuid.uuid4()),
                    "name": element_name,
                    "type": element_type,
                    "taskType": task_type if element_type == 'task' else None,
                    "subprocess_id": flow.get('subprocess_id')
                })
    
    # Parse subprocess flows
    for subprocess_flow in subprocess_flows:
        if ':' in subprocess_flow:
            subprocess_name = subprocess_flow.split(':')[0].strip()
            subprocess_id = next(e["id"] for e in elements 
                               if e["type"] == "subprocess" 
                               and e["name"] == clean_element_name(subprocess_name.replace('[sub]', '')))
            sub_flows = parse_flow(subprocess_flow.split(':', 1)[1], subprocess_id)
            parsed_flows.extend(sub_flows)
    
    return {
        "actors": actors,
        "elements": elements,
        "flows": parsed_flows,
        "actorMapping": actor_map
    }