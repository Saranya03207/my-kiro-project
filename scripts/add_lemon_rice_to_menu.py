#!/usr/bin/env python3
"""
Data migration script to add Lemon Rice to the Smart Canteen menu.

This script adds the new Lemon Rice menu item to the database if it doesn't already exist.
Can be run multiple times safely (idempotent).

Usage:
    python scripts/add_lemon_rice_to_menu.py
"""
import sys
import os
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decimal import Decimal
from backend.database import SessionLocal
from backend.models.menu_item import MenuItem


def add_lemon_rice_to_menu():
    """
    Add Lemon Rice menu item to the database.
    
    This function is idempotent - it can be run multiple times safely.
    If Lemon Rice already exists, it will not be duplicated.
    """
    print("Adding Lemon Rice to Smart Canteen menu...")
    
    db = SessionLocal()
    try:
        # Check if Lemon Rice already exists
        existing_lemon_rice = db.query(MenuItem).filter(
            MenuItem.name == "Lemon Rice",
            MenuItem.is_deleted == False
        ).first()
        
        if existing_lemon_rice:
            print("✅ Lemon Rice already exists in the menu (ID: {})".format(existing_lemon_rice.id))
            print("   No changes needed.")
            return existing_lemon_rice.id
        
        # Create new Lemon Rice menu item
        lemon_rice = MenuItem(
            name="Lemon Rice",
            description="South Indian lemon rice prepared with lemon, rice, and tempered spices.",
            price=Decimal("70.00"),
            category="Meals",
            stock_quantity=20,
            stock_threshold=5,
            image_url="assets/food/lemon-rice.jpg",
            is_available=True,
            is_deleted=False
        )
        
        db.add(lemon_rice)
        db.commit()
        db.refresh(lemon_rice)
        
        print("✅ Successfully added Lemon Rice to the menu!")
        print(f"   - ID: {lemon_rice.id}")
        print(f"   - Name: {lemon_rice.name}")
        print(f"   - Description: {lemon_rice.description}")
        print(f"   - Price: ₹{lemon_rice.price}")
        print(f"   - Category: {lemon_rice.category}")
        print(f"   - Initial Stock: {lemon_rice.stock_quantity}")
        print(f"   - Stock Threshold: {lemon_rice.stock_threshold}")
        print(f"   - Available: {lemon_rice.is_available}")
        
        return lemon_rice.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding Lemon Rice to menu: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to run the migration."""
    try:
        item_id = add_lemon_rice_to_menu()
        print(f"\n🎉 Migration completed successfully!")
        print(f"Lemon Rice is now available in the Smart Canteen menu (ID: {item_id})")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
