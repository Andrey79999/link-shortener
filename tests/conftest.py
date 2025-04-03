import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import dotenv
from sqlalchemy import inspect
import logging

dotenv.load_dotenv(override=True)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://user:password@localhost:5433/test_shortener"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import sys
import os
sys.path.append(os.path.abspath("app"))

from main import app
from db.session import Base, get_db

from models.link import Link
from models.user import User, AuthMethod

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        print("Existing tables:", inspector.get_table_names())
    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            db.begin_nested()
            yield db
        finally:
            db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def final_check(engine):
    yield
    with engine.connect() as conn:
        print("\nFinal tables:", inspect(engine).get_table_names())