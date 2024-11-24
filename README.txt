BPMN Generator API

This project is a BPMN (Business Process Model and Notation) generator API that converts natural language descriptions of business processes into BPMN XML.

Project Structure and Components:

1. main.py: The entry point of the application, sets up the FastAPI server.
2. api/chat.py: Defines the REST endpoint for BPMN generation.
3. lib/natural_language_processor.py: Processes natural language input using OpenAI's GPT model.
4. lib/intermediary_notation_generator.py: Converts NLP output into a structured intermediary notation.
5. lib/bpmn_xml_generator.py: Generates BPMN XML from the intermediary notation.
6. tests/test_natural_language_processor.py: Contains unit tests for the BPMN generation process.

How It Works:

1. The user sends a natural language description of a business process to the API.
2. The natural language processor uses OpenAI's GPT model to extract BPMN elements from the text.
3. The intermediary notation generator converts the extracted elements into a structured format.
4. The BPMN XML generator creates a valid BPMN XML representation of the process.
5. The API returns the generated BPMN XML to the user.

Setup and Configuration:

1. Docker Setup:
- Ensure Docker is installed on your system.
- Clone the repository:
  git clone https://github.com/yourusername/bpmn-generator-api.git
  cd bpmn-generator-api
- Create a .env file in the project root and add your OpenAI API key:
  OPENAI_API_KEY=your_api_key_here
- Build the Docker image:
  docker build -t bpmn-generator-api .
- Run the Docker container:
  docker run -p 8000:8000 --env-file .env bpmn-generator-api

2. Manual Setup:
- Ensure Python 3.9 or higher is installed.
- Clone the repository:
  git clone https://github.com/yourusername/bpmn-generator-api.git
  cd bpmn-generator-api
- Create a virtual environment:
  python -m venv venv
- Activate the virtual environment:
  - On Windows: venv\Scripts\activate
  - On macOS and Linux: source venv/bin/activate
- Install dependencies:
  pip install -r requirements.txt
- Create a .env file in the project root and add your OpenAI API key:
  OPENAI_API_KEY=your_api_key_here
- Run the application:
  uvicorn main:app --host 0.0.0.0 --port 8000

Usage:

1. The API will be available at http://localhost:8000
2. Use the /chat endpoint to generate BPMN from natural language descriptions.
- Send a POST request to http://localhost:8000/chat with a JSON body:
  {
    "text": "Your process description here"
  }
- The API will return a JSON response with the generated BPMN XML:
  {
    "bpmn_xml": "<bpmn:definitions>...</bpmn:definitions>"
  }

3. You can use tools like curl, Postman, or any HTTP client to interact with the API.

Sample curl command:
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The order process starts when a customer submits an order online. The system then automatically checks the inventory. If the items are in stock, the sales team reviews the order. If approved, the warehouse staff fulfills the order manually. The system then generates a shipping label and notifies the customer. If the items are not in stock or the order is rejected, the system notifies the customer. Once the order is shipped or the customer is notified of unavailability, the process ends."
  }'

Running Local Tests:

To run local tests, follow these steps:

1. Ensure you have completed either the Docker or Manual Setup steps mentioned above.
2. If using Docker, exec into the container:
docker exec -it <container_id> /bin/bash
3. Run the tests:
pytest tests/

4. To run a specific test file:
pytest tests/test_natural_language_processor.py

5. To generate a test coverage report:
coverage run -m pytest
coverage report

Helpful Tips:

1. API Key Security: Never expose your OpenAI API key in public repositories or client-side code. Always use environment variables or secure secret management systems.

2. Error Handling: If you encounter errors, check the following:
- Ensure your OpenAI API key is correctly set and has sufficient credits.
- Verify that your input text is clear and descriptive of a business process.
- Check for any network issues if the API is not responding.

3. Customization:
- To modify the BPMN element extraction, update the prompt in natural_language_processor.py.
- To change the structure of the intermediary notation, modify intermediary_notation_generator.py.
- To alter the BPMN XML output, adjust the logic in bpmn_xml_generator.py.

4. BPMN Visualization: To visualize the generated BPMN XML, you can use online tools like bpmn.io or integrate a BPMN viewer into your application.

5. Performance: For large or complex process descriptions, the API might take longer to respond. Consider implementing asynchronous processing for better user experience in such cases.

6. Logging: Enable logging in your application to track the processing steps and help with debugging. You can use Python's built-in logging module or a third-party logging solution.

7. Rate Limiting: Be aware of OpenAI's rate limits and implement appropriate rate limiting in your application to avoid exceeding these limits.

Note: Replace 'your_api_key_here' with your actual OpenAI API key when setting up the environment.

For more information about BPMN, visit: https://www.omg.org/spec/BPMN/2.0/
For OpenAI API documentation, visit: https://platform.openai.com/docs/

