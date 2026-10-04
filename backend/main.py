"""
Smart Canteen Manager - Main FastAPI Application

A web application for Kiro University that enables students to browse menus
and place orders while providing canteen administrators with tools to manage
inventory, menu items, orders, and sales analytics.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings, validate_config
from backend.database import init_db
from backend.routes import auth
import logging


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Smart Canteen Manager API...")
    
    # Validate configuration
    validate_config()
    logger.info("Configuration validated")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    logger.info(f"Server starting on {settings.server_host}:{settings.server_port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Canteen Manager API...")


# Create FastAPI application
app = FastAPI(
    title="Smart Canteen Manager API",
    description="REST API for Kiro University Smart Canteen Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "Smart Canteen Manager API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Welcome message and API documentation link
    """
    return {
        "message": "Welcome to Smart Canteen Manager API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )
