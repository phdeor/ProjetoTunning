# app/routers/categorias.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_db
from app.models.models import Categorias
from app.schemas.schemas import CategoriaCreate, CategoriaOut
from app.core.deps import verificar_adm

router = APIRouter(prefix="/categorias", tags=["Categorias"])


# ── Públicas ──────────────────────────────────────────────


@router.get("/", response_model=list[CategoriaOut])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categorias))
    return result.scalars().all()


@router.get("/{id_categoria}", response_model=CategoriaOut)
async def buscar_categoria(id_categoria: int, db: AsyncSession = Depends(get_db)):
    categoria = await db.get(Categorias, id_categoria)
    if not categoria:
        raise HTTPException(404, "Categoria não encontrada")
    return categoria


# ── ADM ───────────────────────────────────────────────────


@router.post(
    "/",
    response_model=CategoriaOut,
    status_code=201,
    dependencies=[Depends(verificar_adm)],
)
async def criar_categoria(payload: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    categoria = Categorias(**payload.model_dump())
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.put(
    "/{id_categoria}",
    response_model=CategoriaOut,
    dependencies=[Depends(verificar_adm)],
)
async def atualizar_categoria(
    id_categoria: int, payload: CategoriaCreate, db: AsyncSession = Depends(get_db)
):
    categoria = await db.get(Categorias, id_categoria)
    if not categoria:
        raise HTTPException(404, "Categoria não encontrada")
    for k, v in payload.model_dump().items():
        setattr(categoria, k, v)
    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.delete(
    "/{id_categoria}", status_code=204, dependencies=[Depends(verificar_adm)]
)
async def deletar_categoria(id_categoria: int, db: AsyncSession = Depends(get_db)):
    categoria = await db.get(Categorias, id_categoria)
    if not categoria:
        raise HTTPException(404, "Categoria não encontrada")
    await db.delete(categoria)
    await db.commit()
