import pandas as pd
import zipfile
import os

# Definição dos nomes dos arquivos
csv_consolidado = "consolidado_despesas_validado.csv"
csv_cadop = "Relatorio_cadop.csv"
csv_saida = "consolidado_despesas_enriquecido.csv"
zip_saida = "consolidado_despesas_enriquecido.zip"

# Função para carregar e tratar o arquivo CADOP
def carregar_cadop():
    df = pd.read_csv(csv_cadop, sep=";", encoding="latin1")

    df.columns = df.columns.str.lower()

    df = df.rename(columns={
        "cnpj": "CNPJ",
        "registro_operadora": "RegistroANS",
        "modalidade": "Modalidade",
        "uf": "UF"
    })

    # Remover CNPJs inválidos
    df["CNPJ"] = df["CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["CNPJ"].str.len() == 14]

    # Tratar duplicidades
    df["CadastroDuplicado"] = df.duplicated(subset=["CNPJ"], keep=False)

    df = df.drop_duplicates(subset=["CNPJ"], keep="first")

    return df[["CNPJ", "RegistroANS", "Modalidade", "UF", "CadastroDuplicado"]]

# Função principal para enriquecer os dados
def enriquecer_dados():
    df_consolidado = pd.read_csv(csv_consolidado, dtype={"CNPJ": str})
    df_cadop = carregar_cadop()

    df_final = df_consolidado.merge(
        df_cadop,
        on="CNPJ",
        how="left"
    )

    df_final["CadastroEncontrado"] = ~df_final["RegistroANS"].isna()

    return df_final
