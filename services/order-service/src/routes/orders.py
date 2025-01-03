from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.order import Order, MenuItem
from ..utils.validation import validate_order_items

router = APIRouter()

@router.post("/orders")
async def create_order(
    user_id: int,
    items: List[dict],  # List of {item_id: int, quantity: int}
    db: Session = Depends(get_db)
):
    """Create a new order."""
    # Validate items exist and are available
    menu_items = await validate_order_items(db, items)
    
    # Calculate total amount
    total_amount = sum(
        item["quantity"] * menu_items[item["item_id"]].price
        for item in items
    )
    
    # Create order
    order = Order(
        user_id=user_id,
        items=items,
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order

@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get order details."""
    order = await db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    """Update order status."""
    valid_statuses = ["pending", "paid", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order = await db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    
    return order

@router.get("/menu")
async def get_menu(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get menu items, optionally filtered by category."""
    query = db.query(MenuItem).filter(MenuItem.is_available == True)
    if category:
        query = query.filter(MenuItem.category == category)
    return await query.all()
