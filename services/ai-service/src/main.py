import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models.conversation import Base
from .routes import chat, moderation
from .utils.openai_client import OpenAIClient
from shared.client import ServiceClient
from shared.middleware import ServiceAuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Service", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add service auth middleware
app.add_middleware(ServiceAuthMiddleware)

# Initialize service client
service_client = ServiceClient('ai')

# Initialize OpenAI client
openai_client = OpenAIClient()

# Add to app state
app.state.service_client = service_client
app.state.openai_client = openai_client

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(moderation.router, prefix="/api/v1/moderation", tags=["moderation"])

@app.on_event("startup")
async def startup():
    """Initialize service and create database tables on startup."""
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Initialize service client
        await service_client.initialize()
        
        # Initialize OpenAI client
        await openai_client.initialize()
        
        logger.info("AI service initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    try:
        await service_client.close()
        await openai_client.close()
        logger.info("AI service shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
