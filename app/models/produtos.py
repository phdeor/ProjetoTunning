# app/models/models.py
from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.postgres import Base
from sqlalchemy.orm import relationship


class Produtos(Base):
    __tablename__ = "produtos"
    id_produto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    preco = Column(String(10))
    estoque = Column(Integer)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))

    categoria_pai = relationship("categorias", back_populates="produtos")
