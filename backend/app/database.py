"""
SQLAlchemy engine/session setup. Uses SQLite by default (zero external
dependency, ideal for a 48-hour take-home), but DATABASE_URL can be
pointed at Postgres/MySQL without any other code changes since all
access goes through SQLAlchemy's ORM layer.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
