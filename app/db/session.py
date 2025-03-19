from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/shortener")


# if DATABASE_URL is None:
#     raise Exception("DATABASE_URL is None")

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
