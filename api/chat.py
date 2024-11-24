from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from lib.natural_language_processor import process_text
from lib.intermediary_notation_generator import generate_intermediary_notation
from lib.bpmn_xml_generator import generate_bpmn_xml
from core.logger import logger
import traceback
import json

router = APIRouter()

class ChatInput(BaseModel):
    text: str

@router.post("/chat")
async def generate_bpmn(input: ChatInput):
    try:
        logger.info(f"Received request with text: {input.text}")
        
        # Step 1: Process text through NLP
        nlp_result = process_text(input.text)
        
        # Step 2: Generate intermediary notation
        intermediary_notation = generate_intermediary_notation(nlp_result)
        
        # Step 3: Generate BPMN XML
        bpmn_xml = generate_bpmn_xml(intermediary_notation)
        
        logger.info("Successfully generated BPMN XML")
        logger.info(bpmn_xml)
        
        # Pre-serialize the intermediary notation
        intermediary_json = json.dumps(intermediary_notation, indent=2)
        
        # Create response with raw XML string
        from fastapi.responses import JSONResponse
        return JSONResponse(content={
            "original_prompt": input.text,
            "intermediary_notation": intermediary_json,
            "bpmn_xml": bpmn_xml
        }, media_type="application/json")
    except Exception as e:
        logger.error(f"Error in generate_bpmn: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))