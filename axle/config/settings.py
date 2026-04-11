from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    axle_dashboard_port: int = 4000
    axle_db_path: str = "/var/lib/axle/axle.db"
    axle_vault_path: str = "/var/lib/axle/vault.enc"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
