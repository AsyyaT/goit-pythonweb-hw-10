from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.conf.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata_ = MetaData()


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata_


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
