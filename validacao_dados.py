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

# Função para validar CNPJ
def validar_cnpj(cnpj):

    # Remover caracteres não numéricos
    cnpj = re.sub(r"\D", "", str(cnpj))

    # Verificar tamanho e sequências inválidas
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    # Cálculo dos dígitos verificadores
    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(cnpj_parcial[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos_1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos_2 = [6] + pesos_1

    # Cálculo dos dígitos verificadores
    dig1 = calcular_digito(cnpj[:12], pesos_1)
    dig2 = calcular_digito(cnpj[:13], pesos_2)

    return cnpj[-2:] == dig1 + dig2

# Função principal para validar os dados
def validar_dados():
    df = pd.read_csv(csv_entrada)

    # Validação do CNPJ
    df["CNPJ_Valido"] = df["CNPJ"].apply(validar_cnpj)

    # Validação do Valor das Despesas
    df["ValorValido"] = df["ValorDespesas"].apply(
        lambda x: x > 0 if pd.notna(x) else False
    )

    # Validação da Razão Social
    df["RazaoSocialValida"] = (
        df["RazaoSocial"].astype(str).str.strip() != ""
    )

    # Registro final válido
    df["RegistroValido"] = (
        df["CNPJ_Valido"] &
        df["ValorValido"] &
        df["RazaoSocialValida"]
    )

    df.to_csv(csv_saida, index=False)

# Execução do script
if __name__ == "__main__":
    extrair_zip()
    validar_dados()
    print("Validação concluída. Arquivo consolidado_despesas_validado.csv gerado.")
