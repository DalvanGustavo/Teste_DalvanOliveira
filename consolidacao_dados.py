import os
import zipfile
import requests
import pandas as pd
from collections import defaultdict

extensoes_suportadas = (".csv", ".txt", ".xlsx")
expressao_alvo = "despesas com eventos / sinistros"

# URL e nome do arquivo do cadastro de operadoras
cadop_url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
cadop_arquivo = "Relatorio_cadop.csv"

# Função para baixar o cadastro de operadoras, se necessário
def baixar_cadastro_operadoras():
    if os.path.exists(cadop_arquivo):
        return

    print("Baixando Relatorio_cadop.csv...")
    resposta = requests.get(cadop_url, timeout=60)
    resposta.raise_for_status()

    with open(cadop_arquivo, "wb") as f:
        f.write(resposta.content)

    print("Cadastro de operadoras baixado com sucesso")

# Funções auxiliares
def carregar_arquivo(caminho):
    
    # Tentar ler o arquivo com base na extensão
    try:
        if caminho.lower().endswith((".csv", ".txt")):
            return pd.read_csv(caminho, sep=";", encoding="latin1")
        elif caminho.lower().endswith(".xlsx"):
            return pd.read_excel(caminho)
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
    return None

# Função para extrair ano e trimestre de uma data
def extrair_ano_trimestre(valor_data):
    data = pd.to_datetime(valor_data, errors="coerce", dayfirst=True)
    if pd.isna(data):
        return None, None
    trimestre = (data.month - 1) // 3 + 1
    return data.year, trimestre

# Função para carregar o cadastro de operadoras
def carregar_cadastro_operadoras():
    baixar_cadastro_operadoras()
    df = pd.read_csv(cadop_arquivo, sep=";", encoding="latin1")
    df.columns = [c.lower() for c in df.columns]

    df = df.rename(columns={
        "registro_operadora": "reg_ans",
        "razao_social": "razaosocial"
    })

    return df[["reg_ans", "cnpj", "razaosocial"]]
