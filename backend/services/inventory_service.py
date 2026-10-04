"""
Inventory service for Smart Canteen Manager.
Handles stock management, inventory tracking, and low-stock alerts.
"""
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from backend.models.menu_item import MenuItem


class InventoryService:
    """
    Service class for inventory and stock management.
    
    Responsibilities:
    - Retrieve current stock levels for all items
    - Update and modify stock quantities
    - Track low-stock items and thresholds
    - Verify stock availability for operations
    """
    
    @staticmethod
    def get_inventory(db: DBSession) -> List[MenuItem]:
        """
        Get all menu items with their current stock levels.
        
        Includes deleted items to maintain inventory history.
        
        Args:
            db: Database session
            
        Returns:
            List of all menu items with stock information
        """
        return db.query(MenuItem).all()
    
    @staticmethod
    def update_stock(
        db: DBSession,
        item_id: int,
        quantity: int
    ) -> Optional[MenuItem]:
        """
        Set stock quantity to a specific value.
        
        Args:
            db: Database session
            item_id: Menu item ID
            quantity: New stock quantity (must be non-negative)
            
        Returns:
            Updated menu item if found, None otherwise
            
        Raises:
            ValueError: If quantity is negative
        """
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return None
        
        menu_item.stock_quantity = quantity
        db.commit()
        db.refresh(menu_item)
        return menu_item
    
    @staticmethod
    def increment_stock(
        db: DBSession,
        item_id: int,
        amount: int
    ) -> Optional[MenuItem]:
        """
        Increase stock quantity by a specified amount.
        
        Args:
            db: Database session
            item_id: Menu item ID
            amount: Amount to add (must be positive)
            
        Returns:
            Updated menu item if found, None otherwise
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Increment amount must be positive")
        
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return None
        
        menu_item.stock_quantity += amount
        db.commit()
        db.refresh(menu_item)
        return menu_item
    
    @staticmethod
    def decrement_stock(
        db: DBSession,
        item_id: int,
        amount: int
    ) -> Optional[MenuItem]:
        """
        Decrease stock quantity by a specified amount.
        
        Args:
            db: Database session
            item_id: Menu item ID
            amount: Amount to subtract (must be positive)
            
        Returns:
            Updated menu item if found, None otherwise
            
        Raises:
            ValueError: If amount is not positive or exceeds current stock
        """
        if amount <= 0:
            raise ValueError("Decrement amount must be positive")
        
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return None
        
        if menu_item.stock_quantity < amount:
            raise ValueError(
                f"Insufficient stock: current={menu_item.stock_quantity}, "
                f"requested={amount}"
            )
        
        menu_item.stock_quantity -= amount
        db.commit()
        db.refresh(menu_item)
        return menu_item
    
    @staticmethod
    def check_stock_availability(
        db: DBSession,
        item_id: int,
        quantity: int
    ) -> bool:
        """
        Check if sufficient stock is available for a purchase.
        
        Args:
            db: Database session
            item_id: Menu item ID
            quantity: Quantity to check
            
        Returns:
            True if stock is available, False otherwise
        """
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return False
        
        return menu_item.stock_quantity >= quantity
    
    @staticmethod
    def get_low_stock_items(db: DBSession) -> List[MenuItem]:
        """
        Get all items where stock is at or below their threshold.
        
        Compares current stock_quantity against stock_threshold for each item.
        Excludes deleted items from the list.
        
        Args:
            db: Database session
            
        Returns:
            List of menu items with stock <= threshold
        """
        return db.query(MenuItem).filter(
            MenuItem.stock_quantity <= MenuItem.stock_threshold,
            MenuItem.is_deleted == False
        ).all()
    
    @staticmethod
    def update_stock_threshold(
        db: DBSession,
        item_id: int,
        threshold: int
    ) -> Optional[MenuItem]:
        """
        Update the low-stock alert threshold for an item.
        
        Args:
            db: Database session
            item_id: Menu item ID
            threshold: New threshold value (must be non-negative)
            
        Returns:
            Updated menu item if found, None otherwise
            
        Raises:
            ValueError: If threshold is negative
        """
        if threshold < 0:
            raise ValueError("Stock threshold cannot be negative")
        
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return None
        
        menu_item.stock_threshold = threshold
        db.commit()
        db.refresh(menu_item)
        return menu_item
