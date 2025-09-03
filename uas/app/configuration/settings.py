from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the UAS application.
    """

    # Database configuration
    POSTGRESQL_DATABASE_URL: str
    # JWT configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    # Token expiration times (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SESSION_TOKEN_EXPIRE_MINUTES: int
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int

    # FastAPI-Mail configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    MAIL_TEMPLATE_FOLDER: str = str(Path(__file__).parent.parent / "templates")

    # Google OAuth2 configuration
    GOOGLE_CLIENT_ID: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_CLIENT_SECRET: str

    # Recaptcha
    RECAPTCHA_SITE_KEY: str
    RECAPTCHA_SECRET_KEY: str

    # Frontend URL
    FRONTEND_URL: str

    class Config:
        env_file = ".env"  # Specify the environment file if needed
        env_file_encoding = "utf-8"  # Encoding for the environment file
        case_sensitive = True  # Make environment variable names case-sensitive


settings = Settings()  # type: ignore # Create an instance of the settings
