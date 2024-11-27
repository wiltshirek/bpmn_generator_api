# Single source of truth for BPMN types
BPMN_TYPES = {
    'start_event': {
        'id_prefix': 'StartEvent'
    },
    'end_event': {
        'id_prefix': 'EndEvent'
    },
    'user_task': {
        'id_prefix': 'Task'
    },
    'service_task': {
        'id_prefix': 'ServiceTask'
    },
    'exclusive_gateway': {
        'id_prefix': 'Gateway'
    },
    'parallel_gateway': {
        'id_prefix': 'ParallelGateway'
    },
    'sub_process': {
        'id_prefix': 'SubProcess'
    }
}

# Add BPMN type variants mapping
BPMN_TYPE_VARIANTS = {
    'start_event': ['start', 'startevent'],
    'end_event': ['end', 'endevent'],
    'user_task': ['task', 'usertask'],
    'service_task': ['service', 'servicetask'],
    'exclusive_gateway': ['gateway', 'exclusivegateway'],
    'parallel_gateway': ['parallel', 'parallelgateway'],
    'sub_process': ['subprocess', 'subProcess']
}

GATEWAY_PAIRS = {
    'exclusive_gateway': 'start',
    'parallel_gateway': 'start',
    'exclusive_gateway_end': 'end',
    'parallel_gateway_end': 'end'
}

LAYOUT_SETTINGS = {
    'lane_height': 200,
    'element_width': 100,
    'element_height': 80,
    'horizontal_spacing': 150,
    'vertical_spacing': 100
} 