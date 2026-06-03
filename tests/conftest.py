import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app

# We won't actually be able to import TestClient if fastapi is not installed
# but this is the standard FastAPI TestClient implementation for the new stack.
try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

@pytest.fixture(scope="session")
def db_engine():
    # Use an in-memory SQLite database for testing the FastAPI application
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    if not TestClient:
        pytest.skip("FastAPI not installed")
        
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
