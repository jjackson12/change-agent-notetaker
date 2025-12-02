from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./notetaker.db"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    
    # CORS
    allow_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Recall.ai API
    recall_api_key: str
    recall_api_base: str = "https://us-east-1.recall.ai/api/v1"
    
    # Change Agent API (placeholder - to be implemented)
    change_agent_api_url: str = "https://api.changeagent.ai"  # TODO: Update with actual URL
    change_agent_api_key: str = ""  # TODO: Add when available
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()