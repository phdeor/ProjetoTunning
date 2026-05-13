# app/routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import (
    get_current_user,
    verificar_adm,
)

from app.core.security import criar_access_token, gerar_hash, verificar_senha
from app.db.postgres import get_db
from app.models.models import Usuarios
from app.schemas.schemas import (
    UsuarioCreate,
    UsuarioOut,
    UsuarioLogin,
    UsuarioUpdate,
    TokenResponse,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
async def criar_usuario(payload: UsuarioCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Usuarios).where(Usuarios.email == payload.email))

    usuario_existente = result.scalar_one_or_none()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario = Usuarios(
        nome=payload.nome,
        email=payload.email,
        telefone=payload.telefone,
        senha=gerar_hash(payload.senha),
        adm=False,
    )

    db.add(usuario)

    await db.commit()

    await db.refresh(usuario)

    return usuario


@router.post("/login", response_model=TokenResponse)
async def login(payload: UsuarioLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Usuarios).where(Usuarios.email == payload.email))

    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    senha_valida = verificar_senha(payload.senha, usuario.senha)

    if not senha_valida:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    access_token = criar_access_token({"id_usuario": usuario.id_usuario})

    return {"access_token": access_token, "token_type": "bearer", "usuario": usuario}


@router.get("/me", response_model=UsuarioOut)
async def me(usuario: Usuarios = Depends(get_current_user)):

    return usuario


@router.put("/me", response_model=UsuarioOut)
async def atualizar_meu_usuario(
    payload: UsuarioUpdate,
    usuario: Usuarios = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    dados = payload.model_dump(exclude_unset=True)

    if "senha" in dados:
        dados["senha"] = gerar_hash(dados["senha"])

    for campo, valor in dados.items():
        setattr(usuario, campo, valor)

    await db.commit()

    await db.refresh(usuario)

    return usuario


@router.get(
    "/list", response_model=list[UsuarioOut], dependencies=[Depends(verificar_adm)]
)
async def listar_usuarios(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Usuarios))

    return result.scalars().all()


@router.get(
    "/{id_usuario}", response_model=UsuarioOut, dependencies=[Depends(verificar_adm)]
)
async def buscar_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):

    usuario = await db.get(Usuarios, id_usuario)

    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    return usuario


@router.delete("/{id_usuario}", status_code=204, dependencies=[Depends(verificar_adm)])
async def deletar_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):

    usuario = await db.get(Usuarios, id_usuario)

    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    await db.delete(usuario)

    await db.commit()


@router.put(
    "/{id_usuario}", response_model=UsuarioOut, dependencies=[Depends(verificar_adm)]
)
async def atualizar_usuario(
    payload: UsuarioUpdate,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
):

    usuario = await db.get(Usuarios, id_usuario)

    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    dados = payload.model_dump(exclude_unset=True)

    if "senha" in dados:
        dados["senha"] = gerar_hash(dados["senha"])

    for campo, valor in dados.items():
        setattr(usuario, campo, valor)

    await db.commit()

    await db.refresh(usuario)

    return usuario
