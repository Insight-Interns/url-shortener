import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "URL Shortener API"
    API_V1_STR: str = "/api/v1"
    
    # JWT & Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-insecure-super-secret-key-change-in-production-123456789012")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Password Security
    BCRYPT_ROUNDS: int = 12
    
    # Analytics & Privacy
    ANALYTICS_SALT: str = os.getenv("ANALYTICS_SALT", "secure-analytics-privacy-salt-987654321")
    
    # URL Security Limits
    MAX_URL_LENGTH: int = 2048
    MIN_ALIAS_LENGTH: int = 3
    MAX_ALIAS_LENGTH: int = 30
    ALLOWED_SCHEMES: List[str] = ["http", "https"]
    
    # Reserved short codes that cannot be registered as custom aliases
    RESERVED_ALIASES: List[str] = [
        "api", "auth", "login", "register", "signup", "logout",
        "admin", "stats", "analytics", "dashboard", "docs", "redoc",
        "openapi", "health", "metrics", "null", "undefined", "favicon"
    ]
    
    # Rate Limiting (Requests per hour)
    RATE_LIMIT_ANONYMOUS_PER_HOUR: int = 10
    RATE_LIMIT_REGISTERED_PER_HOUR: int = 100
    RATE_LIMIT_PREMIUM_PER_HOUR: int = 10000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://url_user:url_password@localhost:3306/url_shortener_db"
    )


settings = SecuritySettings()
