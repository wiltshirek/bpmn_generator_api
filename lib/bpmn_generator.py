from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from lib.prompt_analyzer import analyze_prompt
from lib.natural_language_processor import process_text
from lib.intermediary_notation_generator import generate_intermediary_notation
from lib.bpmn_xml_generator import generate_bpmn_xml
from core.config import settings
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class BPMNRequest(BaseModel):
    prompt: str
    chat_history: List[ChatMessage]
    existing_bpmn_xml: Optional[str] = None

class BPMNGeneratorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_new_bpmn(self, prompt: str, chat_history: list) -> str:
        """Generate new BPMN XML from business process description"""
        logger.debug(f"Starting new BPMN generation for prompt: {prompt}")
        
        logger.debug("Step 1: Processing text with NLP")
        nlp_result = process_text(prompt)
        logger.debug(f"NLP Result: {json.dumps(nlp_result, indent=2)}")
        
        logger.debug("Step 2: Generating intermediary notation")
        intermediary = generate_intermediary_notation(nlp_result)
        logger.debug(f"Intermediary Notation: {json.dumps(intermediary, indent=2)}")
        
        logger.debug("Step 3: Generating final BPMN XML")
        xml = generate_bpmn_xml(intermediary)
        logger.debug(f"Generated XML length: {len(xml)} characters")
        
        return xml
        
    def update_layout(self, prompt: str, existing_bpmn: str, chat_history: list, is_beautification: bool = False) -> str:
        """Update only the layout of existing BPMN XML"""
        system_message = """
        You are a BPMN XML layout expert. Your task is to modify the given BPMN XML based on the user's layout adjustment requests.

        Follow these layout principles:
        1. Maintain a primarily horizontal flow from left to right
        2. Prevent any element overlaps:
           - Tasks and gateways should have clear spacing
           - Sequence flow arrows should not cross or overlap when possible
           - Minimum spacing of 50px between elements

        3. Subprocess Layout:
           - Group subprocess elements within their parent container
           - Maintain clear boundaries around subprocess content
           - Add 50px padding inside subprocess containers
           - Align internal elements in a logical flow

        4. Connection Rules:
           - Minimize line crossings in sequence flows
           - Use direct paths when possible
           - Maintain consistent spacing between parallel flows
           - Ensure arrow endpoints connect properly to elements

        5. General Guidelines:
           - Start events should be leftmost
           - End events should be rightmost
           - Maintain consistent vertical alignment when possible
           - Use standard spacing between similar element types

        Only modify x and y coordinate attributes.
        Do not change any process logic, flows, or connections.
        Ensure the output is valid BPMN XML.
        """
        
        messages = [
            {"role": "system", "content": system_message},
            *[{"role": m.role, "content": m.content} for m in chat_history],
            {"role": "user", "content": f"Current BPMN XML:\n{existing_bpmn}\n\nLayout request:\n{prompt}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        return response.choices[0].message.content

    def generate_or_update_bpmn(self, prompt: str, chat_history: list, existing_bpmn: Optional[str] = None) -> str:
        """Generate new BPMN or update existing one based on the prompt"""
        if existing_bpmn:
            return self.update_layout(prompt, existing_bpmn, chat_history)
        return self.generate_new_bpmn(prompt, chat_history)

# Singleton instance
bpmn_service = BPMNGeneratorService()

router = APIRouter()

@router.post("/bpmn")
async def handle_bpmn_request(request: BPMNRequest):
    try:
        # Analyze the prompt to determine the type of request
        analysis = analyze_prompt(request.prompt, request.chat_history)
        
        if analysis["update_type"] == "layout":
            if not request.existing_bpmn_xml:
                raise HTTPException(
                    status_code=400,
                    detail="Layout updates require existing BPMN XML"
                )
            
            # Determine if this is a beautification or specific edit
            is_beautification = analysis["sentiment"] == "positive"
            
            # Handle layout adjustment
            updated_xml = bpmn_service.generate_or_update_bpmn(
                prompt=request.prompt,
                existing_bpmn=request.existing_bpmn_xml,
                chat_history=request.chat_history,
                is_beautification=is_beautification  # Pass this to the service
            )
            return {"bpmn_xml": updated_xml}
            
        else:  # workflow update or new process
            # Generate new BPMN XML from scratch
            new_xml = bpmn_service.generate_or_update_bpmn(
                prompt=request.prompt,
                chat_history=request.chat_history
            )
            return {"bpmn_xml": new_xml}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

