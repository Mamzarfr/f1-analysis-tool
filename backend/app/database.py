# Database connection management for PostgreSQL

import os
import psycopg2
from collections.abc import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)


def _get_db_url() -> str:
    """
    Construct the PostgreSQL database URL from .env

    :return: A database URL
    """
    user = os.environ["POSTGRES_USER"]
    psw = os.environ["POSTGRES_PASSWORD"]
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.environ["POSTGRES_DB"]
    return f"postgresql://{user}:{psw}@{host}:{port}/{db}"


engine = create_engine(_get_db_url())
session_maker = sessionmaker(bind=engine, expire_on_commit=False)


def get_connection():
    """
    Return a connection to the PostgreSQL database.

    :return: A connection to the PostgreSQL database
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session, closing it after use.

    :return: A SQLAlchemy session, auto-closed after use
    """
    db = session_maker()
    try:
        yield db
    finally:
        db.close()
