from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import UserProfile
from ..utils.security import get_current_user

router = APIRouter()

@router.get("/me")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile."""
    profile = await db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.put("/me")
async def update_profile(
    nickname: Optional[str] = None,
    avatar_url: Optional[str] = None,
    bio: Optional[str] = None,
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    profile = await db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user["id"])
        db.add(profile)
    
    if nickname is not None:
        profile.nickname = nickname
    if avatar_url is not None:
        profile.avatar_url = avatar_url
    if bio is not None:
        profile.bio = bio
    if location is not None:
        profile.location = location
    
    await db.commit()
    await db.refresh(profile)
    return profile
