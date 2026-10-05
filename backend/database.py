"""
Database connection and session management for Smart Canteen Manager.
Uses SQLAlchemy ORM with SQLite database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from backend.config import settings
import os


# Ensure data directory exists
data_dir = os.path.dirname(settings.database_url.replace("sqlite:///", ""))
if data_dir and not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.log_level == "DEBUG"  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Session:
    """
    Get database session.

    Usage in FastAPI route:
        def my_route(db: Session = Depends(get_db)):
            ...

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Called on application startup.
    """
    # Import all models to ensure they are registered with Base
    from backend.models import menu_item, order, order_item, session

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Ensure image_url column exists in menu_items if table already existed
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE menu_items ADD COLUMN image_url VARCHAR(500)"))
            conn.commit()
    except Exception:
        pass
