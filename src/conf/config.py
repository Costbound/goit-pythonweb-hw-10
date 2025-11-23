from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    VERIFICATION_TOKEN_EXPIRE_SECONDS: int

    SMTP_USER: str
    SMTP_PASSWORD: SecretStr
    SMTP_FROM: EmailStr
    SMTP_PORT: int
    SMTP_HOST: str
    SMTP_FROM_NAME: str = "Contact Book"
    SMTP_STARTTLS: bool = False
    SMTP_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()  # type: ignore[arg-type]
