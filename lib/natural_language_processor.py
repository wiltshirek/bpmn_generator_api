from typing import Dict
import openai
from core.config import settings
from core.logger import logger
import traceback

openai.api_key = settings.OPENAI_API_KEY

def process_text(text: str) -> str:
    try:
        logger.info("Starting natural language processing")
        logger.debug(f"Processing text: {text}")
        
        system_prompt = """You are a BPMN expert AI assistant. Convert the given process description into a structured format with the following elements:
1. List of actors (participants)
2. Process flow using -> notation, with:
   - Substeps indicated by indentation and [sub] prefix
   - Parallel tasks indicated by || between activities
3. Actor mapping to activities

Use this format:
Actors: [comma-separated list of actors]

Start -> SubmitOrder(user) -> [sub]ProcessOrder -> End
  ProcessOrder: Start -> ValidateOrder(service) || CheckInventory(service) -> ReviewOrder(user) -> End

Actor1: [SubmitOrder]
Actor2: [ValidateOrder, CheckInventory]
Actor3: [ReviewOrder]

Note: 
- Use camelCase for activity names (e.g., SubmitOrder, ValidateApplication)
- Avoid spaces and special characters in names
- Task types should be one of: service, user, manual
- Use XOR for exclusive gateways, AND for parallel gateways
- Include conditions in parentheses for gateway paths"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        logger.info("Successfully received OpenAI API response")
        logger.debug(f"OpenAI response: {response}")
        
        result = response.choices[0].message['content']
        return result
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise Exception(f"Error in NLP processing: {str(e)}")