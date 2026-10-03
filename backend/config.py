"""
Configuration management for Smart Canteen Manager.
Loads configuration from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional, List
import os


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    Never hardcode secrets in code.
    """
    
    # Database
    database_url: str = "sqlite:///./data/canteen.db"
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    session_expiry_hours: int = 24
    rate_limit_per_minute: int = 100
    
    # AI Service (optional, sensitive)
    ai_service_url: Optional[str] = None
    ai_service_api_key: Optional[str] = None
    ai_service_timeout: int = 5
    ai_service_enabled: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/canteen.log"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )
        
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()


def validate_config():
    """
    Validate configuration and fail fast if misconfigured.
    
    Raises:
        ValueError: If configuration is invalid
    """
    if settings.secret_key == "CHANGE_THIS_IN_PRODUCTION":
        import logging
        logging.warning(
            "SECRET_KEY is using default value. "
            "Please set SECRET_KEY environment variable in production."
        )
    
    if settings.ai_service_enabled and not settings.ai_service_url:
        import logging
        logging.warning(
            "AI service enabled but URL not configured. Disabling AI service."
        )
        settings.ai_service_enabled = False
    
    # Ensure log directory exists
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
