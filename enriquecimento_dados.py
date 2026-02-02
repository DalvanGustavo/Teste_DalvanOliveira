import pandas as pd
import zipfile
import os

# Definição dos nomes dos arquivos
csv_consolidado = "consolidado_despesas_validado.csv"
csv_cadop = "Relatorio_cadop.csv"
zip_validacao = "consolidado_despesas.zip"
csv_saida = "consolidado_despesas_enriquecido.csv"
zip_saida = "consolidado_despesas_enriquecido.zip"


def garantir_csv_validado():
    # Se já existe, ok
    if os.path.exists(csv_consolidado):
        return

    # Se não existe, avisar claramente com próximo passo
    raise FileNotFoundError(
        f"Não encontrei '{csv_consolidado}'.\n"
        f"Garanta que você executou a etapa 2.1 e que o arquivo está na mesma pasta.\n"
        f"Arquivos presentes: {os.listdir('.')}"
    )


# Função para carregar e tratar o arquivo CADOP
def carregar_cadop():
    df = pd.read_csv(csv_cadop, sep=";", encoding="latin1")

    # Normalizar colunas
    df.columns = df.columns.str.lower().str.strip()

    # 🔍 Identificar coluna de UF dinamicamente
    possiveis_ufs = ["uf", "sigla_uf", "uf_operadora", "sg_uf"]
    coluna_uf = next((c for c in possiveis_ufs if c in df.columns), None)

    if coluna_uf is None:
        raise ValueError("Coluna de UF não encontrada no arquivo CADOP")

    df = df.rename(columns={
        "cnpj": "CNPJ",
        "registro_operadora": "RegistroANS",
        "modalidade": "Modalidade",
        coluna_uf: "UF"
    })

    # Limpar CNPJ
    df["CNPJ"] = (
        df["CNPJ"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
    )

    df = df[df["CNPJ"].str.len() == 14]

    # Tratar duplicidades
    df["CadastroDuplicado"] = df.duplicated(subset=["CNPJ"], keep=False)
    df = df.drop_duplicates(subset=["CNPJ"], keep="first")

    return df[["CNPJ", "RegistroANS", "Modalidade", "UF", "CadastroDuplicado"]]

# Função principal para enriquecer os dados


def enriquecer_dados():
    garantir_csv_validado()

    df_consolidado = pd.read_csv(csv_consolidado, dtype={"CNPJ": str})

    # NORMALIZAÇÃO ESSENCIAL

    # Normalizar CNPJ do consolidado
    df_consolidado["CNPJ"] = (
        df_consolidado["CNPJ"]
        .astype(str)
        .str.strip()
        .str.replace(r"\D", "", regex=True)
        .str.zfill(14)
    )
    df_consolidado = df_consolidado[df_consolidado["CNPJ"].str.len() == 14]

    df_cadop = carregar_cadop()

    # Debug: taxa de match
    taxa_match = df_consolidado["CNPJ"].isin(df_cadop["CNPJ"]).mean()
    print(f"Taxa de match pré-merge (CNPJ): {taxa_match:.2%}")

    df_final = df_consolidado.merge(df_cadop, on="CNPJ", how="left")

    df_final["CadastroEncontrado"] = ~df_final["RegistroANS"].notna()

    return df_final


# Função para gerar o arquivo ZIP de saída
def gerar_zip(df):
    df.to_csv(csv_saida, index=False)

    with zipfile.ZipFile(zip_saida, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_saida)

    os.remove(csv_saida)

# Execução do script
if __name__ == "__main__":
    df_enriquecido = enriquecer_dados()
    gerar_zip(df_enriquecido)

    print(df_enriquecido[["RegistroANS", "Modalidade", "UF", "CadastroDuplicado"]].isna().mean())
    print("Enriquecimento concluído")
    print(f"Arquivo final gerado: {zip_saida}")