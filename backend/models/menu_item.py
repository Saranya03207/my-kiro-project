"""
MenuItem model for Smart Canteen Manager.
Represents food and beverage items available in the canteen.
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class MenuItem(Base):
    """
    Menu item model representing food/beverage items.
    
    Attributes:
        id: Primary key
        name: Item name (unique)
        description: Item description
        price: Item price (positive decimal with 2 decimal places)
        category: Food category (e.g., Meals, Snacks, Beverages)
        stock_quantity: Current stock level
        stock_threshold: Minimum stock level before low-stock alert
        is_available: Whether item is available for ordering
        is_deleted: Soft delete flag (preserves historical data)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    stock_threshold = Column(Integer, nullable=False, default=5)
    is_available = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
