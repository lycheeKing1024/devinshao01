from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import get_db
from ..models.user import User, UserFollow
from ..utils.security import get_current_user

router = APIRouter()

@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow another user."""
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    # Check if target user exists
    target_user = await db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already following
    existing_follow = await db.query(UserFollow).filter(
        and_(
            UserFollow.follower_id == current_user["id"],
            UserFollow.following_id == user_id
        )
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Create follow relationship
    follow = UserFollow(
        follower_id=current_user["id"],
        following_id=user_id
    )
    db.add(follow)
    await db.commit()
    
    return {"status": "success"}

@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user."""
    follow = await db.query(UserFollow).filter(
        and_(
            UserFollow.follower_id == current_user["id"],
            UserFollow.following_id == user_id
        )
    ).first()
    
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this user"
        )
    
    await db.delete(follow)
    await db.commit()
    
    return {"status": "success"}

@router.get("/followers")
async def get_followers(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's followers."""
    followers = await db.query(User).join(
        UserFollow,
        User.id == UserFollow.follower_id
    ).filter(
        UserFollow.following_id == current_user["id"]
    ).all()
    
    return followers

@router.get("/following")
async def get_following(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users that current user is following."""
    following = await db.query(User).join(
        UserFollow,
        User.id == UserFollow.following_id
    ).filter(
        UserFollow.follower_id == current_user["id"]
    ).all()
    
    return following
