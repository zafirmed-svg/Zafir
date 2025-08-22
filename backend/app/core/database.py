from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from ..core.config import settings

# Crear el engine async de SQLAlchemy
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)

# Crear la sesión async
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base para los modelos declarativos
Base = declarative_base()

# Función para obtener la sesión de la base de datos
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()