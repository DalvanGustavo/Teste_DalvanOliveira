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