from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from ..models.order import MenuItem

async def validate_order_items(db: Session, items: List[dict]) -> Dict[int, MenuItem]:
    """Validate order items exist and are available."""
    # Get all item IDs
    item_ids = [item["item_id"] for item in items]
    
    # Get menu items
    menu_items = await db.query(MenuItem).filter(
        MenuItem.id.in_(item_ids),
        MenuItem.is_available == True
    ).all()
    
    # Create lookup dictionary
    menu_items_dict = {item.id: item for item in menu_items}
    
    # Check all items exist and are available
    missing_items = set(item_ids) - set(menu_items_dict.keys())
    if missing_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Items not found or unavailable: {missing_items}"
        )
    
    # Validate quantities
    for item in items:
        if item["quantity"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid quantity for item {item['item_id']}"
            )
    
    return menu_items_dict
