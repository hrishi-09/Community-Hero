"""
Configuration settings for Community Hero
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/community_hero"
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "community-hero-kolkata-secret-key-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # SMS (Twilio or MSG91)
    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "twilio")  # twilio | msg91
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    # MSG91 (Alternative Indian SMS provider)
    MSG91_AUTH_KEY: str = os.getenv("MSG91_AUTH_KEY", "")
    MSG91_SENDER_ID: str = os.getenv("MSG91_SENDER_ID", "CMHERO")
    MSG91_TEMPLATE_ID: str = os.getenv("MSG91_TEMPLATE_ID", "")

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    # App
    ENV: str = os.getenv("ENV", "production")
    APP_NAME: str = "Community Hero Kolkata"

    class Config:
        env_file = ".env"


settings = Settings()
