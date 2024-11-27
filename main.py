from fastapi import FastAPI
from lib.bpmn_generator import router as bpmn_router
from api.chat import router as chat_router

app = FastAPI(
    title="BPMN Generator API",
    description="API for generating and modifying BPMN diagrams",
    version="1.0.0"
)

# Register routers with proper prefixes
app.include_router(bpmn_router, prefix="/api/v1", tags=["BPMN"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

