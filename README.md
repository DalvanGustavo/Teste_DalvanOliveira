# Projeto de Consolidação de Despesas com Eventos / Sinistros – ANS

## 1. Apresentação do Projeto

Este projeto foi desenvolvido como parte de um **teste técnico de engenharia de dados**, utilizando dados públicos disponibilizados pela **Agência Nacional de Saúde Suplementar (ANS)**.

O objetivo é **automatizar a ingestão, extração, processamento, normalização, validação e consolidação** das informações de **Despesas com Eventos / Sinistros**, referentes aos **últimos três trimestres disponíveis**, garantindo resiliência a variações de formato, estrutura e qualidade dos dados.

O resultado final é um **arquivo CSV consolidado**, compactado em ZIP, pronto para análises financeiras, auditorias regulatórias e consumo analítico.

---

## 2. Fontes de Dados Utilizadas

### 2.1 Demonstrações Contábeis (ANS)

Fonte:
```
https://dadosabertos.ans.gov.br/FTP/PDA/
```

Características:
- Arquivos organizados por **ano/trimestre**
- Formatos variados: **CSV, TXT e XLSX**
- Estruturas de colunas heterogêneas
- Possibilidade de múltiplos arquivos por trimestre
- Arquivos disponibilizados em formato **ZIP**

Esses arquivos contêm os valores contábeis das operadoras, incluindo a categoria  
**“Despesas com Eventos / Sinistros”**, identificada no campo descritivo das contas.

---

### 2.2 Cadastro de Operadoras Ativas (CADOP)

Fonte:
```
https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv
```

#### Justificativa técnica para uso do arquivo adicional

Os arquivos de demonstrações contábeis **não contêm diretamente CNPJ e Razão Social**.  
Eles utilizam apenas o identificador:

- `REG_ANS`

No arquivo CADOP, o campo equivalente é:

- `Registro_Operadora`

Ambos representam o **mesmo identificador oficial da ANS**, sendo a **única chave confiável**
para realizar o enriquecimento cadastral.

Esse arquivo adicional é essencial para:
- Associar corretamente **CNPJ**
- Associar corretamente **Razão Social**
- Garantir integridade referencial
- Atender ao requisito de consolidação empresarial

Sem o CADOP, a consolidação exigida pelo teste técnico não seria possível.

---

## 3. Estratégia de Processamento

### 3.1 Extração Automática de Arquivos ZIP

Todos os arquivos ZIP baixados são:
1. Identificados automaticamente
2. Extraídos localmente
3. Processados após a extração

Essa etapa garante que o pipeline funcione de forma autônoma, sem intervenção manual.

---

### 3.2 Modelo de Processamento: Incremental

Foi adotado o **processamento incremental**, no qual cada arquivo é:
1. Lido individualmente
2. Filtrado pela categoria de interesse
3. Normalizado
4. Enriquecido com dados cadastrais
5. Consolidado ao resultado final

Justificativa técnica:
- Redução do consumo de memória
- Robustez frente a grandes volumes de dados
- Tratamento isolado de falhas
- Escalabilidade para novos períodos

---

## 4. Normalização dos Dados

Apesar das variações de formato, todos os dados são normalizados para a seguinte estrutura final:

| Coluna              | Descrição |
|---------------------|-----------|
| CNPJ                | CNPJ da operadora |
| RazaoSocial         | Razão social da operadora |
| Ano                 | Ano de referência |
| Trimestre           | Trimestre de referência |
| ValorDespesas       | Valor consolidado das despesas |
| RazaoSocialSuspeita | Indicador de inconsistência cadastral |
| RegistroValido      | Indicador de validação do registro |

---

## 5. Tratamento de Inconsistências

### 5.1 CNPJs duplicados com razões sociais diferentes
- Tratamento: Marcação como suspeito (`RazaoSocialSuspeita = true`)
- Justificativa: Preservação da informação sem descarte indevido, permitindo auditoria posterior

### 5.2 Valores zerados ou negativos
- Tratamento: Marcados como inválidos
- Justificativa: Valores incompatíveis com despesas operacionais

### 5.3 Datas inconsistentes ou inválidas
- Tratamento: Registros descartados
- Justificativa: Impossibilidade de inferir ano e trimestre com segurança

---

## 6. Validação de Dados (Teste 2.1)

### 6.1 Validações implementadas
- **CNPJ**
  - Verificação de formato (14 dígitos)
  - Validação dos dígitos verificadores
- **ValorDespesas**
  - Apenas valores numéricos estritamente positivos
- **Razão Social**
  - Não vazia ou nula

Cada registro recebe indicadores individuais e o campo final:
- `RegistroValido`

### 6.2 Trade-off técnico – CNPJs inválidos
Estratégia adotada: **marcação explícita dos registros inválidos**.

Justificativa:
- Evita perda de dados potencialmente relevantes
- Permite auditoria e rastreabilidade
- Mantém transparência da qualidade dos dados

---

## 7. Entrega final (CSV)
- Arquivo CSV consolidado
- Compactado em:
```
consolidado_despesas.zip
```

---

## 8. Considerações finais

O projeto foi desenvolvido priorizando:
- Resiliência a dados heterogêneos
- Boas práticas de engenharia de dados
- Clareza técnica
- Transparência no tratamento de inconsistências
- Aderência aos requisitos do teste técnico

Toda a solução é baseada exclusivamente em **dados públicos oficiais da ANS**.

---

## 9. Enriquecimento de Dados (Teste 2.2)

Foi realizado o enriquecimento do CSV consolidado utilizando os dados cadastrais das operadoras ativas (CADOP).

### Estratégia de Join
- Tipo: LEFT JOIN
- Chave: CNPJ

### Tratamento de falhas
- **Registros sem match no cadastro**
  - Mantidos no dataset
  - Campos cadastrais como nulos
  - `CadastroEncontrado = false`
- **CNPJs duplicados no cadastro**
  - Mantido apenas um registro por CNPJ
  - `CadastroDuplicado = true`

Trade-off: join em memória (Pandas), considerando volume reduzido e simplicidade.

---

## 10. Agregação de Despesas (Teste 2.3)

Agrupamento por:
- RazaoSocial
- UF

Métricas:
- TotalDespesas
- MediaDespesasTrimestre
- DesvioPadraoDespesas

Trade-off: agregação em memória (Pandas) pelo volume reduzido; em escala maior poderia ir para processamento distribuído.

---

## 11. Banco de Dados e Importação (MySQL 8.0)

Tabelas finais:
- `operadoras`
- `despesas_consolidadas`
- `despesas_agregadas`

### 11.1 Estratégia: staging + carga tratada
1. Importar CSVs em `stg_*` (tudo `VARCHAR`)
2. Inserir nas tabelas finais com:
   - `CAST`, `TRIM`, `REGEXP_REPLACE`
   - filtros `WHERE` para rejeitar inválidos

### 11.2 Encoding utilizado
- `consolidado_despesas.csv` e `despesas_agregadas.csv`: `utf8mb4`
- `Relatorio_cadop.csv`: `latin1`

### 11.3 Inconsistências tratadas na carga
- Campos obrigatórios nulos/vazios → rejeitados
- Strings em campos numéricos → conversão controlada
- Formatos numéricos BR/US → regra condicional (`,` vs `.`)
- Datas → padronização em `Ano`/`Trimestre`

### 11.4 Observação: `secure_file_priv`
Para verificar diretório permitido:
```sql
SELECT @@secure_file_priv;
```

### 11.5 Observação técnica (Workbench e LOCAL INFILE)
Erro:
```
Error Code: 2068. LOAD DATA LOCAL INFILE file request rejected due to restrictions on access
```

Solução:
- utilizar `LOAD DATA INFILE` (sem LOCAL)
- posicionar arquivos no diretório retornado por `@@secure_file_priv`

---

## 12. Queries Analíticas (Teste 3.4)

### 12.1 Query 1 — Top 5 operadoras com maior crescimento percentual
- Considera somente operadoras com valor no trimestre inicial e final
- Crescimento percentual calculado e ordenado desc

### 12.2 Query 2 — Distribuição de despesas por UF (Top 5)
- Total por UF
- Média por operadora na UF

### 12.3 Query 3 — Operadoras acima da média em ≥ 2 dos 3 trimestres
- Abordagem com CTEs
- Resultado observado: **0**

---

## 13. API e Interface Web (Teste 4)

### 13.1 Backend (FastAPI) — Rotas implementadas

- `GET /api/operadoras`
  - paginação: `page`, `limit`
  - busca opcional: `search` (razão social ou CNPJ)
- `GET /api/operadoras/{cnpj}`
- `GET /api/operadoras/{cnpj}/despesas`
- `GET /api/estatisticas`
  - total, média
  - top 5 operadoras
  - distribuição de despesas por UF (para gráfico)

### 13.2 Trade-offs técnicos — Backend (FastAPI)

#### 13.2.1 Escolha do framework
**Escolha:** FastAPI  
Motivos: validação com Pydantic, OpenAPI/Swagger automático, boa performance e manutenção.

#### 13.2.2 Paginação
**Escolha:** Offset-based (`page`, `limit`)  
Motivos: simplicidade e adequação ao cenário do teste (dados estáveis).

#### 13.2.3 `/api/estatisticas`
**Escolha:** Cache por TTL (ex.: 10 min)  
Motivos: rota com agregações; dados pouco mutáveis; melhora latência.

#### 13.2.4 Resposta de paginação
**Escolha:** dados + metadados  
Exemplo:
```json
{ "data": [...], "total": 100, "page": 1, "limit": 10 }
```
Motivos: facilita UI e evita chamada extra para contagem.

---

## 14. Frontend (Vue.js)

### 14.1 Funcionalidades implementadas
- Dashboard:
  - exibe total e média
  - gráfico de barras com despesas por UF (Chart.js)
  - lista Top 5 operadoras por despesas
- Operadoras:
  - tabela paginada
  - busca/filtro por Razão Social ou CNPJ (server-side)
- Detalhe da operadora:
  - dados cadastrais
  - gráfico de linha com histórico de despesas (por ano/trimestre)

### 14.2 Trade-offs técnicos — Frontend

#### 14.2.1 Estratégia de busca/filtro
**Escolha:** busca no servidor (Opção A)  
Justificativa:
- evita carregar todas as operadoras no cliente
- melhora performance e tempo de resposta com grandes volumes
- permite paginação consistente com filtro aplicado

#### 14.2.2 Gerenciamento de estado
**Escolha:** estado local por componente (Props/Events simples) + chamadas diretas via Axios  
Justificativa:
- aplicação pequena, com baixo compartilhamento de estado
- reduz complexidade (sem Vuex/Pinia)
- melhor legibilidade para o contexto do teste

#### 14.2.3 Performance da tabela
**Escolha:** paginação server-side (limitando renderização)  
Justificativa:
- reduz custo de render em listas grandes
- mantém UX responsiva sem necessidade de virtualização

#### 14.2.4 Tratamento de erros e loading
- loading exibido durante requisições (componente `Loading`)
- erros exibidos de forma clara (componente `ErrorBox`)
- estados vazios tratados (ex.: “nenhuma operadora encontrada”, “sem despesas registradas”)

Trade-off:
- mensagens de erro tendem a ser **específicas** quando possível (ex.: 404 em detalhes), e **genéricas** quando não há detalhe confiável (falha de rede).

---

## 15. Como executar (backend + frontend)

### 15.1 Requisitos
- Python 3.11+
- Node.js 18+ (ou 20+)
- MySQL 8.0 + Workbench

### 15.2 Executar backend (FastAPI)
Na pasta `Backend/`:
```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Acesse:
- Swagger: `http://127.0.0.1:8000/docs`

### 15.3 Executar frontend (Vue)
Na pasta `frontend/`:
```bash
npm install
npm run dev
```

Acesse:
- `http://localhost:5173`

---

## 16. Postman

Foi criada uma coleção para demonstrar as rotas:
- `GET /api/operadoras?page=1&limit=10&search=...`
- `GET /api/operadoras/{cnpj}`
- `GET /api/operadoras/{cnpj}/despesas`
- `GET /api/estatisticas`

Inclui exemplos de requests e respostas esperadas.

---

## 17. Estrutura do repositório

Exemplo de organização:
```
Backend/
  app/
  requirements.txt
  .env
frontend/
  src/
  package.json
sql/
  script.sql
README.md
```

---

## 18. Empacotamento final

Ao final do projeto, todos os arquivos devem ser compactados em:
```
Teste_DalvanOliveira.zip
```

Incluindo:
- scripts Python (pipeline + backend)
- scripts SQL
- frontend Vue
- README.md
- CSVs gerados (quando aplicável)