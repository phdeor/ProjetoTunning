# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis_client import connect_to_redis, close_redis_connection
from app.core.config import settings
# from app.api import routes  <-- Suas rotas viriam aqui


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Executado ao ligar o servidor (Startup) ---
    await connect_to_mongo()
    await connect_to_redis()
    yield
    # --- Executado ao desligar o servidor (Shutdown) ---
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Exemplo de como registrar as rotas (que ficariam na pasta app/api/)
# app.include_router(routes.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API está rodando com Postgres, MongoDB e Redis!"}
