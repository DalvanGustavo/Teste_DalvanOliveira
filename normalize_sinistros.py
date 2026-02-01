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

