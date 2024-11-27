from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ValidationError(Exception):
    message: str
    details: Dict[str, Any] = None

    def __str__(self):
        return self.message 

class ProcessingError(Exception):
    """Raised when text processing fails"""
    pass

class GenerationError(Exception):
    """Raised when BPMN generation fails"""
    pass 