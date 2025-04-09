from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/contacts"
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"
    ORIGINS: tuple = ("http://localhost:3000", "http://localhost:8000")

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    MAIL_EXP_DAYS: int = 7

    CLD_NAME: str
    CLD_API_KEY: int = 12345678
    CLD_API_SECRET: str
    POSTGRES_DB: str = "contacts"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "your_password"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    return Settings()
