from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


def create_db_engine():
    """
    Initializes database engine.
    If MySQL is not reachable, gracefully falls back to local SQLite so localhost works immediately.
    """
    if "sqlite" in DATABASE_URL:
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    try:
        test_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
        )
        with test_engine.connect():
            pass
        return test_engine
    except Exception:
        print("[Notice] MySQL not reachable on localhost:3306. Using local SQLite (./url_shortener.db) for development.")
        return create_engine("sqlite:///./url_shortener.db", connect_args={"check_same_thread": False})


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a thread-safe database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
