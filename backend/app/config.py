from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str = "twogether"
    postgres_password: str = "change-me"
    postgres_db: str = "twogether"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url_override: str|None = Field(None, validation_alias="DATABASE_URL")
    testing: bool = False
    secret_key: str = Field("change-me-in-production", validation_alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    max_upload_size: int = Field(10 * 1024 * 1024, validation_alias="UPLOAD_MAX_SIZE_BYTES")
    registration_enabled: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def database_url(self):
        if self.testing and self.database_url_override:
            return self.database_url_override
        password = quote_plus(self.postgres_password)
        return f"postgresql+psycopg2://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
    @property
    def upload_path(self):
        p=Path(self.upload_dir); p.mkdir(parents=True, exist_ok=True); return p
@lru_cache
def get_settings(): return Settings()
settings = get_settings()
