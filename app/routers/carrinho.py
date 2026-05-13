# app/routers/carrinho.py
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ItemCarrinhoPayload, AtualizarQuantidadePayload
from app.services import carrinho_service

router = APIRouter(prefix="/carrinho", tags=["Carrinho"])


@router.get("/{id_usuario}")
async def ver_carrinho(id_usuario: int):
    """Retorna todos os itens do carrinho do usuário."""
    return await carrinho_service.listar_carrinho(id_usuario)


@router.post("/{id_usuario}/itens", status_code=201)
async def adicionar_ao_carrinho(id_usuario: int, payload: ItemCarrinhoPayload):
    """Adiciona um produto ou incrementa sua quantidade no carrinho."""
    if payload.quantidade == 0:
        raise HTTPException(400, "Quantidade não pode ser zero")
    return await carrinho_service.adicionar_item(
        id_usuario, payload.id_produto, payload.quantidade
    )


@router.put("/{id_usuario}/itens/{id_produto}")
async def atualizar_item(
    id_usuario: int, id_produto: int, payload: AtualizarQuantidadePayload
):
    """Define uma quantidade exata para o produto (útil para o campo numérico no front)."""
    return await carrinho_service.atualizar_quantidade(
        id_usuario, id_produto, payload.quantidade
    )


@router.delete("/{id_usuario}/itens/{id_produto}", status_code=204)
async def remover_do_carrinho(id_usuario: int, id_produto: int):
    """Remove um produto específico do carrinho."""
    await carrinho_service.remover_item(id_usuario, id_produto)


@router.delete("/{id_usuario}", status_code=204)
async def limpar_carrinho(id_usuario: int):
    """Esvazia o carrinho inteiro (ex: após finalizar pedido)."""
    await carrinho_service.limpar_carrinho(id_usuario)
