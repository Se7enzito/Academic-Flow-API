from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)

from backend.core.database import Base

class DisciplinaProfessor(Base):
    __tablename__ = "disciplinas_professores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_professor = Column(Integer, ForeignKey("professores.id"), index=True, nullable=False)
    id_disciplina = Column(Integer, nullable=False)