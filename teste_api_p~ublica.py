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