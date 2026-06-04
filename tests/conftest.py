import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base, get_db
from src.models import LeadModel  # Required for Base.metadata to know about the table
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
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
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

from src.repository import LeadRepository
import sqlite3

@pytest.fixture
def in_memory_repo():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)  # Close the OS file descriptor immediately so SQLite can own it
    
    repo = LeadRepository(db_path)
    
    conn = sqlite3.connect(repo.db_path)
    try:
        conn.execute("""
            CREATE TABLE leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                source TEXT,
                stage TEXT DEFAULT 'New',
                notes TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """)
        conn.commit()
    finally:
        conn.close()

    yield repo
    
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # Just in case Windows still complains
