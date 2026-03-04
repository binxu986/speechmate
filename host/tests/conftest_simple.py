"""
Simplified conftest.py for SpeechMate tests
"""
import sys
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, APIKey
from app.config import config


@pytest.fixture(scope="function")
def isolated_db():
    """Create an isolated test database for each test"""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # Create a default test key
        session = SessionLocal()
        test_key = APIKey(
            key="test_default_key_12345678",
            name="Test Default Key",
            is_active=True
        )
        session.add(test_key)
        session.commit()
        session.close()

        yield {"db_path": db_path, "engine": engine, "SessionLocal": SessionLocal}

        # Cleanup
        engine.dispose()
        try:
            os.unlink(db_path)
        except:
            pass


@pytest.fixture(scope="function")
def web_client(isolated_db):
    """Create Flask test client with isolated database"""
    # Add host directory to path for imports
    host_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(host_dir))

    # Patch the database to use isolated test database
    with patch('app.database.engine', isolated_db['engine']):
        with patch('app.database.SessionLocal', isolated_db['SessionLocal']):
            with patch('web.init_db'):  # Skip init_db in web module
                from web import app as flask_app
                flask_app.config['TESTING'] = True
                yield flask_app.test_client()
