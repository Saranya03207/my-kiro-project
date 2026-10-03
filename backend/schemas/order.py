"""
Pydantic schemas for order validation.
Handles request validation and response serialization for orders.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


class OrderItemCreate(BaseModel):
    """
    Schema for creating an order item within an order.
    
    Validates:
    - menu_item_id: Must be a valid integer
    - quantity: Must be >= 1
    """
    menu_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_positive(cls, v: int) -> int:
        """Validate that quantity is at least 1."""
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v


class OrderCreate(BaseModel):
    """
    Schema for creating a new order.
    
    An order must contain at least one item.
    Each item specifies a menu_item_id and quantity.
    """
    items: List[OrderItemCreate] = Field(..., min_length=1)
    
    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v: List[OrderItemCreate]) -> List[OrderItemCreate]:
        """Validate that order contains at least one item."""
        if not v or len(v) == 0:
            raise ValueError('Order must contain at least one item')
        return v


class OrderItemResponse(BaseModel):
    """
    Schema for order item in API responses.
    
    Returns order item details including the menu item name
    and the price at the time the order was placed.
    """
    menu_item_id: int
    menu_item_name: str
    quantity: int
    price_at_order_time: Decimal


class OrderResponse(BaseModel):
    """
    Schema for order API responses.
    
    Returns complete order details including all items,
    student information, status, and timestamps.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    student_id: str
    total_price: Decimal
    status: str
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
