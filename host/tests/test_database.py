"""
Tests for Database Module
"""
import pytest
from pathlib import Path


class TestDatabaseImport:
    """Test database module imports"""

    def test_import_database(self):
        """Test that database module can be imported"""
        from app import database
        assert database is not None

    def test_import_functions(self):
        """Test that all required functions are available"""
        from app.database import (
            init_db,
            get_session,
            verify_api_key,
            log_usage,
            get_stats,
            get_all_api_keys,
            create_api_key,
            delete_api_key,
            toggle_api_key
        )


class TestDatabaseInit:
    """Test database initialization"""

    def test_init_db(self):
        """Test database initialization"""
        from app.database import init_db

        # Should not raise error
        init_db()

    def test_init_db_creates_tables(self):
        """Test that init_db creates tables"""
        from app.database import init_db, engine, Base

        init_db()

        # Check that tables exist
        inspector = engine.dialect.get_table_names(engine.connect())
        assert "api_keys" in inspector
        assert "usage_logs" in inspector


class TestAPIKeyOperations:
    """Test API key operations"""

    def test_create_api_key(self):
        """Test creating API key"""
        from app.database import init_db, create_api_key

        init_db()
        key = create_api_key("Test Key")

        assert isinstance(key, str)
        assert len(key) == 32  # 16 bytes = 32 hex chars

    def test_get_all_api_keys(self):
        """Test getting all API keys"""
        from app.database import init_db, get_all_api_keys

        init_db()
        keys = get_all_api_keys()

        assert isinstance(keys, list)

    def test_verify_valid_api_key(self):
        """Test verifying valid API key"""
        from app.database import init_db, create_api_key, verify_api_key

        init_db()
        key = create_api_key("Test Key for Verify")

        result = verify_api_key(key)
        assert result is not None
        assert result["key"] == key
        assert result["name"] == "Test Key for Verify"

    def test_verify_invalid_api_key(self):
        """Test verifying invalid API key"""
        from app.database import init_db, verify_api_key

        init_db()
        result = verify_api_key("invalid_key_12345")
        assert result is None

    def test_toggle_api_key(self):
        """Test toggling API key status"""
        from app.database import init_db, create_api_key, toggle_api_key, verify_api_key

        init_db()
        key = create_api_key("Test Key for Toggle")

        # Toggle to disabled
        is_active = toggle_api_key(1)  # Assuming first key
        assert isinstance(is_active, bool)

    def test_delete_api_key(self):
        """Test deleting API key"""
        from app.database import init_db, create_api_key, delete_api_key, get_all_api_keys

        init_db()

        # Get initial count
        initial_keys = get_all_api_keys()
        initial_count = len(initial_keys)

        # Create and delete a key
        key = create_api_key("Test Key for Delete")
        keys_after_create = get_all_api_keys()
        assert len(keys_after_create) == initial_count + 1

        # Find the key we just created
        key_id = None
        for k in keys_after_create:
            if k["key"] == key:
                key_id = k["id"]
                break

        if key_id:
            delete_api_key(key_id)
            keys_after_delete = get_all_api_keys()
            assert len(keys_after_delete) == initial_count


class TestUsageLogging:
    """Test usage logging"""

    def test_log_usage_success(self):
        """Test logging successful usage"""
        from app.database import init_db, get_all_api_keys, log_usage

        init_db()
        keys = get_all_api_keys()

        if keys:
            log_usage(
                api_key_id=keys[0]["id"],
                endpoint="transcribe",
                audio_duration=5.0,
                processing_time=1.5,
                source_lang="en",
                success=True
            )

    def test_log_usage_failure(self):
        """Test logging failed usage"""
        from app.database import init_db, get_all_api_keys, log_usage

        init_db()
        keys = get_all_api_keys()

        if keys:
            log_usage(
                api_key_id=keys[0]["id"],
                endpoint="transcribe",
                processing_time=0.5,
                success=False,
                error_message="Test error"
            )

    def test_get_stats(self):
        """Test getting usage statistics"""
        from app.database import init_db, get_stats

        init_db()
        stats = get_stats(days=30)

        assert isinstance(stats, dict)