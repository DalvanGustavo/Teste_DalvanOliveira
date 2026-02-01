import pandas as pd
import zipfile
import os
import re

# Definição dos nomes dos arquivos
zip_entrada = "consolidado_despesas.zip"
csv_entrada = "consolidado_despesas.csv"
csv_saida = "consolidado_despesas_validado.csv"

# Função para extrair o arquivo ZIP
def extrair_zip():
    if not os.path.exists(zip_entrada):
        raise FileNotFoundError(f"Arquivo {zip_entrada} não encontrado.")

    with zipfile.ZipFile(zip_entrada, "r") as zip_ref:
        zip_ref.extractall(".")

    if not os.path.exists(csv_entrada):
        raise FileNotFoundError(
            f"{csv_entrada} não encontrado após extração."
        )

