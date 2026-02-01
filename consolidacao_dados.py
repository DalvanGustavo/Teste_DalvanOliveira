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