# app/schemas/schemas.py  ← versão completa consolidada
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ══════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: Optional[str] = None
    adm: bool = False


class UsuarioOut(UsuarioCreate):
    id_usuario: int

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioOut


# ══════════════════════════════════════════════════
# CATEGORIAS
# ══════════════════════════════════════════════════
class CategoriaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CategoriaOut(CategoriaCreate):
    id_categoria: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# PRODUTOS
# ══════════════════════════════════════════════════
class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    estoque: int
    id_categoria: int


class CategoriaSimpleOut(BaseModel):
    nome: str  # Nome da coluna na tabela Categorias

    class Config:
        from_attributes = True


class ProdutoOut(ProdutoCreate):
    id_produto: int
    mongo_image_ids: Optional[str] = None
    categoria: CategoriaSimpleOut

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# ITEM PEDIDO
# ══════════════════════════════════════════════════
class ItemPedidoCreate(BaseModel):
    id_produto: int
    quantidade: int
    preco_unitario: float


class ItemPedidoOut(BaseModel):
    id_item_pedido: int
    id_produto: int
    quantidade: int
    preco_unitario: float
    subtotal: float  # calculado na serialização
    nome_produto: Optional[str] = None  # enriquecido na query

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# PEDIDOS
# ══════════════════════════════════════════════════
class PedidoCreate(BaseModel):
    id_usuario: int
    observacao: Optional[str] = None


class PedidoOut(BaseModel):
    id_pedido: int
    id_usuario: int
    dh_pedido: datetime
    status: str
    valor_total: float
    observacao: Optional[str] = None
    itens: list[ItemPedidoOut] = []  # ← itens embutidos

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# CARRINHO
# ══════════════════════════════════════════════════
class ItemCarrinhoPayload(BaseModel):
    id_produto: int
    quantidade: int = 1


class AtualizarQuantidadePayload(BaseModel):
    quantidade: int


# ══════════════════════════════════════════════════
# CHECKOUT
# ══════════════════════════════════════════════════
class CheckoutPayload(BaseModel):
    id_usuario: int
    observacao: Optional[str] = None
