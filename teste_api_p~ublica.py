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

except Exception as e:
    print(f"Ocorreu um erro geral: {e}")