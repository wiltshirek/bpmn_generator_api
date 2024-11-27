# BPMN Generator API

This project is a BPMN (Business Process Model and Notation) generator API that converts natural language descriptions of business processes into BPMN XML.

## Project Structure and Components:

1. main.py: The entry point of the application, sets up the FastAPI server.
2. api/bpmn_generator.py: Defines the REST endpoint for BPMN generation.
3. lib/natural_language_processor.py: Processes natural language input using OpenAI's GPT model.
4. lib/intermediary_notation_generator.py: Converts NLP output into a structured intermediary notation.
5. lib/bpmn_xml_generator.py: Generates BPMN XML from the intermediary notation.

## Setup and Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your OpenAI API key in a .env file: `OPENAI_API_KEY=your_api_key_here`
4. Run the server: `python main.py`

## Usage

Send a POST request to `http://localhost:8000/generate-bpmn` with a JSON body:

```json
{
  "description": "Your process description here"
}
