# app/models/models.py
from sqlalchemy import Column, Integer, String, Boolean
from app.db.postgres import Base


class Usuarios(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    email = Column(String(255))
    telefone = Column(String(20))
    adm = Column(Boolean)
