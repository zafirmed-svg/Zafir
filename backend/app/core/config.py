from pathlib import Path
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

class Settings:
    def __init__(self):
        # Load environment variables
        ROOT_DIR = Path(__file__).parent.parent.parent
        load_dotenv(ROOT_DIR / '.env')
        
        # MongoDB settings
        self.mongo_url: str = os.environ['MONGO_URL']
        self.db_name: str = os.environ['DB_NAME']
        
        # CORS settings
        self.cors_origins: list = os.environ.get('CORS_ORIGINS', '*').split(',')

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls.client is None:
            settings = Settings()
            cls.client = AsyncIOMotorClient(settings.mongo_url)
        return cls.client

    @classmethod
    def close_client(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None

settings = Settings()
