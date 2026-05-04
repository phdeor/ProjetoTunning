# app/models/models.py
from sqlalchemy import Column, Integer, String
from app.db.postgres import Base
from sqlalchemy.orm import relationship


class Categorias(Base):
    __tablename__ = "categorias"
    id_categoria = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    descricao = Column(String(255))

    produtos = relationship("produtos", back_populates="categoria_pai")
