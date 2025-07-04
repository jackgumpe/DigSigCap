import os
import sqlite3
import msgpack
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config.settings import config
from utils.logger import setup_logger
import platform

Base = declarative_base()
logger = setup_logger("Database")

# Windows-specific path handling
if platform.system() == "Windows":
    DB_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'DigitalSignalCapture', 'signals.db')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    config.DATABASE_URL = f"sqlite:///{DB_PATH}"

class DigitalSignal(Base):
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float, index=True)
    source_type = Column(String(20))  # network/screen/audio
    source_name = Column(String(50))  # YouTube/GameName/etc
    data_format = Column(String(10))  # text/image/audio/packet
    raw_data = Column(LargeBinary)    # Compressed binary data
    processed_text = Column(String)   # Extracted text content
    metadata = Column(String)         # JSON-like metadata

def init_db():
    """Initialize database with connection pooling"""
    engine = create_engine(
        config.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    logger.info(f"Database initialized at {config.DATABASE_URL}")
    return Session

# ... rest of database functions ...

def compress_data(data):
    """Compress data using MessagePack"""
    try:
        return msgpack.packb(data)
    except Exception as e:
        logger.error(f"Data compression failed: {str(e)}")
        return b''

def decompress_data(compressed):
    """Decompress MessagePack data"""
    try:
        return msgpack.unpackb(compressed)
    except Exception as e:
        logger.error(f"Data decompression failed: {str(e)}")
        return {}

def store_signal(session, signal_data):
    """Store processed signal in database"""
    try:
        signal = DigitalSignal(
            timestamp=datetime.now().timestamp(),
            source_type=signal_data.get('source_type'),
            source_name=signal_data.get('source_name'),
            data_format=signal_data.get('format'),
            raw_data=compress_data(signal_data.get('raw_data')),
            processed_text=signal_data.get('processed_text', ''),
            metadata=signal_data.get('metadata', '')
        )
        session.add(signal)
        session.commit()
        logger.debug(f"Stored signal from {signal_data.get('source_name')}")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error storing signal: {str(e)}")
        return False