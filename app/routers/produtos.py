# app/routers/produtos.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.postgres import get_db
from app.models.models import Produtos
from app.schemas.schemas import ProdutoCreate, ProdutoOut
from app.services.image_service import buscar_imagem, salvar_imagem, deletar_imagem
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("/", response_model=ProdutoOut, status_code=201)
async def criar_produto(payload: ProdutoCreate, db: AsyncSession = Depends(get_db)):
    novo_produto = Produtos(**payload.model_dump())
    db.add(novo_produto)
    await db.commit()

    query = (
        select(Produtos)
        .where(Produtos.id_produto == novo_produto.id_produto)
        .options(joinedload(Produtos.categoria))
    )
    result = await db.execute(query)
    produto_completo = result.scalar_one()

    return produto_completo


@router.post("/{id_produto}/imagem", response_model=ProdutoOut)
async def upload_imagem(
    id_produto: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    query = (
        select(Produtos)
        .where(Produtos.id_produto == id_produto)
        .options(joinedload(Produtos.categoria))
    )
    result = await db.execute(query)
    produto = result.scalars().first()
    if not produto:
        raise HTTPException(404, "Produto não encontrado")

    content = await file.read()
    image_id = await salvar_imagem(id_produto, file.filename, content)

    ids_atuais = produto.mongo_image_ids.split(",") if produto.mongo_image_ids else []
    ids_atuais.append(image_id)
    produto.mongo_image_ids = ",".join(ids_atuais)

    await db.commit()
    await db.refresh(produto)
    return produto


@router.get("/{id_produto}/imagem/{image_id}")
async def ver_imagem(image_id: str, db: AsyncSession = Depends(get_db)):

    image = await buscar_imagem(image_id)
    filename = image["filename"].lower()

    if filename.endswith(".png"):
        mime = "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        mime = "image/jpeg"
    elif filename.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "application/octet-stream"

    return Response(content=image["content"], media_type=mime)


@router.get("/", response_model=list[ProdutoOut])
async def listar_produtos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Produtos).options(joinedload(Produtos.categoria)))
    return result.scalars().all()


@router.get("/{id_produto}", response_model=ProdutoOut)
async def buscar_produto(id_produto: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Produtos)
        .where(Produtos.id_produto == id_produto)
        .options(joinedload(Produtos.categoria))
    )
    result = await db.execute(query)
    produto = result.scalars().first()
    if not produto:
        raise HTTPException(404, "Produto não encontrado")
    return produto


@router.put("/{id_produto}", response_model=ProdutoOut)
async def atualizar_produto(
    id_produto: int, payload: ProdutoCreate, db: AsyncSession = Depends(get_db)
):
    query = (
        select(Produtos)
        .where(Produtos.id_produto == id_produto)
        .options(joinedload(Produtos.categoria))
    )
    result = await db.execute(query)
    produto = result.scalars().first()
    if not produto:
        raise HTTPException(404, "Produto não encontrado")
    for k, v in payload.model_dump().items():
        setattr(produto, k, v)
    await db.commit()
    await db.refresh(produto)
    return produto


@router.delete("/{id_produto}", status_code=204)
async def deletar_produto(id_produto: int, db: AsyncSession = Depends(get_db)):
    produto = await db.get(Produtos, id_produto)
    if not produto:
        raise HTTPException(404, "Produto não encontrado")
    # limpa imagens do Mongo antes
    if produto.mongo_image_ids:
        for img_id in produto.mongo_image_ids.split(","):
            await deletar_imagem(img_id)
    await db.delete(produto)
    await db.commit()
