"""
OrderItem model for Smart Canteen Manager.
Represents individual items within an order.
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base


class OrderItem(Base):
    """
    Order item model representing individual items in an order.
    
    Attributes:
        id: Primary key
        order_id: Foreign key to Order
        menu_item_id: Foreign key to MenuItem
        quantity: Number of items ordered
        price_at_order_time: Price when order was placed (immutable)
        order: Relationship to Order
        menu_item: Relationship to MenuItem
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_order_time = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
