import os
import pandas as pd

# Definir a expressão alvo e as extensões de arquivo suportadas
expressao_alvo = "despesas com eventos / sinistros"
extensoes_suportadas = (".csv", ".txt", ".xlsx")

# Função para verificar se o DataFrame contém a expressão alvo
def contem_expressao_alvo(df):
    df_str = df.astype(str).apply(lambda col: col.str.lower())
    return df_str.apply(lambda col: col.str.contains(expressao_alvo, regex=False, na=False)).any().any()

# Função para verificar se um arquivo contém a expressão alvo
def arquivo_contem_sinistros(caminho):

    # Tentar ler o arquivo com base na extensão
    try:
        if caminho.lower().endswith(".csv"):
            df = pd.read_csv(caminho, nrows=1000, sep=None, engine="python")
        elif caminho.lower().endswith(".txt"):
            df = pd.read_csv(caminho, nrows=1000, sep=";", engine="python")
        elif caminho.lower().endswith(".xlsx"):
            df = pd.read_excel(caminho, nrows=1000)
        else:
            return False

        return contem_expressao_alvo(df)

    except Exception:
        return False
