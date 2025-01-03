from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.room import Room, RoomParticipant, Message
from ..utils.agora import generate_rtc_token

router = APIRouter()

@router.post("/rooms")
async def create_room(
    name: str,
    owner_id: int,
    room_type: str,
    max_participants: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Create a new room."""
    # Generate unique channel name
    channel_name = f"{name}-{datetime.now().timestamp()}"
    
    room = Room(
        name=name,
        channel_name=channel_name,
        owner_id=owner_id,
        room_type=room_type,
        max_participants=max_participants
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    
    # Add owner as participant
    participant = RoomParticipant(
        room_id=room.id,
        user_id=owner_id,
        role="host"
    )
    db.add(participant)
    await db.commit()
    
    return room

@router.get("/rooms")
async def list_rooms(
    room_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List active rooms."""
    query = db.query(Room).filter(Room.is_active == True)
    if room_type:
        query = query.filter(Room.room_type == room_type)
    return await query.all()

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Join a room."""
    room = await db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    if room.current_participants >= room.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is full"
        )
    
    # Check if user is already in room
    participant = await db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == user_id,
        RoomParticipant.left_at.is_(None)
    ).first()
    
    if participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already in room"
        )
    
    # Add participant
    participant = RoomParticipant(
        room_id=room_id,
        user_id=user_id,
        role="participant"
    )
    db.add(participant)
    
    # Update room participant count
    room.current_participants += 1
    
    await db.commit()
    
    # Generate Agora token
    token = generate_rtc_token(room.channel_name, user_id)
    
    return {
        "room": room,
        "token": token,
        "channel_name": room.channel_name
    }

@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Leave a room."""
    participant = await db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == user_id,
        RoomParticipant.left_at.is_(None)
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not in room"
        )
    
    # Update participant
    participant.left_at = datetime.utcnow()
    
    # Update room participant count
    room = await db.query(Room).filter(Room.id == room_id).first()
    room.current_participants -= 1
    
    # If no participants left, deactivate room
    if room.current_participants <= 0:
        room.is_active = False
    
    await db.commit()
    return {"status": "success"}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for room chat."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Save message to database
            message = Message(
                room_id=room_id,
                user_id=user_id,
                content=data["content"],
                message_type="text"
            )
            db.add(message)
            await db.commit()
            
            # Broadcast message to room
            await websocket.send_json({
                "user_id": user_id,
                "content": data["content"],
                "created_at": message.created_at.isoformat()
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
