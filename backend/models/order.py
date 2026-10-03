"""
Order model for Smart Canteen Manager.
Represents customer orders placed through the system.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Order(Base):
    """
    Order model representing a student's food order.
    
    Attributes:
        id: Primary key
        student_id: Identifier of the student who placed the order
        total_price: Total order amount
        status: Order status (pending, preparing, ready, completed, cancelled)
        created_at: Timestamp of order placement
        updated_at: Timestamp of last status update
        items: Relationship to OrderItem (one-to-many)
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
