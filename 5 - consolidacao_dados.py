import re
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

def normalizar_cnpj(valor):
    s = str(valor).strip()

    # remove .0 se existir
    if s.endswith(".0"):
        s = s[:-2]

    # mantém apenas dígitos
    s = re.sub(r"\D", "", s)

    # se ficou com 15 e termina em 0 (efeito float), remove o último
    if len(s) == 15 and s.endswith("0"):
        s = s[:-1]

    # completa para 14
    s = s.zfill(14)

    # se não for 14, marca como NA
    if len(s) != 14:
        return None

    return s


def carregar_cadastro_operadoras():
    baixar_cadastro_operadoras()

    # FORÇAR tudo como string
    df = pd.read_csv(cadop_arquivo, sep=";", encoding="latin1", dtype=str)
    df.columns = [c.lower().strip() for c in df.columns]

    df = df.rename(columns={
        "registro_operadora": "reg_ans",
        "razao_social": "razaosocial"
    })

    # normalizar campos-chave
    df["reg_ans"] = df["reg_ans"].astype(str).str.strip()
    df["cnpj"] = df["cnpj"].apply(normalizar_cnpj)

    # remove cadastros sem CNPJ normalizado
    df = df.dropna(subset=["cnpj"])

    return df[["reg_ans", "cnpj", "razaosocial"]]

# Função para consolidar dados de todos os arquivos relevantes
def consolidar_dados(diretorio_base):
    registros = []
    cnpj_razao_map = defaultdict(set)

    cadastro = carregar_cadastro_operadoras()

    # Iterar sobre as pastas extraídas
    for pasta in os.listdir(diretorio_base):
        if not os.path.isdir(pasta):
            continue

        # Construir o caminho completo da pasta
        for arquivo in os.listdir(pasta):
            if not arquivo.lower().endswith(extensoes_suportadas):
                continue

            caminho = os.path.join(pasta, arquivo)
            df = carregar_arquivo(caminho)
            if df is None:
                continue

            df.columns = [c.lower() for c in df.columns]

            colunas_necessarias = {
                "reg_ans", "data", "descricao", "vl_saldo_final"
            }
            if not colunas_necessarias.issubset(df.columns):
                continue

            df["descricao"] = df["descricao"].astype(str).str.lower()
            df = df[df["descricao"] == expressao_alvo]
            if df.empty:
                continue

            df["vl_saldo_final"] = (
                df["vl_saldo_final"]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df["vl_saldo_final"] = pd.to_numeric(
                df["vl_saldo_final"], errors="coerce"
            )
            df = df.dropna(subset=["vl_saldo_final"])

            df["Ano"], df["Trimestre"] = zip(
                *df["data"].apply(extrair_ano_trimestre)
            )
            df = df.dropna(subset=["Ano", "Trimestre"])

            # Garantir o mesmo tipo nos dois lados do merge
            df["reg_ans"] = (df["reg_ans"].astype(str).str.strip().str.replace(r"\D", "", regex=True))
            cadastro["reg_ans"] = (cadastro["reg_ans"].astype(str).str.strip().str.replace(r"\D", "", regex=True))

            df = df.merge(cadastro, on="reg_ans", how="left")

            # manter vazio em vez de "NAO_ENCONTRADO" para não poluir CNPJ
            df["cnpj"] = df["cnpj"].fillna("")
            df["razaosocial"] = df["razaosocial"].fillna("")

            for _, row in df.iterrows():
                cnpj_razao_map[row["cnpj"]].add(row["razaosocial"])

                registros.append({
                    "CNPJ": row["cnpj"],
                    "RazaoSocial": row["razaosocial"],
                    "Ano": int(row["Ano"]),
                    "Trimestre": int(row["Trimestre"]),
                    "ValorDespesas": float(row["vl_saldo_final"])
                })

    return pd.DataFrame(registros), cnpj_razao_map

# Função para tratar inconsistências nos dados
def tratar_inconsistencias(df, cnpj_razao_map):
    df.loc[df["ValorDespesas"] <= 0, "ValorDespesas"] = None

    df["RazaoSocialSuspeita"] = df["CNPJ"].apply(
        lambda cnpj: len(cnpj_razao_map[cnpj]) > 1
    )

    return df

# Função para gerar o arquivo ZIP com o CSV consolidado
def gerar_zip(df, nome_csv="consolidado_despesas.csv"):
    df.to_csv(nome_csv, index=False)

    with zipfile.ZipFile(
        "consolidado_despesas.zip",
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:
        zipf.write(nome_csv)

    os.remove(nome_csv)

if __name__ == "__main__":
    df, mapa_cnpj = consolidar_dados(".")
    df_tratado = tratar_inconsistencias(df, mapa_cnpj)
    gerar_zip(df_tratado)

    print("consolidado_despesas.zip gerado com sucesso")