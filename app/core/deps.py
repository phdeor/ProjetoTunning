from fastapi import Depends, HTTPException

from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.db.postgres import get_db

from app.models.models import Usuarios

from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):

    credentials_exception = HTTPException(status_code=401, detail="Token inválido")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id_usuario = payload.get("id_usuario")

        if id_usuario is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Usuarios).where(Usuarios.id_usuario == id_usuario))

    usuario = result.scalar_one_or_none()

    if not usuario:
        raise credentials_exception

    return usuario


async def verificar_adm(usuario: Usuarios = Depends(get_current_user)):

    if not usuario.adm:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usuario
