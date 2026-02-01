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

# Função principal para identificar arquivos relevantes
def identificar_arquivos_sinistros(diretorio_base):
    arquivos_relevantes = []

    # Iterar sobre as pastas extraídas
    for pasta in os.listdir(diretorio_base):
        if not os.path.isdir(pasta):
            continue

        # Construir o caminho completo da pasta
        for arquivo in os.listdir(pasta):
            if not arquivo.lower().endswith(extensoes_suportadas):
                continue

            caminho = os.path.join(pasta, arquivo)

            # Verificar se o arquivo contém a expressão alvo
            if arquivo_contem_sinistros(caminho):
                print(f"Contém 'Despesas com Eventos / Sinistros': {caminho}")
                arquivos_relevantes.append(caminho)
            else:
                print(f"Ignorado: {caminho}")

    return arquivos_relevantes

# Executar a função principal
if __name__ == "__main__":
    arquivos = identificar_arquivos_sinistros(".")