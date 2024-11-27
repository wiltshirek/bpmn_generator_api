from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import json
from core.config import settings
from core.logger import logger
from .exceptions import ValidationError
from .natural_language_processor import process_text, build_system_prompt, process_layout_update
from .prompt_analyzer import analyze_prompt
from .intermediary_notation_generator import generate_intermediary_notation
from .bpmn_xml_generator import BPMNXMLGenerator

class ChatMessage(BaseModel):
    role: str
    content: str

class BPMNRequest(BaseModel):
    prompt: str
    chat_history: List[ChatMessage] = []
    existing_bpmn_xml: Optional[str] = None

class BPMNGeneratorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_new_bpmn(self, prompt: str, chat_history: list) -> str:
        """Generate new BPMN XML from business process description"""
        logger.debug("=== Starting New BPMN Generation ===")
        
        try:
            nlp_result = process_text(prompt)
            intermediary = generate_intermediary_notation(nlp_result)
            xml_generator = BPMNXMLGenerator()
            return xml_generator.generate_bpmn_xml(intermediary)
            
        except Exception as e:
            logger.error(f"Failed to generate new BPMN: {str(e)}")
            raise
        
    def update_layout(self, prompt: str, existing_bpmn: str, chat_history: list, is_beautification: bool = False) -> str:
        """Update only the layout of existing BPMN XML"""
        logger.debug("\n=== Starting Layout Update ===")
        logger.debug(f"Layout Request: {prompt}")
        logger.debug(f"Is Beautification: {is_beautification}")
        
        try:
            result = process_layout_update(prompt, existing_bpmn, chat_history)
            logger.debug(f"Changes Made: {result.get('changes_made', [])}")
            logger.debug(f"Layout Principles Applied: {result.get('layout_principles_applied', [])}")
            return result['modified_bpmn']
            
        except Exception as e:
            logger.error(f"Failed to update layout: {str(e)}")
            raise

    def generate_or_update_bpmn(self, prompt: str, chat_history: list, existing_bpmn: str = None, is_beautification: bool = False) -> str:
        """Generate new BPMN or update existing one based on parameters"""
        if existing_bpmn:
            return self.update_layout(
                prompt=prompt,
                existing_bpmn=existing_bpmn,
                chat_history=chat_history,
                is_beautification=is_beautification
            )
        else:
            return self.generate_new_bpmn(
                prompt=prompt,
                chat_history=chat_history
            )

# Singleton instance
bpmn_service = BPMNGeneratorService()

router = APIRouter(prefix="/api")

@router.post("/bpmn")
async def handle_bpmn_request(request: BPMNRequest):
    try:
        logger.debug("\n=== New BPMN Request ===")
        logger.debug(f"Request Prompt: {request.prompt}")
        logger.debug(f"Has Existing BPMN: {bool(request.existing_bpmn_xml)}")
        logger.debug(f"Chat History Length: {len(request.chat_history)}")
        
        logger.debug("\n=== Analyzing Prompt ===")
        analysis = analyze_prompt(request.prompt, request.chat_history)
        logger.debug(f"Prompt Analysis Result:\n{json.dumps(analysis, indent=2)}")
        
        if analysis["update_type"] == "layout":
            logger.debug("\n=== Handling Layout Update ===")
            if not request.existing_bpmn_xml:
                raise HTTPException(
                    status_code=400,
                    detail="Layout updates require existing BPMN XML"
                )
            
            is_beautification = analysis["sentiment"] == "positive"
            logger.debug(f"Is Beautification Request: {is_beautification}")
            
            updated_xml = bpmn_service.generate_or_update_bpmn(
                prompt=request.prompt,
                existing_bpmn=request.existing_bpmn_xml,
                chat_history=request.chat_history,
                is_beautification=is_beautification
            )
            
            logger.debug("\n=== Layout Update Complete ===")
            logger.debug(f"Updated BPMN XML Length: {len(updated_xml)}")
            return {"bpmn_xml": updated_xml}
            
        else:
            logger.debug("\n=== Handling New Process Generation ===")
            new_xml = bpmn_service.generate_or_update_bpmn(
                prompt=request.prompt,
                chat_history=request.chat_history
            )
            
            logger.debug("\n=== Process Generation Complete ===")
            logger.debug(f"New BPMN XML Length: {len(new_xml)}")
            return {"bpmn_xml": new_xml}
            
    except Exception as e:
        logger.error("\n=== Error Processing Request ===")
        logger.error(f"Error: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

