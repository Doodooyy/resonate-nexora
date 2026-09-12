from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXORA API"
    API_V1_STR: str = "/api/v1"
    
    # Auth configuration
    SECRET_KEY: str = "nexora_secret_hackathon_demo_key_123456" # For demo only
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Email SMTP configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./nexora.db"
    
    # LLM & Optional APIs
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    # Weights for Ranking Formula
    WEIGHT_SEMANTIC: float = 0.40
    WEIGHT_KEYWORD: float = 0.35
    WEIGHT_REQUIRED: float = 0.15
    WEIGHT_COHERENCE: float = 0.10
    
    model_config = {"env_file": ".env"}

@lru_cache()
def get_settings():
    return Settings()
