from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    """
    Settings for the UAS application.
    """
    
    # Database configuration
    POSTGRESQL_DATABASE_URL: str

    # JWT configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    # FastAPI-Mail configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    MAIL_TEMPLATE_FOLDER: str = str(Path(__file__).parent.parent / "templates")

    # Frontend URL
    FRONTEND_URL: str

    class Config:
        env_file = ".env"  # Specify the environment file if needed
        env_file_encoding = "utf-8"  # Encoding for the environment file
        case_sensitive = True  # Make environment variable names case-sensitive


settings = Settings()  # Create an instance of the settings
