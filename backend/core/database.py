from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from fastapi import Depends
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get absolute path to database
DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "zafir.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

logger.debug(f"Database file path: {DATABASE_FILE}")
logger.debug(f"Database URL: {DATABASE_URL}")

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # 30 second timeout
    },
    poolclass=StaticPool,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections every hour
    echo=True  # Enable SQL query logging
)

# Add engine event listeners for debugging
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.debug("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checkout")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        logger.debug("Yielding database session")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Closing database session")
        db.close()
