from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./twogether.db"
    secret_key: str = Field("change-me-in-production", validation_alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    max_upload_size: int = Field(10 * 1024 * 1024, validation_alias="UPLOAD_MAX_SIZE_BYTES")
    registration_enabled: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
    @property
    def upload_path(self):
        p=Path(self.upload_dir); p.mkdir(parents=True, exist_ok=True); return p
@lru_cache
def get_settings(): return Settings()
settings = get_settings()
