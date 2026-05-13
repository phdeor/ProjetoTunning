# app/routers/pedidos.py  ← versão atualizada com itens embutidos e controle ADM
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.postgres import get_db
from app.models.models import Pedidos, ItemPedido
from app.schemas.schemas import PedidoOut, ItemPedidoOut
from app.core.deps import verificar_adm

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def _montar_itens(itens: list[ItemPedido]) -> list[ItemPedidoOut]:
    """Converte os ORM items em schema, calculando subtotal e nome."""
    resultado = []
    for item in itens:
        resultado.append(
            ItemPedidoOut(
                id_item_pedido=item.id_item_pedido,
                id_produto=item.id_produto,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                subtotal=round(item.quantidade * item.preco_unitario, 2),
                nome_produto=item.produto.nome if item.produto else None,
            )
        )
    return resultado


async def _buscar_pedido_completo(id_pedido: int, db: AsyncSession) -> Pedidos:
    """Busca pedido com eager load de itens + produto de cada item."""
    result = await db.execute(
        select(Pedidos)
        .options(selectinload(Pedidos.itens).selectinload(ItemPedido.produto))
        .where(Pedidos.id_pedido == id_pedido)
    )
    return result.scalar_one_or_none()


# ── Públicas ──────────────────────────────────────────────


@router.get("/{id_pedido}", response_model=PedidoOut)
async def buscar_pedido(id_pedido: int, db: AsyncSession = Depends(get_db)):
    pedido = await _buscar_pedido_completo(id_pedido, db)
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")

    return PedidoOut(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        dh_pedido=pedido.dh_pedido,
        status=pedido.status,
        valor_total=pedido.valor_total,
        observacao=pedido.observacao,
        itens=_montar_itens(pedido.itens),
    )


@router.get("/usuario/{id_usuario}", response_model=list[PedidoOut])
async def pedidos_do_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pedidos)
        .options(selectinload(Pedidos.itens).selectinload(ItemPedido.produto))
        .where(Pedidos.id_usuario == id_usuario)
        .order_by(Pedidos.dh_pedido.desc())
    )
    pedidos = result.scalars().all()

    return [
        PedidoOut(
            id_pedido=p.id_pedido,
            id_usuario=p.id_usuario,
            dh_pedido=p.dh_pedido,
            status=p.status,
            valor_total=p.valor_total,
            observacao=p.observacao,
            itens=_montar_itens(p.itens),
        )
        for p in pedidos
    ]


# ── ADM ───────────────────────────────────────────────────


@router.get("/", response_model=list[PedidoOut], dependencies=[Depends(verificar_adm)])
async def listar_todos_pedidos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pedidos)
        .options(selectinload(Pedidos.itens).selectinload(ItemPedido.produto))
        .order_by(Pedidos.dh_pedido.desc())
    )
    pedidos = result.scalars().all()
    return [
        PedidoOut(
            id_pedido=p.id_pedido,
            id_usuario=p.id_usuario,
            dh_pedido=p.dh_pedido,
            status=p.status,
            valor_total=p.valor_total,
            observacao=p.observacao,
            itens=_montar_itens(p.itens),
        )
        for p in pedidos
    ]


@router.patch(
    "/{id_pedido}/status",
    response_model=PedidoOut,
    dependencies=[Depends(verificar_adm)],
)
async def atualizar_status(
    id_pedido: int, status: str, db: AsyncSession = Depends(get_db)
):
    STATUS_VALIDOS = {"pendente", "confirmado", "enviado", "entregue", "cancelado"}
    if status not in STATUS_VALIDOS:
        raise HTTPException(400, f"Status inválido. Use: {STATUS_VALIDOS}")

    pedido = await _buscar_pedido_completo(id_pedido, db)
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")

    pedido.status = status
    await db.commit()
    await db.refresh(pedido)

    return PedidoOut(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        dh_pedido=pedido.dh_pedido,
        status=pedido.status,
        valor_total=pedido.valor_total,
        observacao=pedido.observacao,
        itens=_montar_itens(pedido.itens),
    )


@router.delete("/{id_pedido}", status_code=204, dependencies=[Depends(verificar_adm)])
async def deletar_pedido(id_pedido: int, db: AsyncSession = Depends(get_db)):
    pedido = await db.get(Pedidos, id_pedido)
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")
    await db.delete(pedido)
    await db.commit()
