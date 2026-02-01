
# Projeto de Consolidação de Despesas com Eventos / Sinistros – ANS

## 1. Apresentação do Projeto

Este projeto foi desenvolvido como parte de um **teste técnico de engenharia de dados**, utilizando dados públicos disponibilizados pela **Agência Nacional de Saúde Suplementar (ANS)**.

O objetivo é **automatizar a ingestão, processamento, normalização e consolidação** das informações de **Despesas com Eventos / Sinistros**, referentes aos **últimos três trimestres disponíveis**, garantindo resiliência a variações de formato, estrutura e qualidade dos dados.

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
- Formatos variados: CSV, TXT e XLSX
- Estruturas de colunas não totalmente padronizadas
- Possibilidade de múltiplos arquivos por trimestre

Esses arquivos contêm os valores contábeis, incluindo a categoria **“Despesas com Eventos / Sinistros”**, identificada no campo descritivo das contas.

---

### 2.2 Cadastro de Operadoras Ativas (CADOP)

Fonte:
```
https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv
```

Justificativa técnica para uso do arquivo adicional:

Os arquivos de demonstrações contábeis **não contêm diretamente CNPJ e Razão Social** das operadoras. Eles utilizam o identificador:

- `REG_ANS`

No cadastro CADOP, o campo equivalente é:

- `Registro_Operadora`

Esses campos representam o **mesmo identificador oficial da ANS**, sendo a única chave confiável para:
- Enriquecer os dados contábeis
- Associar corretamente **CNPJ** e **Razão Social**
- Garantir integridade referencial

Sem esse arquivo adicional, não seria possível atender ao requisito de consolidação com identificação empresarial.

---

## 3. Estratégia de Processamento

### 3.1 Modelo de Processamento: Incremental

Foi adotado o **processamento incremental**, no qual cada arquivo é:
1. Lido individualmente
2. Filtrado
3. Normalizado
4. Consolidado

Justificativa:
- Redução do consumo de memória
- Maior robustez frente a grandes volumes de dados
- Facilidade de tratamento de falhas parciais
- Escalabilidade para inclusão de novos períodos

---

## 4. Normalização dos Dados

### Estrutura final padronizada:

| Coluna           | Descrição |
|------------------|-----------|
| CNPJ             | CNPJ da operadora |
| RazaoSocial      | Razão social da operadora |
| Ano              | Ano de referência |
| Trimestre        | Trimestre de referência |
| ValorDespesas    | Valor consolidado de despesas |
| RazaoSocialSuspeita | Indicador de inconsistência cadastral |

---

## 5. Tratamento de Inconsistências

Durante a consolidação, foram identificadas as seguintes situações:

### 5.1 CNPJs com múltiplas razões sociais
- Tratamento: **marcação como suspeito**
- Justificativa: preservação da informação sem descarte indevido

### 5.2 Valores zerados ou negativos
- Tratamento: **anulados**
- Justificativa: valores incompatíveis com despesas operacionais

### 5.3 Datas inconsistentes
- Tratamento: **descartadas**
- Justificativa: impossibilidade de inferir trimestre com segurança

---

## 6. Entrega Final

- Arquivo CSV consolidado
- Compactação em:
```
consolidado_despesas.zip
```

Pronto para:
- Análises financeiras
- Auditorias
- Processos regulatórios
- Consumo por pipelines analíticos

---

## 7. Considerações Finais

O projeto foi desenvolvido priorizando:
- Resiliência a dados heterogêneos
- Clareza técnica
- Aderência a boas práticas de engenharia de dados
- Transparência no tratamento de inconsistências

Toda a solução é baseada exclusivamente em **dados públicos oficiais da ANS**.
