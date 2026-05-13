# app/main.py  ← versão final
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis_client import connect_to_redis, close_redis_connection
from fastapi.middleware.cors import CORSMiddleware
from app.db.postgres import Base, engine
from app.core.config import settings

from app.routers import (
    usuarios,
    categorias,
    produtos,
    pedidos,
    carrinho,
    checkout,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await connect_to_mongo()
    await connect_to_redis()
    yield
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Mini Mercado — Postgres · MongoDB · Redis",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou coloque seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api"

app.include_router(usuarios.router, prefix=PREFIX)
app.include_router(categorias.router, prefix=PREFIX)
app.include_router(produtos.router, prefix=PREFIX)
app.include_router(pedidos.router, prefix=PREFIX)
app.include_router(carrinho.router, prefix=PREFIX)
app.include_router(checkout.router, prefix=PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Mini Mercado API",
        "bancos": ["PostgreSQL", "MongoDB", "Redis"],
        "docs": "/docs",
    }
