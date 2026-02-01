import os
import requests
from bs4 import BeautifulSoup
import re

base_url = "https://dadosabertos.ans.gov.br/FTP/PDA/"
palavra_chave_pasta = "demonstracoes_contabeis"

# Fazer a requisição para obter o conteúdo da página
try:
    resposta = requests.get(base_url)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Procurar links que contenham a palavra-chave especificada
    link_encontrados = ""
    for link in soup.find_all('a', href=True):
        if palavra_chave_pasta in link.get('href').lower():
            link_encontrados = link.get('href')
            break
    
    url_da_pasta_principal = f"{base_url}{link_encontrados}"
    
    # Acessar a pasta principal para listar os anos disponíveis
    resp_pasta = requests.get(url_da_pasta_principal)
    soup_pasta = BeautifulSoup(resp_pasta.text, 'html.parser')
    
    anos_encontrados = [a.get('href') for a in soup_pasta.find_all('a', href=True) if re.match(r'^\d{4}/', a.get('href'))]
    anos_ordenados = sorted(anos_encontrados, reverse=True)

    # Definir os padrões regex para os arquivos desejados
    padrao_1 = r'\d{4}_\d{1}_trimestre'
    padrao_2 = r'\d{8}_\d{1}T\d{4}'
    padrao_3 = r'\d{1}T\d{4}'
    regex_final = f"({padrao_1}|{padrao_2}|{padrao_3})"

    arquivos_baixados_count = 0

    # Iterar pelos anos para encontrar e baixar os arquivos desejados
    for ano in anos_ordenados:
        if arquivos_baixados_count >= 3:
            break
            
        url_ano = f"{url_da_pasta_principal}{ano}"
        print(f"Verificando ano: {ano}")
        
        res_ano = requests.get(url_ano)
        soup_ano = BeautifulSoup(res_ano.text, 'html.parser')

except Exception as e:
    print(f"Ocorreu um erro geral: {e}")