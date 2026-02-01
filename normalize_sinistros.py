import os
import pandas as pd

expressao_alvo = "despesas com eventos / sinistros"
extensoes_suportadas = (".csv", ".txt", ".xlsx")

# Função para carregar o arquivo com a codificação correta
def carregar_arquivo(caminho):
    if caminho.lower().endswith(".csv"):
        return pd.read_csv(caminho, sep=";", encoding="latin1")
    elif caminho.lower().endswith(".txt"):
        return pd.read_csv(caminho, sep=";", encoding="latin1")
    elif caminho.lower().endswith(".xlsx"):
        return pd.read_excel(caminho)
    else:
        return None

# Função para normalizar o DataFrame
def normalizar_arquivo(caminho):

    # Carregar o arquivo
    df = carregar_arquivo(caminho)
    if df is None:
        return None

    # Padronizar nomes de colunas
    df.columns = [c.strip().lower() for c in df.columns]

    # Verificar se todas as colunas necessárias estão presentes
    colunas_necessarias = {
        "data",
        "reg_ans",
        "descricao",
        "vl_saldo_final"
    }

    if not colunas_necessarias.issubset(df.columns):
        return None

    # Filtrar apenas a categoria desejada
    df["descricao"] = df["descricao"].astype(str).str.lower()
    df = df[df["descricao"] == expressao_alvo]

    # Verificar se o DataFrame resultante está vazio
    if df.empty:
        return None

    # Normalizar valor monetário
    df["valor"] = (
        df["vl_saldo_final"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )


    return df[["data", "reg_ans", "descricao", "valor"]]
