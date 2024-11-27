# Single source of truth for BPMN types
BPMN_TYPES = {
    'start_event': {
        'xml_type': 'startEvent',  # Only used when generating XML
        'id_prefix': 'StartEvent',
        'dimensions': {'width': 36, 'height': 36}
    },
    'end_event': {
        'xml_type': 'endEvent',
        'id_prefix': 'EndEvent',
        'dimensions': {'width': 36, 'height': 36}
    },
    'user_task': {
        'xml_type': 'userTask',
        'id_prefix': 'Task',
        'dimensions': {'width': 100, 'height': 80}
    },
    'service_task': {
        'xml_type': 'serviceTask',
        'id_prefix': 'Task',
        'dimensions': {'width': 100, 'height': 80}
    },
    'manual_task': {
        'xml_type': 'manualTask',
        'id_prefix': 'Task',
        'dimensions': {'width': 100, 'height': 80}
    },
    'exclusive_gateway': {
        'xml_type': 'exclusiveGateway',
        'id_prefix': 'Gateway',
        'dimensions': {'width': 50, 'height': 50}
    },
    'sub_process': {
        'xml_type': 'subProcess',
        'id_prefix': 'SubProcess',
        'dimensions': {'width': 350, 'height': 200}
    }
}

# Create reverse lookup for variants
BPMN_TYPE_VARIANTS = {
    # Each type maps to itself
    bpmn_type: bpmn_type
    for bpmn_type in BPMN_TYPES.keys()
}

# Add common variants
variant_mappings = {
    # Events
    'startEvent': 'start_event',
    'endEvent': 'end_event',
    'StartEvent': 'start_event',
    'EndEvent': 'end_event',
    
    # Tasks
    'userTask': 'user_task',
    'serviceTask': 'service_task',
    'manualTask': 'manual_task',
    'UserTask': 'user_task',
    'ServiceTask': 'service_task',
    'ManualTask': 'manual_task',
    'Task': 'user_task',  # Default task type
    
    # Gateways
    'exclusiveGateway': 'exclusive_gateway',
    'ExclusiveGateway': 'exclusive_gateway',
    'Gateway': 'exclusive_gateway',
    
    # Subprocesses
    'subProcess': 'sub_process',
    'SubProcess': 'sub_process',
    'subprocess': 'sub_process'
}

# Update the variants dictionary
BPMN_TYPE_VARIANTS.update(variant_mappings)

# Layout Constants
LAYOUT_SETTINGS = {
    'base_x': 100,
    'base_y': 100,
    'element_spacing': 200,
    'subprocess_spacing': 120,
    'subprocess_offset': 50
}

# For backward compatibility
ELEMENT_SPACING = LAYOUT_SETTINGS['element_spacing']

# XML Namespace Constants
XML_NAMESPACES = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
    'camunda': 'http://camunda.org/schema/1.0/bpmn'
} 