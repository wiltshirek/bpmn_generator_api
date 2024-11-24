from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from core.logger import logger
import traceback

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}")
    logger.error(f"Stack trace:\n{traceback.format_exc()}")
    return {"detail": str(exc), "stack_trace": traceback.format_exc()}

app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting BPMN Generator API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)