from typing import Dict, Any
from core.config import settings
from core.logger import logger, log_exception
import json

def analyze_prompt(prompt: str, chat_history: list) -> Dict[str, Any]:
    """
    Analyze the user prompt to determine the type of update required.
    """
    system_message = """You are an AI assistant specializing in BPMN analysis.
    Analyze user prompts and determine if they are requesting:
    1. A business workflow update
    2. A layout adjustment
    3. Both a workflow update and layout adjustment
    4. Neither (a general query)

    You must ALWAYS respond with valid JSON only, no other text.
    The JSON must follow this structure:
    {
        "update_type": "workflow|layout|both|general",
        "workflow_changes": ["list", "of", "changes"],
        "layout_requests": ["list", "of", "adjustments"],
        "sentiment": "positive|negative|neutral"
    }
    """

    logger.debug(f"Analyzing prompt: {prompt}")
    logger.debug(f"Chat history length: {len(chat_history)}")
    
    try:
        response = settings.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                *chat_history,
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        result = response.choices[0].message.content
        logger.debug(f"OpenAI analysis response: {result}")
        
        parsed_result = json.loads(result)
        logger.debug(f"Parsed analysis: {json.dumps(parsed_result, indent=2)}")
        return parsed_result
            
    except Exception as e:
        logger.error("Error during prompt analysis")
        log_exception(e)
        raise

