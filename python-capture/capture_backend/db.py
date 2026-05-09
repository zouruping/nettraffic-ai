from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .db_models import Base


def create_engine_and_session_factory(database_url: str) -> tuple:
    engine = create_engine(database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, session_factory


def init_db(database_url: str) -> tuple:
    engine, session_factory = create_engine_and_session_factory(database_url)
    Base.metadata.create_all(bind=engine)
    return engine, session_factory


def get_db_session(session_factory) -> Session:
    return session_factory()
