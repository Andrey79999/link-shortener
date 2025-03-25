from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Get a database session.

    This function creates a new database session using the SessionLocal class and yields it.
    After the session is no longer needed, it is closed.

    Yields:
        Session: A new database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
