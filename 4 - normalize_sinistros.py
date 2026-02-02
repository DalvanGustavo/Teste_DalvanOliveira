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

# Função para consolidar dados de todos os arquivos relevantes
def consolidar_dados(diretorio_base, saida="despesas_sinistros_normalizado.csv"):
    consolidado = []

    # Iterar sobre as pastas extraídas
    for pasta in os.listdir(diretorio_base):
        if not os.path.isdir(pasta):
            continue
        
        # Construir o caminho completo da pasta
        for arquivo in os.listdir(pasta):
            if not arquivo.lower().endswith(extensoes_suportadas):
                continue

            caminho = os.path.join(pasta, arquivo)
            df_norm = normalizar_arquivo(caminho)

            if df_norm is not None:
                consolidado.append(df_norm)
                print(f"Normalizado: {caminho}")

    # Concatenar todos os DataFrames normalizados e salvar em CSV
    if consolidado:
        resultado = pd.concat(consolidado, ignore_index=True)
        resultado.to_csv(saida, index=False)
        print(f"\nDataset final gerado: {saida}")
    else:
        print("Nenhum dado relevante encontrado.")


if __name__ == "__main__":
    consolidar_dados(".")
