"""
Verification script to check if Smart Canteen Manager setup is correct.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_imports():
    """Verify all required modules can be imported"""
    print("✓ Checking Python imports...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        from backend.config import settings
        from backend.database import Base, engine, init_db
        from backend.models.menu_item import MenuItem
        from backend.models.order import Order
        from backend.models.order_item import OrderItem
        from backend.models.session import Session
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_database():
    """Verify database can be created and tables exist"""
    print("✓ Checking database setup...")
    try:
        from backend.database import init_db, engine
        init_db()
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['menu_items', 'orders', 'order_items', 'sessions']
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def verify_config():
    """Verify configuration is loaded correctly"""
    print("✓ Checking configuration...")
    try:
        from backend.config import settings, validate_config
        
        print(f"  ✓ Database URL: {settings.database_url}")
        print(f"  ✓ Server: {settings.server_host}:{settings.server_port}")
        print(f"  ✓ Log level: {settings.log_level}")
        
        validate_config()
        print("  ✓ Configuration valid")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def verify_directories():
    """Verify all required directories exist"""
    print("✓ Checking directory structure...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_dirs = [
        'backend/models',
        'backend/schemas',
        'backend/routes',
        'backend/services',
        'backend/middleware',
        'backend/utils',
        'frontend/html',
        'frontend/css',
        'frontend/js',
        'frontend/tests',
        'tests/unit',
        'tests/properties',
        'tests/integration',
        'data',
        'logs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Smart Canteen Manager - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Imports", verify_imports),
        ("Directory Structure", verify_directories),
        ("Configuration", verify_config),
        ("Database", verify_database)
    ]
    
    results = []
    for name, check_func in checks:
        print()
        result = check_func()
        results.append((name, result))
    
    print()
    print("=" * 60)
    print("Verification Results:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All checks passed! Setup is complete.")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
