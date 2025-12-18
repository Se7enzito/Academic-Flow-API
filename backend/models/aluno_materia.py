from sqlalchemy import Column, Integer, String, Boolean, Date
from backend.core.database import Base

class AlunoMateria(Base):
    __tablename__ = "aluno_materia"

    aluno_id = Column(Integer, primary_key=True)
    materia_codigo = Column(String, primary_key=True)

    concluida = Column(Boolean, default=False)
    data_conclusao = Column(Date, nullable=True)