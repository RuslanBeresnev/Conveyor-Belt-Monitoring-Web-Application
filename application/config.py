from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the secret parameters and connection configuration that are stored in the .env file
    """
    CLIENT_ADDRESS: str
    CLIENT_PORT: int
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    JWT_SIGN_SECRET_KEY: str
    AUTH_TOKEN_EXPIRATION_MINUTES: int
    DATABASE_URL: str
    GMAIL_ADDRESS: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_USER_NAME: str
    TELEGRAM_USER_CHAT_ID: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"
    )


settings = Settings()
