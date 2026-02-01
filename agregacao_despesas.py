import pandas as pd
import zipfile

# Definição dos nomes dos arquivos
zip_entrada = "consolidado_despesas_enriquecido.zip"
csv_entrada = "consolidado_despesas_enriquecido.csv"
csv_saida = "despesas_agregadas.csv"

# Função para extrair o arquivo ZIP
def extrair_zip():
    with zipfile.ZipFile(zip_entrada, "r") as zip_ref:
        zip_ref.extractall(".")
