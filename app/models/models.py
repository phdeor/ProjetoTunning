# app/models/models.py

from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.postgres import Base


class Usuarios(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefone = Column(String(20))
    senha = Column(String(255), nullable=False)
    adm = Column(Boolean, default=False)

    pedidos = relationship("Pedidos", back_populates="usuario")


class Categorias(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255))

    produtos = relationship(
        "Produtos", back_populates="categoria"
    )  # ← "categoria", não "categoria_pai"


class Produtos(Base):
    __tablename__ = "produtos"

    id_produto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    preco = Column(Float, nullable=False)  # ← Float, não String
    estoque = Column(Integer, default=0)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))

    # IDs de imagens armazenadas no MongoDB (lista de strings)
    mongo_image_ids = Column(String(512), nullable=True)  # ← ex: "id1,id2,id3"

    categoria = relationship("Categorias", back_populates="produtos")  # ← nome alinhado
    itens_pedido = relationship("ItemPedido", back_populates="produto")


class Pedidos(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    dh_pedido = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="pendente")
    valor_total = Column(Float, default=0.0)
    observacao = Column(String(255), nullable=True)

    usuario = relationship("Usuarios", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "item_pedido"

    id_item_pedido = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)  # ← Float, não String

    pedido = relationship(
        "Pedidos", back_populates="itens"
    )  # ← era "Usuarios" (errado)
    produto = relationship("Produtos", back_populates="itens_pedido")
