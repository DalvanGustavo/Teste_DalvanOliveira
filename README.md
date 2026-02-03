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

#### Justificativa técnica:
- Redução do consumo de memória
- Robustez frente a grandes volumes de dados
- Tratamento isolado de falhas
- Escalabilidade para novos períodos

---

## 4. Normalização dos Dados

Apesar das variações de formato, todos os dados são normalizados para a seguinte estrutura final:

| Coluna                | Descrição |
|-----------------------|-----------|
| CNPJ                  | CNPJ da operadora |
| RazaoSocial           | Razão social da operadora |
| Ano                   | Ano de referência |
| Trimestre             | Trimestre de referência |
| ValorDespesas         | Valor consolidado das despesas |
| RazaoSocialSuspeita   | Indicador de inconsistência cadastral |
| RegistroValido        | Indicador de validação do registro |

---

## 5. Tratamento de Inconsistências

Durante a consolidação, foram identificadas e tratadas as seguintes situações:

### 5.1 CNPJs duplicados com razões sociais diferentes
- **Tratamento:** Marcação como suspeito (`RazaoSocialSuspeita = true`)
- **Justificativa:** Preservação da informação sem descarte indevido, permitindo auditoria posterior

---

### 5.2 Valores zerados ou negativos
- **Tratamento:** Marcados como inválidos
- **Justificativa:** Valores incompatíveis com despesas operacionais

---

### 5.3 Datas inconsistentes ou inválidas
- **Tratamento:** Registros descartados
- **Justificativa:** Impossibilidade de inferir ano e trimestre com segurança

---

## 6. Validação de Dados (Teste 2.1)

Após a consolidação, é aplicada uma etapa de **validação de qualidade dos dados**.

### 6.1 Validações Implementadas

- **CNPJ**
  - Verificação de formato (14 dígitos)
  - Validação dos dígitos verificadores

- **ValorDespesas**
  - Apenas valores numéricos estritamente positivos

- **Razão Social**
  - Não vazia ou nula

Cada registro recebe indicadores individuais de validação e um campo final:

- `RegistroValido`

---

### 6.2 Trade-off Técnico – Tratamento de CNPJs Inválidos

#### Estratégias consideradas:
1. Remover registros inválidos
2. Corrigir automaticamente CNPJs
3. Marcar registros inválidos sem descartá-los

#### Estratégia adotada:
**Marcação explícita dos registros inválidos**

#### Justificativa:
- Evita perda de dados potencialmente relevantes
- Permite auditoria e rastreabilidade
- Mantém transparência da qualidade dos dados

**Prós:**
- Preserva histórico
- Facilita análises de qualidade
- Compatível com contextos regulatórios

**Contras:**
- Exige filtragem adicional em análises futuras

---

## 7. Entrega Final

- Arquivo CSV consolidado
- Compactado em:
```
consolidado_despesas.zip
```


Pronto para:
- Análises financeiras
- Auditorias
- Processos regulatórios
- Consumo por pipelines analíticos

---

## 8. Considerações Finais

O projeto foi desenvolvido priorizando:
- Resiliência a dados heterogêneos
- Boas práticas de engenharia de dados
- Clareza técnica
- Transparência no tratamento de inconsistências
- Aderência aos requisitos do teste técnico

Toda a solução é baseada exclusivamente em **dados públicos oficiais da ANS**.

## 9. Enriquecimento de Dados (Teste 2.2)

Foi realizado o enriquecimento do CSV consolidado utilizando os dados cadastrais das operadoras ativas (CADOP).

### Estratégia de Join
- Tipo: LEFT JOIN
- Chave: CNPJ

Essa abordagem garante que nenhum registro financeiro seja perdido, mesmo quando não há correspondência cadastral.

### Tratamento de Falhas

**Registros sem match no cadastro**
- Mantidos no dataset
- Campos cadastrais preenchidos como nulos
- Flag `CadastroEncontrado = false`

**CNPJs duplicados no cadastro**
- Mantido apenas um registro por CNPJ
- Flag `CadastroDuplicado = true` para sinalização

### Trade-off Técnico
O join foi realizado em memória, considerando:
- Volume reduzido dos dados
- Simplicidade e clareza da solução
- Ausência de impacto relevante em consumo de recursos

## 10. Agregação de Despesas (Teste 2.3)

Foi realizada a agregação dos dados enriquecidos com o objetivo de analisar o comportamento financeiro das operadoras por unidade federativa.

### Estratégia de Agregação
Os dados foram agrupados por:
- RazaoSocial
- UF

Para cada grupo foram calculados:
- TotalDespesas: soma total das despesas
- MediaDespesasTrimestre: média das despesas por trimestre
- DesvioPadraoDespesas: medida de variabilidade das despesas

### Ordenação
Os resultados foram ordenados pelo valor total de despesas, do maior para o menor, facilitando a identificação das operadoras com maior impacto financeiro.

### Trade-off Técnico
A agregação e ordenação foram realizadas em memória utilizando Pandas, considerando:
- Volume reduzido de dados
- Eficiência das operações vetorizadas
- Simplicidade da solução

Em cenários de maior escala, essa etapa poderia ser migrada para processamento distribuído ou bancos analíticos.

## 11. Teste de Banco de Dados e Análise (MySQL 8.0)

Esta etapa utiliza o MySQL 8.0 para estruturar as tabelas e importar os dados gerados nas etapas anteriores:

- `consolidado_despesas.csv` (Teste 1.3)
- `despesas_agregadas.csv` (Teste 2.3)
- `Relatorio_cadop.csv` (CADOP – dados cadastrais das operadoras)

---

### 11.1 Importação dos CSVs (3.3)

#### Estratégia adotada: Staging + Carga tratada
Para atender aos requisitos de validação e tratamento de inconsistências durante a importação, foi adotada a estratégia:

1. **Importar os CSVs para tabelas de staging (`stg_*`)**
   - Todas as colunas são carregadas como `VARCHAR`
   - Evita falhas de importação por tipo incorreto
   - Permite validação e limpeza antes da inserção final

2. **Inserir os dados nas tabelas finais (`operadoras`, `despesas_consolidadas`, `despesas_agregadas`)**
   - Conversões explícitas (`CAST`)
   - Limpeza de campos (`TRIM`, `REGEXP_REPLACE`)
   - Rejeição de registros inválidos (via cláusulas `WHERE`)

Essa abordagem é mais robusta, pois impede que inconsistências contaminem as tabelas analíticas finais e permite contabilizar/explicar rejeições.

---

### 11.2 Encoding utilizado
- Os arquivos gerados pelo pipeline em Python (`consolidado_despesas.csv` e `despesas_agregadas.csv`) são carregados com `UTF-8` (`CHARACTER SET utf8mb4`).
- O arquivo do CADOP (`Relatorio_cadop.csv`) pode estar em `latin1` (conforme padrão frequente de arquivos ANS). Por isso, na importação foi utilizado `CHARACTER SET latin1` para evitar caracteres corrompidos.

---

### 11.3 Tratamento de inconsistências durante a importação

Durante o carregamento e conversão dos dados, foram tratadas as seguintes inconsistências:

#### a) Valores `NULL` (ou vazios) em campos obrigatórios
Exemplos: `CNPJ`, `Ano`, `Trimestre`, `UF`, `RazaoSocial`.

**Tratamento adotado:** rejeitar registro na carga final.  
Implementação: filtros `WHERE` nas queries de inserção (ex.: CNPJ com 14 dígitos, ano com 4 dígitos, trimestre entre 1 e 4).

**Justificativa:** registros incompletos inviabilizam análises e podem gerar resultados incorretos.

---

#### b) Strings em campos numéricos
Exemplos: valores monetários contendo caracteres inesperados.

**Tratamento adotado:**
- Tentativa de conversão controlada com `REGEXP`
- Caso não seja possível converter → valor vira `NULL` e o registro pode ser rejeitado (quando necessário)

**Justificativa:** evita conversões automáticas incorretas do MySQL (por exemplo, texto virando `0` silenciosamente).

---

#### c) Formatos numéricos inconsistentes (vírgula/ponto)
Durante a importação foram identificados formatos distintos:
- `1234.56` (padrão US)
- `1.234,56` (padrão BR)

**Tratamento adotado:** regra condicional:
- Se o valor contém `,` → considera formato BR (remove `.` de milhar e troca `,` por `.`)
- Caso contrário → considera formato US (mantém o ponto decimal)

**Justificativa:** garante conversão correta para `DECIMAL`, evitando erro de `Out of range` e distorções.

---

#### d) Datas inconsistentes
O modelo final foi estruturado com `Ano` e `Trimestre` (tipos `YEAR` e `TINYINT`), evitando dependência de parsing de datas completas no banco.

**Tratamento adotado:** validação de ano/trimestre via regex e conversão com `CAST`.

**Justificativa:** reduz complexidade e aumenta robustez, mantendo o período temporal de forma padronizada.

---

### 11.4 Observação sobre restrição do Workbench (LOAD DATA)
Durante a execução foi necessário lidar com restrições de leitura de arquivos no MySQL/Workbench.

- O MySQL pode restringir leitura a um diretório definido por:
  ```sql
  SELECT @@secure_file_priv;

## 11.5 Observação técnica (MySQL Workbench e LOCAL INFILE)

Durante a importação foi identificado o erro:

```
Error Code: 2068. LOAD DATA LOCAL INFILE file request rejected due to restrictions on access
```

Esse comportamento ocorre quando o cliente (Workbench) bloqueia o uso de LOCAL INFILE por segurança.

Solução adotada:

- Utilização de LOAD DATA INFILE (sem LOCAL)
- Posicionamento dos arquivos no diretório permitido por @@secure_file_priv

Essa abordagem foi a mais estável e compatível com a execução no MySQL Workbench.

---

## 12. Queries Analíticas (Teste 3.4)

Nesta etapa foram desenvolvidas queries analíticas sobre os dados consolidados para responder às perguntas propostas.

### 12.1 Query 1 — Top 5 operadoras com maior crescimento percentual

**Objetivo:** identificar as 5 operadoras com maior crescimento percentual de despesas entre o primeiro e o último trimestre analisado.

Tratamento de operadoras sem dados em todos os trimestres:

- Caso a operadora não possua valor no trimestre inicial ou final, não é possível calcular crescimento com consistência.
- Assim, operadoras sem pelo menos dois pontos temporais são descartadas do ranking.

---

### 12.2 Query 2 — Distribuição de despesas por UF (Top 5 estados)

**Objetivo:** calcular o total de despesas por UF e listar os 5 estados com maiores despesas.

Desafio adicional implementado:

- cálculo da média de despesas por operadora em cada UF, além do total.

---

### 12.3 Query 3 — Operadoras acima da média geral em pelo menos 2 dos 3 trimestres

**Objetivo:** identificar quantas operadoras tiveram despesas acima da média geral em pelo menos 2 dos 3 trimestres analisados.

Abordagem adotada (Opção A)

Foi escolhida a abordagem de contagem agregada, retornando explicitamente o número de operadoras que satisfazem a condição.

Resultado observado no dataset analisado:

- Nenhuma operadora ficou acima da média em pelo menos 2 dos 3 trimestres.
- O resultado final da query é **0**.

Justificativa:

O comportamento do dataset indica que, apesar de existirem operadoras acima da média em 1 trimestre, não há recorrência suficiente em 2 ou mais períodos para atender à condição proposta.

---

### 12.4 Trade-off técnico (Query 3)

A Query 3 pode ser implementada de diversas formas, incluindo:

- subqueries aninhadas
- CTEs (Common Table Expressions)
- funções de janela (window functions)

Estratégia escolhida: uso de CTEs com agregações intermediárias.

Justificativa:

- **Performance:** permite reduzir volume intermediário via agregação por trimestre antes de comparar com médias.
- **Legibilidade:** o raciocínio fica explícito (períodos → média por período → comparação → contagem).
- **Manutenibilidade:** facilita ajuste para outros números de trimestres ou critérios.

---

## 13. Como executar o projeto

### 13.1 Requisitos

- Python 3.x
- Bibliotecas: pandas, requests, bs4
- MySQL 8.0 + MySQL Workbench

---

### 13.2 Execução (pipeline em Python)

Baixar últimos 3 trimestres e extrair ZIPs:

```
python acesso_api.py
python processamento_arquivos.py
```

Consolidar dados e gerar consolidado_despesas.zip:

```
python consolidacao_dados.py
```

Validar dados:

```
python validacao_dados.py
```

Enriquecer com CADOP:

```
python enriquecimento_dados.py
```

Agregar e gerar despesas_agregadas.csv:

```
python agregacao_despesas.py
```

---

### 13.3 Execução (MySQL)

Criar schema e tabelas:

- Executar script DDL (.sql) no Workbench

Importar dados:

- Carregar CSVs em tabelas staging via LOAD DATA INFILE
- Inserir dados nas tabelas finais com as queries de conversão

Rodar queries analíticas:

- Executar as queries do item 3.4

---

## 4.2 Trade-offs técnicos — Backend (FastAPI)

### 4.2.1 Escolha do Framework
**Escolha:** FastAPI (Opção B)

**Justificativa:**
- **Complexidade/boilerplate menor:** validação e serialização com Pydantic reduzem código manual.
- **Documentação automática:** geração nativa de OpenAPI/Swagger facilita testes e integração (incluindo Postman).
- **Performance e escalabilidade:** execução em ASGI e compatibilidade com rotas assíncronas (quando necessário).
- **Manutenção:** tipagem e contratos de resposta ajudam a manter consistência do backend.

### 4.2.2 Estratégia de Paginação
**Escolha:** Offset-based (Opção A) via parâmetros `page` e `limit`.

**Justificativa:**
- O volume de operadoras é significativo, mas **compatível com paginação tradicional** no contexto do teste.
- Dados possuem **baixa frequência de atualização**, reduzindo problemas de inconsistência típicos de offset.
- É a abordagem **mais simples para o frontend**, permitindo controle direto de página atual e total.

### 4.2.3 Cache vs Queries Diretas na rota `/api/estatisticas`
**Escolha:** Cachear resultado por X minutos (Opção B), com TTL em memória.

**Justificativa:**
- Estatísticas agregadas (total, média, top 5, distribuição por UF) podem envolver queries mais custosas.
- O dataset do teste é relativamente estável (pouca mutação), então o cache não compromete consistência.
- Melhora latência e reduz carga no banco sem necessidade de tabelas auxiliares.

### 4.2.4 Estrutura de Resposta da API
**Escolha:** Dados + Metadados (Opção B).

Exemplo:
```json
{
  "data": [{...}],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

**Justificativa:**
- Simplifica a implementação da paginação no frontend (não exige request extra para contagem).
- Melhora UX ao permitir exibir total de registros, página atual e controle de navegação.


## 14. Empacotamento final

Ao final do projeto, todos os arquivos de código e scripts SQL devem ser compactados em:

```
Teste_DalvanOliveira.zip
```

Incluindo:

- scripts Python
- scripts SQL
- README.md
- CSVs gerados (quando aplicável)