# app/routers/checkout.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.db.postgres import get_db
from app.models.models import Pedidos, ItemPedido, Produtos
from app.schemas.schemas import CheckoutPayload, PedidoOut, ItemPedidoOut
from app.services.carrinho_service import listar_carrinho, limpar_carrinho

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/", response_model=PedidoOut, status_code=201)
async def finalizar_compra(
    payload: CheckoutPayload,
    db: AsyncSession = Depends(get_db),
):
    # 1. Busca o carrinho no Redis
    carrinho = await listar_carrinho(payload.id_usuario)
    if not carrinho:
        raise HTTPException(
            400, "Carrinho vazio. Adicione produtos antes de finalizar."
        )

    # 2. Valida estoque e coleta preços em uma só query
    ids_produtos = list(carrinho.keys())
    result = await db.execute(
        select(Produtos).where(Produtos.id_produto.in_(ids_produtos))
    )
    produtos_db = {p.id_produto: p for p in result.scalars().all()}

    erros = []
    for id_produto, quantidade in carrinho.items():
        produto = produtos_db.get(id_produto)
        if not produto:
            erros.append(f"Produto {id_produto} não encontrado.")
        elif produto.estoque < quantidade:
            erros.append(
                f"Estoque insuficiente para '{produto.nome}': "
                f"disponível {produto.estoque}, solicitado {quantidade}."
            )
    if erros:
        raise HTTPException(400, {"erros": erros})

    # 3. Cria o pedido
    pedido = Pedidos(
        id_usuario=payload.id_usuario,
        observacao=payload.observacao,
        status="pendente",
        valor_total=0.0,
    )
    db.add(pedido)
    await db.flush()  # gera id_pedido sem commitar ainda

    # 4. Cria os itens e desconta estoque
    valor_total = 0.0
    itens_criados = []

    for id_produto, quantidade in carrinho.items():
        produto = produtos_db[id_produto]
        preco = produto.preco

        item = ItemPedido(
            id_pedido=pedido.id_pedido,
            id_produto=id_produto,
            quantidade=quantidade,
            preco_unitario=preco,
        )
        db.add(item)
        produto.estoque -= quantidade  # desconta estoque atomicamente
        valor_total += preco * quantidade
        itens_criados.append((item, produto.nome))

    # 5. Atualiza valor total e commita tudo junto
    pedido.valor_total = round(valor_total, 2)
    await db.commit()

    # 6. Limpa o carrinho no Redis (só após commit com sucesso)
    await limpar_carrinho(payload.id_usuario)

    # 7. Monta resposta
    itens_out = [
        ItemPedidoOut(
            id_item_pedido=item.id_item_pedido,
            id_produto=item.id_produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            subtotal=round(item.quantidade * item.preco_unitario, 2),
            nome_produto=nome,
        )
        for item, nome in itens_criados
    ]

    return PedidoOut(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        dh_pedido=pedido.dh_pedido,
        status=pedido.status,
        valor_total=pedido.valor_total,
        observacao=pedido.observacao,
        itens=itens_out,
    )
