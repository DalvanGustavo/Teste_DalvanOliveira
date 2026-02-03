from pydantic import BaseModel
from typing import List, Optional

# Schemas para respostas da API
class OperadoraBase(BaseModel):
    cnpj: str
    razao_social: Optional[str] = None
    uf: Optional[str] = None

# Schema para detalhes da operadora
class OperadoraDetalhe(OperadoraBase):
    registro_ans: Optional[int] = None

# Schema para item de despesa
class DespesaItem(BaseModel):
    ano: int
    trimestre: int
    valor_despesas: float

# Schema para resposta paginada de operadoras
class OperadorasResponse(BaseModel):
    data: List[OperadoraBase]
    total: int
    page: int
    limit: int

# Schema para estatísticas agregadas
class EstatisticasResponse(BaseModel):
    total_despesas: float
    media_despesas: float
    top5_operadoras: List[dict]
    despesas_por_uf: List[dict]
