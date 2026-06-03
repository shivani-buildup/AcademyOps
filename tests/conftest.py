import pytest
import tempfile
import os
import sqlite3
from src.repository import LeadRepository
from src.api import app
from src.db_init import init_db
from unittest.mock import patch

@pytest.fixture
def in_memory_repo():
    # Use a real temp file so connections work identically to production
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Initialize the schema
    init_db(path)
    
    repo = LeadRepository(path)
    yield repo
    
    # Cleanup
    try:
        os.remove(path)
    except OSError:
        pass

@pytest.fixture
def test_client(in_memory_repo):
    # Patch the get_repo in api.py to return our in-memory repo
    with patch('src.api.get_repo', return_value=in_memory_repo):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
