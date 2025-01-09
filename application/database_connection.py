from sqlmodel import create_engine
from .config import Settings

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
