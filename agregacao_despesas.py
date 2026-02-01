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

# Função principal para agregar os dados
def agregar_dados():
    df = pd.read_csv(csv_entrada)

    # Considerar apenas valores válidos
    df = df[df["RegistroValido"] == True]

    # Agregação por Razão Social e UF
    agrupado = (
        df
        .groupby(["RazaoSocial", "UF"], as_index=False)
        .agg(
            TotalDespesas=("ValorDespesas", "sum"),
            MediaDespesasTrimestre=("ValorDespesas", "mean"),
            DesvioPadraoDespesas=("ValorDespesas", "std")
        )
    )

    # Ordenar do maior para o menor
    agrupado = agrupado.sort_values(
        by="TotalDespesas",
        ascending=False
    )

    return agrupado

# Execução do script
if __name__ == "__main__":
    extrair_zip()
    df_agregado = agregar_dados()
    df_agregado.to_csv(csv_saida, index=False)

    print("Agregação concluída")
    print(f"Arquivo gerado: {csv_saida}")