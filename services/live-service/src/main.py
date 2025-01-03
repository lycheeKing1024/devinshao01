import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect

from .database import engine
from .models.room import Base
from .routes import rooms
from .utils.agora import AgoraClient
from shared.client import ServiceClient
from shared.middleware import ServiceAuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Live Service", version="0.1.0")

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
service_client = ServiceClient('live')

# Initialize Agora client
agora_client = AgoraClient()

# Add to app state
app.state.service_client = service_client
app.state.agora_client = agora_client

# WebSocket connections store
active_connections: dict = {}

# Include routers
app.include_router(rooms.router, prefix="/api/v1/rooms", tags=["rooms"])

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time chat."""
    try:
        await websocket.accept()
        if room_id not in active_connections:
            active_connections[room_id] = {}
        active_connections[room_id][user_id] = websocket
        
        try:
            while True:
                data = await websocket.receive_text()
                # Broadcast message to all users in the room
                for uid, conn in active_connections[room_id].items():
                    if uid != user_id:  # Don't send back to sender
                        await conn.send_text(f"{user_id}: {data}")
        except WebSocketDisconnect:
            # Remove connection when client disconnects
            if room_id in active_connections:
                active_connections[room_id].pop(user_id, None)
                if not active_connections[room_id]:
                    active_connections.pop(room_id, None)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        raise

@app.on_event("startup")
async def startup():
    """Initialize service and create database tables on startup."""
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Initialize service client
        await service_client.initialize()
        
        # Initialize Agora client
        await agora_client.initialize()
        
        logger.info("Live service initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    try:
        await service_client.close()
        await agora_client.close()
        
        # Close all WebSocket connections
        for room in active_connections.values():
            for connection in room.values():
                await connection.close()
        
        logger.info("Live service shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "live",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
