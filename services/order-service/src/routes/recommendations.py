import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.order import MenuItem
from ..utils.recommendation_engine import (
    get_personalized_recommendations,
    filter_by_constraints,
    get_similar_items as get_similar_items_engine
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recommendations")
async def get_recommendations(
    user_id: int,
    preferences: Optional[dict] = None,
    constraints: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Get personalized drink recommendations."""
    try:
        # Get available menu items
        menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).all()
        
        # Apply any constraints (age, alcohol content, etc.)
        if constraints:
            menu_items = filter_by_constraints(menu_items, constraints)
        
        # Get personalized recommendations
        recommendations = get_personalized_recommendations(
            user_id=user_id,
            preferences=preferences or {},
            available_items=menu_items
        )
        
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing recommendations"
        )

@router.get("/recommendations/popular")
async def get_popular_recommendations(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get popular drink recommendations, optionally filtered by category."""
    try:
        # Get available menu items
        query = db.query(MenuItem).filter(MenuItem.is_available == True)
        if category:
            query = query.filter(MenuItem.category == category)
        menu_items = query.all()
        
        # TODO: Implement popularity tracking and sorting
        # For now, return all items
        return menu_items
    except Exception as e:
        logger.error(f"Error getting popular recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing popular recommendations"
        )

@router.get("/recommendations/similar/{item_id}")
async def get_similar_items(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get similar items to a given menu item."""
    try:
        # Get the reference item
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Get all available items
        menu_items = db.query(MenuItem).filter(
            MenuItem.is_available == True
        ).all()
        
        # Use the recommendation engine to find similar items
        similar_items = get_similar_items_engine(item, menu_items)
        
        return similar_items
    except Exception as e:
        logger.error(f"Error getting similar items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing recommendation"
        )
