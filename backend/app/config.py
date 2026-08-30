"""Application settings, sourced from environment variables.

The single most important knob here is DATABASE_URL: it defaults to a local
SQLite file so the app and the test suite run with zero external dependencies,
but docker-compose and CI override it with a PostgreSQL URL. Because we use only
portable SQLAlchemy ORM constructs (no JSONB/array/Postgres-specific features),
the two engines behave identically. See the README "Decisions & Tradeoffs".
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./issuetracker.db"
    jwt_secret: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    password_min_length: int = 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
