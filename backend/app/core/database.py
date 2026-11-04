import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("gkjw_inventory.database")

# PostgreSQL Connection Pooling (SKILL.md & AGENTS.md: pool_size=5, max_overflow=10)
engine_kwargs = {
    "pool_pre_ping": True,
}

if settings.sync_database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    })

engine = create_engine(settings.sync_database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy database session per request
    and safely closes it upon completion.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
