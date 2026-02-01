import os
import pandas as pd

# Definir a expressão alvo e as extensões de arquivo suportadas
expressao_alvo = "despesas com eventos / sinistros"
extensoes_suportadas = (".csv", ".txt", ".xlsx")

# Função para verificar se o DataFrame contém a expressão alvo
def contem_expressao_alvo(df):
    df_str = df.astype(str).apply(lambda col: col.str.lower())
    return df_str.apply(lambda col: col.str.contains(expressao_alvo, regex=False, na=False)).any().any()
