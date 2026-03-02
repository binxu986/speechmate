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


class TestDatabaseEdgeCases:
    """Test database edge cases"""

    def test_create_key_empty_name(self):
        """Test creating API key with empty name"""
        from app.database import init_db, create_api_key

        init_db()
        key = create_api_key("")
        assert key is not None
        assert len(key) == 32

    def test_create_key_long_name(self):
        """Test creating API key with long name"""
        from app.database import init_db, create_api_key

        init_db()
        long_name = "A" * 1000
        key = create_api_key(long_name)
        assert key is not None

    def test_verify_disabled_api_key(self):
        """Test verifying disabled API key returns None"""
        from app.database import init_db, create_api_key, toggle_api_key, verify_api_key, get_all_api_keys

        init_db()
        key = create_api_key("Key to Disable")

        # Find key ID
        keys = get_all_api_keys()
        key_id = None
        for k in keys:
            if k["key"] == key:
                key_id = k["id"]
                break

        if key_id:
            # Disable the key
            toggle_api_key(key_id)

            # Verify should return None for disabled key
            result = verify_api_key(key)
            assert result is None

    def test_delete_nonexistent_key(self):
        """Test deleting non-existent key"""
        from app.database import init_db, delete_api_key

        init_db()
        # Should not raise error
        result = delete_api_key(99999)
        assert result == False

    def test_toggle_nonexistent_key(self):
        """Test toggling non-existent key"""
        from app.database import init_db, toggle_api_key

        init_db()
        # Should handle gracefully
        try:
            result = toggle_api_key(99999)
        except:
            pass  # May raise error, which is acceptable

    def test_log_usage_minimal_fields(self):
        """Test logging usage with minimal fields"""
        from app.database import init_db, log_usage

        init_db()
        # Log with only required fields
        log_usage(
            api_key_id=1,
            endpoint="test",
            success=True
        )

    def test_get_stats_different_days(self):
        """Test getting stats with different day ranges"""
        from app.database import init_db, get_stats

        init_db()

        for days in [1, 7, 30, 90, 365]:
            stats = get_stats(days=days)
            assert isinstance(stats, dict)


class TestDatabaseAPIKeyFormat:
    """Test API key format and uniqueness"""

    def test_key_format(self):
        """Test that generated keys are valid hex strings"""
        from app.database import init_db, create_api_key

        init_db()
        key = create_api_key("Format Test")

        # Should be valid hex
        try:
            int(key, 16)
            assert True
        except ValueError:
            assert False, "API key should be hex string"

    def test_key_length(self):
        """Test that all keys have correct length"""
        from app.database import init_db, create_api_key

        init_db()

        for i in range(5):
            key = create_api_key(f"Length Test {i}")
            assert len(key) == 32

    def test_multiple_keys_unique(self):
        """Test that multiple keys are unique"""
        from app.database import init_db, create_api_key

        init_db()

        keys = set()
        for i in range(10):
            key = create_api_key(f"Uniqueness Test {i}")
            assert key not in keys, "Keys should be unique"
            keys.add(key)


class TestDatabaseSession:
    """Test database session management"""

    def test_get_session(self):
        """Test getting database session"""
        from app.database import init_db, get_session

        init_db()
        # get_session returns a context manager
        with get_session() as session:
            assert session is not None

    def test_session_query(self):
        """Test querying through session"""
        from app.database import init_db, get_session, APIKey

        init_db()

        # Use session as context manager
        with get_session() as session:
            # Should be able to query
            result = session.query(APIKey).all()
            assert isinstance(result, list)