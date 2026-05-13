# app/services/image_service.py
from bson import ObjectId
from app.db.mongodb import db_mongo


async def salvar_imagem(produto_id: int, filename: str, content: bytes) -> str:
    """Salva binário no Mongo e devolve o ObjectId como string."""
    doc = {
        "produto_id": produto_id,
        "filename": filename,
        "content": content,  # bytes
    }
    result = await db_mongo.collection.insert_one(doc)
    return str(result.inserted_id)


async def buscar_imagem(image_id: str) -> dict | None:
    return await db_mongo.collection.find_one({"_id": ObjectId(image_id)})


async def deletar_imagem(image_id: str) -> bool:
    result = await db_mongo.collection.delete_one({"_id": ObjectId(image_id)})
    return result.deleted_count == 1
