from sqlalchemy import (
    Column,
    Integer,
    String
)

from backend.core.database import Base

class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    departamento = Column(String(100), nullable=False)