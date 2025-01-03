from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from ..database import get_db
from ..models.conversation import Message
from ..utils.openai_client import moderate_content

router = APIRouter()

@router.post("/moderate/message")
async def moderate_message(
    content: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Moderate a message using OpenAI's moderation API.
    Returns moderation results and whether the message is safe.
    """
    moderation_result = await moderate_content(content)
    return {
        "is_safe": not moderation_result.get("flagged", False),
        "moderation_result": moderation_result
    }

@router.post("/moderate/batch")
async def moderate_messages(
    messages: List[str],
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Moderate multiple messages in batch.
    Returns moderation results for each message.
    """
    results = []
    for message in messages:
        moderation_result = await moderate_content(message)
        results.append({
            "content": message,
            "is_safe": not moderation_result.get("flagged", False),
            "moderation_result": moderation_result
        })
    return results

@router.get("/moderation/history/{conversation_id}")
async def get_moderation_history(
    conversation_id: int,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get moderation history for a conversation.
    """
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.moderation_result.isnot(None)
    ).order_by(Message.created_at.desc()).all()
    
    return [
        {
            "message_id": message.id,
            "content": message.content,
            "moderation_result": message.moderation_result,
            "created_at": message.created_at
        }
        for message in messages
    ]
