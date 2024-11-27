import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Settings:
    PROJECT_NAME: str = "BPMN Generator API"
    PROJECT_VERSION: str = "1.0.0"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    @property
    def openai_client(self):
        if not hasattr(self, '_openai_client'):
            self._openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
        return self._openai_client

settings = Settings()
