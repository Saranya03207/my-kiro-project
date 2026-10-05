#!/usr/bin/env python3
"""
Data migration script to add Curd Rice to the Smart Canteen menu.

This script adds the new Curd Rice menu item to the database if it doesn't already exist.
Can be run multiple times safely (idempotent).

Usage:
    python scripts/add_curd_rice_to_menu.py
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


def add_curd_rice_to_menu():
    """
    Add Curd Rice menu item to the database.
    
    This function is idempotent - it can be run multiple times safely.
    If Curd Rice already exists, it will not be duplicated.
    """
    print("Adding Curd Rice to Smart Canteen menu...")
    
    db = SessionLocal()
    try:
        # Check if Curd Rice already exists
        existing_curd_rice = db.query(MenuItem).filter(
            MenuItem.name == "Curd Rice",
            MenuItem.is_deleted == False
        ).first()
        
        if existing_curd_rice:
            print("✅ Curd Rice already exists in the menu (ID: {})".format(existing_curd_rice.id))
            print("   No changes needed.")
            return existing_curd_rice.id
        
        # Create new Curd Rice menu item
        curd_rice = MenuItem(
            name="Curd Rice",
            description="South Indian curd rice made with rice, fresh curd and mild tempered spices.",
            price=Decimal("60.00"),
            category="Meals",
            stock_quantity=20,
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        )
        
        db.add(curd_rice)
        db.commit()
        db.refresh(curd_rice)
        
        print("✅ Successfully added Curd Rice to the menu!")
        print(f"   - ID: {curd_rice.id}")
        print(f"   - Name: {curd_rice.name}")
        print(f"   - Description: {curd_rice.description}")
        print(f"   - Price: ₹{curd_rice.price}")
        print(f"   - Category: {curd_rice.category}")
        print(f"   - Initial Stock: {curd_rice.stock_quantity}")
        print(f"   - Stock Threshold: {curd_rice.stock_threshold}")
        print(f"   - Available: {curd_rice.is_available}")
        
        return curd_rice.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding Curd Rice to menu: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to run the migration."""
    try:
        item_id = add_curd_rice_to_menu()
        print(f"\n🎉 Migration completed successfully!")
        print(f"Curd Rice is now available in the Smart Canteen menu (ID: {item_id})")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
