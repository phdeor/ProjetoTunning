# app/db/postgres.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Cria a engine assíncrona
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# Dependência do FastAPI para injetar a sessão nas rotas
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
