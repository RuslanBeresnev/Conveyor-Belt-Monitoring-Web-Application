from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the secret parameters and connection configuration that are stored in the .env file
    """
    client_address: str
    client_port: int
    admin_username: str
    admin_password: str
    jwt_sign_secret_key: str
    auth_token_expiration_minutes: int
    database_url: str
    gmail_address: str
    telegram_bot_token: str
    telegram_user_name: str
    telegram_user_chat_id: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"
    )


settings = Settings()
