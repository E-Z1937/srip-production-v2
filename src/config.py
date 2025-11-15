"""Configuration management"""
import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    API_TITLE: str = "SRIP - Smart Research Intelligence Platform"
    API_VERSION: str = "2.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    GROQ_API_KEY: str
    GROQ_DEFAULT_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_FALLBACK_MODELS: List[str] = Field(
        default_factory=lambda: ["mixtral-8x7b-32768", "llama-3.1-8b-instant"]
    )
    GROQ_MAX_RETRIES: int = 3
    GROQ_TIMEOUT: int = 60
    
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "SRIP-Production-V2"
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_HOUR: int = 100
    RATE_LIMIT_PER_MINUTE: int = 10
    
    ANALYSIS_TIMEOUT: int = 120
    MAX_TARGETS: int = 8
    MIN_RECOMMENDATIONS: int = 6
    
    ENABLE_CACHE: bool = True
    CACHE_MAX_SIZE: int = 1000
    ENABLE_GUARDRAILS: bool = True
    ENABLE_METRICS: bool = True
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/srip.log"
    
    @field_validator("GROQ_API_KEY")
    @classmethod
    def validate_groq_key(cls, v: str) -> str:
        if not v or len(v) < 10 or v == "your_groq_api_key_here":
            raise ValueError("Please set a valid GROQ_API_KEY in .env file")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
