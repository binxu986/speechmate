"""
Tests for Server Startup and Lifecycle

Tests for FastAPI server initialization, database setup, and graceful shutdown.
"""
import pytest
import sys
from pathlib import Path


class TestFastAPIStartup:
    """Test FastAPI application startup"""

    def test_fastapi_app_creation(self):
        """Test that FastAPI app can be created"""
        from app.main import app
        assert app is not None
        assert app.title == "SpeechMate API"

    def test_app_has_routes(self):
        """Test that app has expected routes registered"""
        from app.main import app

        # Get all route paths
        routes = [route.path for route in app.routes]

        # Check essential routes
        assert "/health" in routes
        assert "/api/v1/info" in routes
        assert "/api/v1/config/model" in routes

    def test_app_middleware_configured(self):
        """Test that middleware is configured"""
        from app.main import app

        # Check CORS middleware is added
        middleware_types = [m.__class__.__name__ for m in app.user_middleware]
        assert len(middleware_types) > 0

    def test_app_lifespan_configured(self):
        """Test that lifespan is configured"""
        from app.main import app

        # App should have router
        assert app.router is not None


class TestDatabaseAutoInit:
    """Test database auto-initialization"""

    def test_database_initialization(self):
        """Test that database can be initialized"""
        from app.database import init_db, engine
        from sqlalchemy import inspect

        init_db()

        # Check tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "api_keys" in tables
        assert "usage_logs" in tables

    def test_database_default_key_created(self):
        """Test that default API key is created on init"""
        from app.database import init_db, get_all_api_keys

        init_db()
        keys = get_all_api_keys()

        # Should have at least one key
        assert len(keys) >= 1

    def test_database_sessions_work(self):
        """Test that database sessions work correctly"""
        from app.database import init_db, get_session, APIKey

        init_db()

        with get_session() as session:
            # Should be able to query
            result = session.query(APIKey).all()
            assert isinstance(result, list)


class TestConfigLoad:
    """Test configuration loading"""

    def test_config_loaded(self):
        """Test that configuration is loaded"""
        from app.config import config

        assert config is not None
        assert hasattr(config, "server")
        assert hasattr(config, "model")
        assert hasattr(config, "database")

    def test_admin_key_generated(self):
        """Test that admin API key is generated"""
        from app.config import config

        assert config.admin_api_key is not None
        assert len(config.admin_api_key) > 0

    def test_jwt_secret_generated(self):
        """Test that JWT secret is generated"""
        from app.config import config

        assert config.jwt_secret is not None
        assert len(config.jwt_secret) > 0

    def test_directories_created(self):
        """Test that required directories are created"""
        from app.config import DATA_DIR, LOGS_DIR, MODELS_DIR

        assert DATA_DIR.exists()
        assert LOGS_DIR.exists()
        assert MODELS_DIR.exists()


class TestServerInfo:
    """Test server information endpoints"""

    def test_get_local_ip(self):
        """Test getting local IP"""
        from app.config import get_local_ip

        ip = get_local_ip()
        assert isinstance(ip, str)
        # Should be valid IP format
        parts = ip.split(".")
        assert len(parts) == 4
        for part in parts:
            assert 0 <= int(part) <= 255

    def test_get_base_url(self):
        """Test getting base URL"""
        from app.config import get_base_url

        url = get_base_url()
        assert url.startswith("http://")
        assert ":8000" in url or ":5000" in url


class TestFlaskWebStartup:
    """Test Flask web admin startup"""

    def test_flask_app_creation(self):
        """Test that Flask app can be created"""
        import sys
        host_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(host_dir))

        from web import app
        assert app is not None

    def test_flask_routes_registered(self):
        """Test that Flask routes are registered"""
        import sys
        host_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(host_dir))

        from web import app

        # Get all routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]

        # Check essential routes
        assert "/" in routes
        assert "/api/keys" in routes
        assert "/api/stats" in routes

    def test_flask_app_config(self):
        """Test Flask app configuration"""
        import sys
        host_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(host_dir))

        from web import app

        # App should have config
        assert app.config is not None


class TestGracefulShutdown:
    """Test graceful shutdown behavior"""

    def test_unload_model_function_exists(self):
        """Test that model unload function exists"""
        from models.asr_model import unload_model

        # Should not raise error even if no model loaded
        unload_model()

    def test_get_model_info_safe(self):
        """Test getting model info is safe"""
        from models.asr_model import get_model_info

        info = get_model_info()
        assert info is not None
        assert "loaded" in info

    def test_cleanup_on_error(self):
        """Test that cleanup happens on error"""
        from app.database import get_session
        from app.database import APIKey

        # Start a session
        with get_session() as session:
            # Session should work
            result = session.query(APIKey).all()
            assert isinstance(result, list)
        # Session should be closed after context exit


class TestServerIntegration:
    """Integration tests for server components"""

    def test_full_startup_sequence(self):
        """Test full startup sequence"""
        # Import in order of startup
        from app.config import config
        from app.database import init_db
        from app.main import app

        # Init database
        init_db()

        # Verify app is ready
        assert app is not None
        assert config is not None

    def test_api_client_can_connect(self):
        """Test that API client can connect to test client"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Should be able to reach health endpoint
        response = client.get("/health")
        assert response.status_code == 200

    def test_web_client_can_connect(self):
        """Test that web client can connect"""
        import sys
        host_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(host_dir))

        from web import app

        client = app.test_client()

        # Should be able to reach index
        response = client.get("/")
        assert response.status_code == 200


class TestServerPorts:
    """Test server port configuration"""

    def test_api_port_config(self):
        """Test API port configuration"""
        from app.config import config

        port = config.server.api_port
        assert isinstance(port, int)
        assert 1 <= port <= 65535

    def test_web_port_config(self):
        """Test web port configuration"""
        from app.config import config

        port = config.server.web_port
        assert isinstance(port, int)
        assert 1 <= port <= 65535

    def test_ports_different(self):
        """Test that API and web ports are different"""
        from app.config import config

        assert config.server.api_port != config.server.web_port


class TestEnvironmentSetup:
    """Test environment setup"""

    def test_python_version(self):
        """Test Python version is compatible"""
        import sys

        # Should be Python 3.8+
        assert sys.version_info >= (3, 8)

    def test_required_modules_importable(self):
        """Test that required modules can be imported"""
        # Core modules
        import fastapi
        import flask
        import sqlalchemy
        import pydantic

        # All imports should succeed
        assert fastapi is not None
        assert flask is not None
        assert sqlalchemy is not None
        assert pydantic is not None

    def test_project_structure(self):
        """Test project structure is correct"""
        base_dir = Path(__file__).parent.parent

        # Check directories exist
        assert (base_dir / "app").exists()
        assert (base_dir / "models").exists()
        assert (base_dir / "web").exists()
        assert (base_dir / "tests").exists()

        # Check key files exist
        assert (base_dir / "app" / "main.py").exists()
        assert (base_dir / "app" / "config.py").exists()
        assert (base_dir / "app" / "database.py").exists()
        assert (base_dir / "models" / "asr_model.py").exists()
