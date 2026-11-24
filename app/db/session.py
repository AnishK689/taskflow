from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# The engine is the core interface to the DB.
# pool_pre_ping=True: before handing out a connection from the pool,
# SQLAlchemy does a lightweight "SELECT 1" to check it's still alive.
# This prevents "connection closed" errors after the DB restarts or idles.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # echo=True logs every SQL query — useful for learning/debugging
    echo=settings.DEBUG,
)

# sessionmaker creates a factory for Session objects.
# autocommit=False → we control when transactions are committed.
# autoflush=False → SQLAlchemy won't auto-send pending changes to DB
#                   before every query. We flush manually or on commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All models inherit from this — SQLAlchemy tracks them for migrations."""
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session per request.

    The 'yield' pattern ensures the session is always closed after the
    request finishes — even if an exception is raised.

    Usage in a route:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
