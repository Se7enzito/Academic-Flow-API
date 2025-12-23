from fastapi import APIRouter, Query, Depends
import polars as pl
from sqlalchemy.orm import Session
from datetime import date

from backend.core.database import get_db
from backend.core.lazy_loader import LazyLoader
from backend.core.grafo import coletar_prerequisitos
from backend.core.security import get_current_user
from backend.models.aluno_materia import AlunoMateria
from backend.models.user import User

router = APIRouter(prefix="/fluxograma", tags=["Fluxograma"])

@router.get("/")
def fluxograma():
    materias = LazyLoader.materias()
    prereqs = LazyLoader.prerequisitos()
    materias_semestre = LazyLoader.materias_semestre()

    semestre_df = (
        materias_semestre
        .explode("materias")
        .rename({"materias": "codigo"})
    )

    df = (
        materias
        .select(["codigo", "nome"])
        .join(
            semestre_df,
            on="codigo",
            how="left"
        )
        .join(
            prereqs,
            left_on="codigo",
            right_on="materia",
            how="left"
        )
        .join(
            materias.select(["codigo", "nome"]),
            left_on="pre_requisito",
            right_on="codigo",
            how="left"
        )
        .select([
            pl.col("codigo").alias("id"),
            pl.col("nome").alias("nome"),
            pl.col("semestre"),
            pl.col("pre_requisito").alias("prereq_id"),
            pl.col("nome_right").alias("prereq_nome"),
        ])
        .group_by(["id", "nome", "semestre"])
        .agg(
            pl.struct(
                pl.col("prereq_id").alias("id"),
                pl.col("prereq_nome").alias("nome")
            )
            .filter(pl.col("prereq_id").is_not_null())
            .alias("pre_requisitos")
        )
        .collect()
    )

    return df.to_dicts()

@router.get("/requisitos-completos")
def requisitos_completos(codigo: str = Query(...)):
    prereqs_df = LazyLoader.prerequisitos().collect()
    materias_df = LazyLoader.materias().collect()

    mapa = {}
    for row in prereqs_df.iter_rows(named=True):
        materia = row["materia"]
        prereq = row["pre_requisito"]
        mapa.setdefault(materia, []).append(prereq)
    
    todos = coletar_prerequisitos(mapa, codigo)

    if not todos:
        return {
            "materia": codigo,
            "pre_requisitos": []
        }
        
    materias_semestre_df = (
        LazyLoader.materias_semestre()
        .explode("materias")
        .rename({"materias": "codigo"})
        .collect()
    )
    
    resultado = (
        materias_df
        .join(materias_semestre_df, on="codigo", how="left")
        .filter(pl.col("codigo").is_in(list(todos)))
        .select(["codigo", "nome", "semestre"])
        .to_dicts()
    )
    
    return {
        "materia": codigo,
        "quantidade": len(resultado),
        "pre_requisitos": resultado
    }

@router.post("/progresso")
def progresso_aluno(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    aluno_id = current_user.id
    
    registros = (
        db.query(AlunoMateria)
        .filter_by(aluno_id=aluno_id, concluida=True)
        .all()
    )

    materias_concluidas = [
        registro.materia_codigo for registro in registros
    ]

    return {
        "aluno_id": aluno_id,
        "materias_concluidas": materias_concluidas,
        "quantidade": len(materias_concluidas)
    }

@router.post("/concluir")
def concluir_materia(
    materia_codigo: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    aluno_id = current_user.id
    
    registro = (
        db.query(AlunoMateria)
        .filter_by(
            aluno_id=aluno_id,
            materia_codigo=materia_codigo
        )
        .first()
    )

    if not registro:
        registro = AlunoMateria(
            aluno_id=aluno_id,
            materia_codigo=materia_codigo,
            concluida=True,
            data_conclusao=date.today()
        )
        db.add(registro)
    else:
        registro.concluida = True
        registro.data_conclusao = date.today()

    db.commit()
    return {"status": "ok"}

@router.post("/desmarcar")
def desmarcar_materia(
    materia_codigo: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    aluno_id = current_user.id
    
    registro = (
        db.query(AlunoMateria)
        .filter_by(
            aluno_id=aluno_id,
            materia_codigo=materia_codigo
        )
        .first()
    )

    if not registro:
        return {"status": "nao_existe"}

    registro.concluida = False
    registro.data_conclusao = None

    db.commit()
    return {"status": "ok"}

if __name__ == "__main__":
    pass