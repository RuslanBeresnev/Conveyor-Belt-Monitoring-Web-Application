from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for secret parameters that are stored in the .env file
    """
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="forbid"
    )
