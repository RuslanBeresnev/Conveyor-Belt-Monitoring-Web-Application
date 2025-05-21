from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for secret parameters that are stored in the .env file
    """
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str
    GMAIL_ADDRESS: str
    TELEGRAM_USER_NAME: str
    TELEGRAM_USER_CHAT_ID: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"
    )


class UserPreferences(BaseSettings):
    """
    Settings for user preferences that are stored in the .user_preferences file and used by the client-side
    """
    SEND_TELEGRAM_NOTIFICATION_ON_NEW_DEFECT: bool
    SEND_GMAIL_NOTIFICATION_ON_NEW_DEFECT: bool
    SEND_REPORTS_BY_TELEGRAM: bool
    SEND_REPORTS_BY_GMAIL: bool

    model_config = SettingsConfigDict(
        env_file=".user_preferences",
        extra="forbid"
    )

