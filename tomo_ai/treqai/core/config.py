# treqai/core/config.py

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    SLACK_BOT_TOKEN: str | None = None
    SLACK_SIGNING_SECRET: str | None = None
    REQ_TARGET_CHANNEL: str | None = None

    NOTION_API_KEY: str | None = None
    NOTION_REQUEST_DB_ID: str | None = None

    GROQ_API_KEY: str | None = None

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"

settings = Settings()
