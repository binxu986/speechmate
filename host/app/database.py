"""
SpeechMate Database Module
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.config import config

Base = declarative_base()


class APIKey(Base):
    """API Key model"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)


class UsageLog(Base):
    """Usage log model"""
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(Integer, nullable=False, index=True)
    endpoint = Column(String(50), nullable=False)  # transcribe, translate
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    audio_duration = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    source_lang = Column(String(10), nullable=True)
    target_lang = Column(String(10), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)


class ModelConfigDB(Base):
    """Model configuration stored in database"""
    __tablename__ = "model_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create engine
engine = create_engine(f"sqlite:///{config.database.db_path}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

    # Create default API key if not exists
    with get_session() as session:
        if session.query(APIKey).count() == 0:
            import secrets
            default_key = APIKey(
                key=secrets.token_hex(16),
                name="Default Key",
                is_active=True
            )
            session.add(default_key)
            session.commit()
            print(f"Created default API key: {default_key.key}")


@contextmanager
def get_session():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def verify_api_key(api_key: str) -> Optional[APIKey]:
    """Verify API key and return the key object if valid"""
    with get_session() as session:
        key_obj = session.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        if key_obj:
            key_obj.last_used_at = datetime.utcnow()
            session.commit()
        return key_obj


def log_usage(
    api_key_id: int,
    endpoint: str,
    audio_duration: float = 0.0,
    processing_time: float = 0.0,
    source_lang: str = None,
    target_lang: str = None,
    success: bool = True,
    error_message: str = None
):
    """Log API usage"""
    with get_session() as session:
        log = UsageLog(
            api_key_id=api_key_id,
            endpoint=endpoint,
            audio_duration=audio_duration,
            processing_time=processing_time,
            source_lang=source_lang,
            target_lang=target_lang,
            success=success,
            error_message=error_message
        )
        session.add(log)


def get_stats(api_key_id: Optional[int] = None, days: int = 30) -> dict:
    """Get usage statistics"""
    with get_session() as session:
        from sqlalchemy import func

        start_date = datetime.utcnow() - timedelta(days=days)

        query = session.query(
            UsageLog.api_key_id,
            UsageLog.endpoint,
            func.date(UsageLog.timestamp).label("date"),
            func.count().label("count")
        ).filter(
            UsageLog.timestamp >= start_date
        )

        if api_key_id:
            query = query.filter(UsageLog.api_key_id == api_key_id)

        results = query.group_by(
            UsageLog.api_key_id,
            UsageLog.endpoint,
            func.date(UsageLog.timestamp)
        ).all()

        # Organize stats
        stats = {}
        for row in results:
            key_id = row.api_key_id
            if key_id not in stats:
                stats[key_id] = {
                    "daily": {},
                    "total_transcribe": 0,
                    "total_translate": 0
                }

            date_str = str(row.date)
            if date_str not in stats[key_id]["daily"]:
                stats[key_id]["daily"][date_str] = {"transcribe": 0, "translate": 0}

            stats[key_id]["daily"][date_str][row.endpoint] = row.count
            if row.endpoint == "transcribe":
                stats[key_id]["total_transcribe"] += row.count
            else:
                stats[key_id]["total_translate"] += row.count

        return stats


def get_all_api_keys() -> List[dict]:
    """Get all API keys with stats"""
    with get_session() as session:
        keys = session.query(APIKey).all()
        result = []
        for key in keys:
            result.append({
                "id": key.id,
                "key": key.key,
                "name": key.name,
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat() if key.created_at else None,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None
            })
        return result


def create_api_key(name: str) -> str:
    """Create new API key"""
    import secrets
    with get_session() as session:
        key = secrets.token_hex(16)
        new_key = APIKey(key=key, name=name)
        session.add(new_key)
        return key


def delete_api_key(key_id: int) -> bool:
    """Delete API key"""
    with get_session() as session:
        key = session.query(APIKey).filter(APIKey.id == key_id).first()
        if key:
            session.delete(key)
            return True
        return False


def toggle_api_key(key_id: int) -> bool:
    """Toggle API key active status"""
    with get_session() as session:
        key = session.query(APIKey).filter(APIKey.id == key_id).first()
        if key:
            key.is_active = not key.is_active
            return key.is_active
        return False
