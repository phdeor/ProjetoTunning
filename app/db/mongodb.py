# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


db_mongo = MongoDB()


async def connect_to_mongo():
    print("Conectando ao MongoDB...")
    db_mongo.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_mongo.db = db_mongo.client[settings.MONGODB_DATABASE_NAME]
    print("MongoDB conectado!")


async def close_mongo_connection():
    if db_mongo.client is not None:
        db_mongo.client.close()
        print("MongoDB desconectado.")
