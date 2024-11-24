import pytest
from lib.natural_language_processor import process_text
from lib.intermediary_notation_generator import generate_intermediary_notation
from lib.bpmn_xml_generator import generate_bpmn_xml
import json

@pytest.fixture
def sample_process_description():
    return """
    The order process starts when a customer submits an order online. The system then automatically checks the inventory.
    If the items are in stock, the sales team reviews the order. If approved, the warehouse staff fulfills the order manually.
    The system then generates a shipping label and notifies the customer. If the items are not in stock or the order is rejected,
    the system notifies the customer. Once the order is shipped or the customer is notified of unavailability, the process ends.
    """

def test_process_text(sample_process_description):
    # Step 1: Natural Language Processing
    nlp_result = process_text(sample_process_description)
    
    # Check if the result is a non-empty string
    assert isinstance(nlp_result, str)
    assert len(nlp_result) > 0
    
    # Check if the result contains expected keywords
    expected_keywords = ['Actors:', 'Start', 'Submit order', 'Check inventory', 'Review order', 'XOR', 'Fulfill order', 'Generate shipping label', 'Notify customer', 'End', 'Customer:', 'System:', 'Sales Team:', 'Warehouse:']
    for keyword in expected_keywords:
        assert keyword in nlp_result, f"Expected keyword '{keyword}' not found in the result"

    # Step 2: Generate Intermediary Notation
    try:
        intermediary_notation = generate_intermediary_notation(nlp_result)
        assert 'actors' in intermediary_notation
        assert 'elements' in intermediary_notation
        assert 'flows' in intermediary_notation
        assert 'actorMapping' in intermediary_notation
        
        # Check if expected actors are present
        expected_actors = ['Customer', 'System', 'Sales Team', 'Warehouse']
        for actor in expected_actors:
            assert actor in intermediary_notation['actors'], f"Expected actor '{actor}' not found in the intermediary notation"
        
        # Check if task types are present
        task_types = [element['taskType'] for element in intermediary_notation['elements'] if element['type'] == 'task']
        assert 'user' in task_types
        assert 'service' in task_types
        assert 'manual' in task_types
        
        # Check if gateways are present
        gateway_types = [element['type'] for element in intermediary_notation['elements'] if 'Gateway' in element['type']]
        assert 'exclusiveGateway' in gateway_types
    except Exception as e:
        pytest.fail(f"Failed to generate intermediary notation: {str(e)}")

    # Step 3: Generate BPMN XML
    try:
        bpmn_xml = generate_bpmn_xml(intermediary_notation)
        assert isinstance(bpmn_xml, str)
        assert len(bpmn_xml) > 0
        assert bpmn_xml.startswith('<?xml')
        assert '<bpmn:definitions' in bpmn_xml
        assert '<bpmn:process' in bpmn_xml
        assert '<bpmndi:BPMNDiagram' in bpmn_xml
        assert '<bpmn:laneSet' in bpmn_xml
        assert '<bpmn:lane' in bpmn_xml
        assert '<bpmn:userTask' in bpmn_xml
        assert '<bpmn:serviceTask' in bpmn_xml
        assert '<bpmn:manualTask' in bpmn_xml
        assert '<bpmn:exclusiveGateway' in bpmn_xml
    except Exception as e:
        pytest.fail(f"Failed to generate BPMN XML: {str(e)}")

    # Return both intermediary notation and BPMN XML
    return {
        'intermediary_notation': json.dumps(intermediary_notation, indent=2),
        'bpmn_xml': bpmn_xml
    }

def test_process_text_error_handling():
    with pytest.raises(Exception):
        process_text("")  # Empty input should raise an exception

if __name__ == "__main__":
    # This allows us to run the test and print the results
    result = test_process_text(sample_process_description())
    print("Intermediary Notation:")
    print(result['intermediary_notation'])
    print("\nBPMN XML:")
    print(result['bpmn_xml'])