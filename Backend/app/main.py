import re
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from cachetools import TTLCache
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from .db import get_db
from .schemas import (
    OperadorasResponse,
    OperadoraDetalhe,
    DespesaItem,
    EstatisticasResponse,
)
from .settings import API_CORS_ORIGINS, STATS_CACHE_TTL_SECONDS

# FastAPI app instance
app = FastAPI(title="ANS - Despesas API", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stats_cache = TTLCache(maxsize=10, ttl=STATS_CACHE_TTL_SECONDS)

# Endpoint para listar operadoras com paginação e busca
@app.get("/api/operadoras", response_model=OperadorasResponse)
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit

    where_clause = ""
    params = {"limit": limit, "offset": offset}

    if search:
        search = search.strip()

        # se o usuário digitou CNPJ com máscara, remove tudo que não é dígito
        search_digits = re.sub(r"\D", "", search)

        # se tiver pelo menos 5 dígitos, usamos o digits para buscar por cnpj
        if len(search_digits) >= 5:
            where_clause = """
                WHERE o.razao_social LIKE :search_text
                   OR o.cnpj LIKE :search_digits
            """
            params["search_text"] = f"%{search}%"
            params["search_digits"] = f"%{search_digits}%"
        else:
            where_clause = "WHERE o.razao_social LIKE :search_text"
            params["search_text"] = f"%{search}%"

    # total
    if where_clause:
        total = db.execute(
            text(f"SELECT COUNT(*) FROM operadoras o {where_clause}"),
            params,
        ).scalar() or 0
    else:
        total = db.execute(
            text("SELECT COUNT(*) FROM operadoras")
        ).scalar() or 0

    # data
    rows = db.execute(
        text(
            f"""
            SELECT o.cnpj, o.razao_social, o.uf
            FROM operadoras o
            {where_clause}
            ORDER BY o.razao_social
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).mappings().all()

    return {
        "data": [dict(r) for r in rows],
        "total": int(total),
        "page": page,
        "limit": limit,
    }

# Endpoint para detalhes de uma operadora específica
@app.get("/api/operadoras/{cnpj}", response_model=OperadoraDetalhe)
def detalhe_operadora(cnpj: str, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT cnpj, razao_social, uf, registro_ans
            FROM operadoras
            WHERE cnpj = :cnpj
            """
        ),
        {"cnpj": cnpj},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    return dict(row)

# Endpoint para histórico de despesas de uma operadora
@app.get("/api/operadoras/{cnpj}/despesas", response_model=list[DespesaItem])
def despesas_operadora(cnpj: str, db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT ano, trimestre, valor_despesas
            FROM despesas_consolidadas
            WHERE cnpj = :cnpj
            ORDER BY ano, trimestre
            """
        ),
        {"cnpj": cnpj},
    ).mappings().all()

    # Pode existir operadora sem despesas (mantém coerência com LEFT JOIN / dados incompletos)
    return [dict(r) for r in rows]

# Endpoint para estatísticas agregadas
@app.get("/api/estatisticas", response_model=EstatisticasResponse)
def estatisticas(db: Session = Depends(get_db)):
    if "payload" in stats_cache:
        return stats_cache["payload"]

    total = db.execute(
        text("SELECT SUM(valor_despesas) FROM despesas_consolidadas")
    ).scalar() or 0

    media = db.execute(
        text("SELECT AVG(valor_despesas) FROM despesas_consolidadas")
    ).scalar() or 0

    top5 = db.execute(
        text(
            """
            SELECT o.razao_social, o.cnpj, SUM(d.valor_despesas) AS total
            FROM despesas_consolidadas d
            JOIN operadoras o ON o.cnpj = d.cnpj
            GROUP BY o.razao_social, o.cnpj
            ORDER BY total DESC
            LIMIT 5
            """
        )
    ).mappings().all()

    por_uf = db.execute(
        text(
            """
            SELECT o.uf, SUM(d.valor_despesas) AS total
            FROM despesas_consolidadas d
            JOIN operadoras o ON o.cnpj = d.cnpj
            WHERE o.uf IS NOT NULL AND o.uf <> ''
            GROUP BY o.uf
            ORDER BY total DESC
            """
        )
    ).mappings().all()

    payload = {
        "total_despesas": float(total),
        "media_despesas": float(media),
        "top5_operadoras": [dict(x) for x in top5],
        "despesas_por_uf": [dict(x) for x in por_uf],
    }

    stats_cache["payload"] = payload
    return payload
