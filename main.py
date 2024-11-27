from contextlib import asynccontextmanager
from fastapi import FastAPI
from lib.bpmn_generator import router as bpmn_router
from core.config import settings
from core.logger import logger
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Register only the BPMN router
app.include_router(bpmn_router, prefix="/api", tags=["bpmn"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Required for Docker
        port=8000,
        reload=False  # Disable reload in production
    )

