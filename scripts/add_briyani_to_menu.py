#!/usr/bin/env python3
"""
Data migration script to add Briyani to the Smart Canteen menu.

This script adds the new Briyani menu item to the database if it doesn't already exist.
Can be run multiple times safely (idempotent).

Usage:
    python scripts/add_briyani_to_menu.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decimal import Decimal
from backend.database import SessionLocal
from backend.models.menu_item import MenuItem


def add_briyani_to_menu():
    """
    Add Briyani menu item to the database.
    
    This function is idempotent - it can be run multiple times safely.
    If Briyani already exists, it will not be duplicated.
    """
    print("Adding Briyani to Smart Canteen menu...")
    
    db = SessionLocal()
    try:
        # Check if Briyani already exists
        existing_briyani = db.query(MenuItem).filter(
            MenuItem.name == "Briyani",
            MenuItem.is_deleted == False
        ).first()
        
        if existing_briyani:
            print("✅ Briyani already exists in the menu (ID: {})".format(existing_briyani.id))
            print("   No changes needed.")
            return existing_briyani.id
        
        # Create new Briyani menu item
        briyani = MenuItem(
            name="Briyani",
            description="South Indian style chicken briyani served as a complete meal.",
            price=Decimal("120.00"),
            category="Meals", 
            stock_quantity=20,
            stock_threshold=5,
            image_url="assets/food/biryani.jpg",
            is_available=True,
            is_deleted=False
        )
        
        db.add(briyani)
        db.commit()
        db.refresh(briyani)
        
        print("✅ Successfully added Briyani to the menu!")
        print(f"   - ID: {briyani.id}")
        print(f"   - Name: {briyani.name}")
        print(f"   - Description: {briyani.description}")
        print(f"   - Price: ₹{briyani.price}")
        print(f"   - Category: {briyani.category}")
        print(f"   - Initial Stock: {briyani.stock_quantity}")
        print(f"   - Stock Threshold: {briyani.stock_threshold}")
        print(f"   - Available: {briyani.is_available}")
        
        return briyani.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding Briyani to menu: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to run the migration."""
    try:
        item_id = add_briyani_to_menu()
        print(f"\n🎉 Migration completed successfully!")
        print(f"Briyani is now available in the Smart Canteen menu (ID: {item_id})")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()