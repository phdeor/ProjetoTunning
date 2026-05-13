# app/services/carrinho_service.py
from app.db.redis_client import redis_cache

PREFIXO = "carrinho"
TTL_SEGUNDOS = 60 * 60 * 24 * 7  # 7 dias


def _chave(id_usuario: int) -> str:
    return f"{PREFIXO}:{id_usuario}"


async def adicionar_item(id_usuario: int, id_produto: int, quantidade: int) -> dict:
    """Adiciona ou incrementa a quantidade de um item no carrinho."""
    chave = _chave(id_usuario)
    r = redis_cache.client

    # HINCRBY soma se já existir, cria se não existir
    nova_qtd = await r.hincrby(chave, str(id_produto), quantidade)

    # Se ficou <= 0 remove o campo
    if nova_qtd <= 0:
        await r.hdel(chave, str(id_produto))
    else:
        await r.expire(chave, TTL_SEGUNDOS)  # renova TTL a cada interação

    return await listar_carrinho(id_usuario)


async def remover_item(id_usuario: int, id_produto: int) -> dict:
    """Remove completamente um produto do carrinho."""
    await redis_cache.client.hdel(_chave(id_usuario), str(id_produto))
    return await listar_carrinho(id_usuario)


async def listar_carrinho(id_usuario: int) -> dict:
    """Retorna o carrinho como { id_produto: quantidade }."""
    dados = await redis_cache.client.hgetall(_chave(id_usuario))
    return {int(k): int(v) for k, v in dados.items()}


async def limpar_carrinho(id_usuario: int) -> None:
    """Esvazia o carrinho (usado após fechar pedido)."""
    await redis_cache.client.delete(_chave(id_usuario))


async def atualizar_quantidade(
    id_usuario: int, id_produto: int, quantidade: int
) -> dict:
    """Define uma quantidade exata (substitui ao invés de somar)."""
    chave = _chave(id_usuario)
    r = redis_cache.client

    if quantidade <= 0:
        await r.hdel(chave, str(id_produto))
    else:
        await r.hset(chave, str(id_produto), quantidade)
        await r.expire(chave, TTL_SEGUNDOS)

    return await listar_carrinho(id_usuario)
