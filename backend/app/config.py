"""Application settings, loaded from the project-root .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# backend/app/config.py -> project root is two levels up from app/
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # .env also holds frontend/scraper keys we don't need here
    )

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "honeybee_listings"
    mysql_user: str = "listings_app"
    mysql_password: str
    # Path to the CA certificate of a hosted MySQL (e.g. Aiven); enables verified TLS. Unset locally.
    mysql_ssl_ca: str | None = None
    cors_origins: str = "http://localhost:5173"

    @property
    def database_url(self) -> URL:
        # URL.create escapes special characters (@, #, :) in the password for us
        return URL.create(
            drivername="mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_db,
            query={"charset": "utf8mb4"},
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
