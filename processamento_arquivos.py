import os
import zipfile

# Processar os arquivos ZIP baixados
diretorio_atual = os.getcwd()

# Iterar sobre os arquivos no diretório atual
for arquivo in os.listdir(diretorio_atual):

    # Verificar se o arquivo é um ZIP
    if not arquivo.lower().endswith(".zip"):
        continue

    # Definir o caminho completo do arquivo ZIP e a pasta de destino
    caminho_zip = os.path.join(diretorio_atual, arquivo)
    nome_base = os.path.splitext(arquivo)[0]
    pasta_destino = os.path.join(diretorio_atual, nome_base)

