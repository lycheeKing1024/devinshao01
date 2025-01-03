import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models.order import Base
from .routes import orders, recommendations
from shared.client import ServiceClient
from shared.middleware import ServiceAuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service", version="0.1.0")

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
service_client = ServiceClient('order')

# Add to app state
app.state.service_client = service_client

# Include routers
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])

@app.on_event("startup")
async def startup():
    """Create database tables and initialize service on startup."""
    try:
        # Create database tables
        async with engine.begin() as conn: 
            await conn.run_sync(Base.metadata.create_all)
            
        # Initialize service client
        await service_client.initialize()
        logger.info("Order service initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    try: 
        await service_client.close()
        logger.info("Order service shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "order",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
