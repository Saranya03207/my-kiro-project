"""
Menu service for Smart Canteen Manager.
Handles menu item retrieval, creation, updates, and management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from backend.models.menu_item import MenuItem
from backend.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse


class MenuService:
    """
    Service class for menu item management.
    
    Responsibilities:
    - Retrieve available menu items with sorting
    - Search and filter menu items
    - Create new menu items with uniqueness validation
    - Update menu items (partial updates)
    - Toggle item availability
    - Soft delete menu items
    """
    
    @staticmethod
    def get_available_menu_items(
        db: DBSession,
        include_unavailable: bool = False
    ) -> List[MenuItem]:
        """
        Get available menu items sorted by category and name.
        
        Args:
            db: Database session
            include_unavailable: If True, include unavailable items (admin view)
            
        Returns:
            List of menu items sorted by category then name
        """
        query = db.query(MenuItem).filter(MenuItem.is_deleted == False)
        
        if not include_unavailable:
            query = query.filter(MenuItem.is_available == True)
        
        # Sort by category and name
        return query.order_by(MenuItem.category, MenuItem.name).all()
    
    @staticmethod
    def get_menu_item_by_id(db: DBSession, item_id: int) -> Optional[MenuItem]:
        """
        Get a menu item by ID.
        
        Args:
            db: Database session
            item_id: Menu item ID
            
        Returns:
            MenuItem if found and not deleted, None otherwise
        """
        return db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.is_deleted == False
        ).first()
    
    @staticmethod
    def search_menu_items(
        db: DBSession,
        search: Optional[str] = None,
        category: Optional[str] = None,
        include_unavailable: bool = False
    ) -> List[MenuItem]:
        """
        Search and filter menu items.
        
        Args:
            db: Database session
            search: Search term for name or description (case-insensitive)
            category: Filter by category
            include_unavailable: If True, include unavailable items
            
        Returns:
            List of matching menu items sorted by category and name
        """
        query = db.query(MenuItem).filter(MenuItem.is_deleted == False)
        
        if not include_unavailable:
            query = query.filter(MenuItem.is_available == True)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (MenuItem.name.ilike(search_pattern)) |
                (MenuItem.description.ilike(search_pattern))
            )
        
        if category:
            query = query.filter(MenuItem.category == category)
        
        return query.order_by(MenuItem.category, MenuItem.name).all()
    
    @staticmethod
    def create_menu_item(
        db: DBSession,
        item_data: MenuItemCreate
    ) -> MenuItem:
        """
        Create a new menu item with uniqueness validation.
        
        Args:
            db: Database session
            item_data: Menu item creation data
            
        Returns:
            Created menu item
            
        Raises:
            ValueError: If menu item name already exists
        """
        # Check for name uniqueness
        existing = db.query(MenuItem).filter(
            MenuItem.name == item_data.name,
            MenuItem.is_deleted == False
        ).first()
        
        if existing:
            raise ValueError(f"Menu item with name '{item_data.name}' already exists")
        
        # Create new menu item
        menu_item = MenuItem(
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category,
            stock_quantity=item_data.stock_quantity,
            stock_threshold=item_data.stock_threshold,
            is_available=True,
            is_deleted=False
        )
        
        db.add(menu_item)
        try:
            db.commit()
            db.refresh(menu_item)
            return menu_item
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to create menu item: {str(e)}")
    
    @staticmethod
    def update_menu_item(
        db: DBSession,
        item_id: int,
        item_data: MenuItemUpdate
    ) -> Optional[MenuItem]:
        """
        Update a menu item with partial updates.
        
        Args:
            db: Database session
            item_id: Menu item ID
            item_data: Update data (only provided fields are updated)
            
        Returns:
            Updated menu item if found, None otherwise
            
        Raises:
            ValueError: If name update conflicts with existing item
        """
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.is_deleted == False
        ).first()
        
        if not menu_item:
            return None
        
        # Check name uniqueness if name is being updated
        if item_data.name is not None and item_data.name != menu_item.name:
            existing = db.query(MenuItem).filter(
                MenuItem.name == item_data.name,
                MenuItem.is_deleted == False,
                MenuItem.id != item_id
            ).first()
            
            if existing:
                raise ValueError(f"Menu item with name '{item_data.name}' already exists")
        
        # Update only provided fields
        update_dict = item_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(menu_item, field, value)
        
        try:
            db.commit()
            db.refresh(menu_item)
            return menu_item
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to update menu item: {str(e)}")
    
    @staticmethod
    def toggle_availability(
        db: DBSession,
        item_id: int
    ) -> Optional[MenuItem]:
        """
        Toggle menu item availability status.
        
        Args:
            db: Database session
            item_id: Menu item ID
            
        Returns:
            Updated menu item if found, None otherwise
        """
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.is_deleted == False
        ).first()
        
        if not menu_item:
            return None
        
        menu_item.is_available = not menu_item.is_available
        db.commit()
        db.refresh(menu_item)
        return menu_item
    
    @staticmethod
    def delete_menu_item(db: DBSession, item_id: int) -> bool:
        """
        Soft delete a menu item.
        
        Marks the item as deleted without removing it from the database,
        preserving historical order references.
        
        Args:
            db: Database session
            item_id: Menu item ID
            
        Returns:
            True if item was deleted, False if not found
        """
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.is_deleted == False
        ).first()
        
        if not menu_item:
            return False
        
        menu_item.is_deleted = True
        menu_item.is_available = False  # Also mark as unavailable
        db.commit()
        return True
