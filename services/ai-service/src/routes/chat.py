from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from ..database import get_db
from ..models.conversation import Conversation, Message
from ..utils.openai_client import chat_completion, analyze_sentiment
from ..utils.prompt_templates import PromptTemplates

router = APIRouter()

@router.post("/chat/start")
async def start_conversation(
    user_id: int,
    initial_context: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """Start a new conversation."""
    conversation = Conversation(user_id=user_id, context=initial_context or {})
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.post("/chat/{conversation_id}/message")
async def send_message(
    conversation_id: int,
    content: str,
    db: Session = Depends(get_db)
):
    """Send a message in a conversation and get AI response."""
    # Get conversation
    conversation = await db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=content
    )
    db.add(user_message)
    
    # Get conversation history
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    # Prepare messages for OpenAI
    chat_messages = [{"role": m.role, "content": m.content} for m in messages]
    
    # Get AI response
    response_content = await chat_completion(chat_messages)
    if not response_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI response"
        )
    
    # Create AI message
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_content
    )
    db.add(ai_message)
    
    # Analyze sentiment
    sentiment = await analyze_sentiment(content)
    
    # Update conversation context
    conversation.context = {
        **(conversation.context or {}),
        "last_sentiment": sentiment
    }
    
    await db.commit()
    return {
        "message": ai_message,
        "sentiment": sentiment
    }

@router.get("/chat/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation history."""
    conversation = await db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return {
        "conversation": conversation,
        "messages": messages
    }
