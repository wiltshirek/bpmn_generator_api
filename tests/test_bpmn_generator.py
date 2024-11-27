from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_bpmn():
    response = client.post(
        "/api/bpmn",
        json={
            "prompt": "Start the process, then perform Task A, followed by Task B, and end the process.",
            "chat_history": []
        }
    )
    assert response.status_code == 200
    assert "bpmn_xml" in response.json()

def test_update_layout():
    response = client.post(
        "/api/bpmn",
        json={
            "prompt": "Move Task A to the right of Task B",
            "chat_history": [],
            "existing_bpmn_xml": "<some valid BPMN XML>"
        }
    )
    assert response.status_code == 200
    assert "bpmn_xml" in response.json()
