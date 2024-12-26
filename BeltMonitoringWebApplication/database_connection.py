from sqlmodel import create_engine
from data import DATABASE_URL

engine = create_engine(DATABASE_URL)
