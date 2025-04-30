from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import btreeDriver
import geraId
from openai import OpenAI

# ------------------------------------------------------
# Configuração de variáveis de ambiente e instâncias globais
# ------------------------------------------------------
load_dotenv()
API_KEY = os.environ.get('API_KEY')

# Inicializa cliente OpenAI com rotas customizadas
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Gerador global de IDs
ids = geraId.GeraId()
# Árvore B para gerenciar múltiplas instâncias de WebDriver
arvore = btreeDriver.btreeDriver(id=ids.gerar_id())

# Criação da aplicação Flask e configuração de CORS
app = Flask(__name__)
CORS(app)

# ------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------

def login(username: str, password: str, node_id: int) -> str:
    """
    Realiza o login no SIGA usando Selenium.
    1. Espera pelo campo de usuário
    2. Preenche usuário e senha
    3. Clica em confirmar
    4. Aguarda carregamento do nome e retorna JSON de sucesso ou falha
    """
    driver = arvore.encontra(node_id).getDriver()
    try:
        # Aguarda campo de usuário estar disponível
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.ID, "vSIS_USUARIOID"))
        )
        driver.find_element(By.ID, "vSIS_USUARIOID").send_keys(username)
        driver.find_element(By.ID, "vSIS_USUARIOSENHA").send_keys(password)
        driver.find_element(By.NAME, "BTCONFIRMA").click()

        # Aguarda elemento do nome
        WebDriverWait(driver, 4).until(
            EC.presence_of_all_elements_located((By.ID, "span_MPW0041vPRO_PESSOALNOME"))
        )
        raw_name = driver.find_element(By.ID, 'span_MPW0041vPRO_PESSOALNOME').text

        # Processa retorno do nome
        nome = raw_name[:-2].title().split()[0]
        response = {'bool': True, 'nome': nome, 'id': node_id}
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception:
        # Retorna falha de login
        return json.dumps({'bool': False}, ensure_ascii=False)


def notas_parciais(node_id: int) -> list:
    """
    Coleta notas parciais:
    1. Clica na aba "Notas Parciais"
    2. Lê linhas de disciplina e nota
    3. Filtra "Projeto Integrador"
    4. Retorna lista de dicionários com nome e nota
    """
    driver = arvore.encontra(node_id).obtemDriver()

    try:
        # Seleciona aba de notas parciais
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel10Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel10Span").click()

        # Coleta notas e nomes
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        notas_elems = driver.find_elements(By.XPATH,
            "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        materias_elems = driver.find_elements(By.XPATH,
            "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")

        notas = [n.text for n in notas_elems]
        materias = []

        # Filtra disciplinas de projeto integrador
        for idx, elem in enumerate(materias_elems):
            if elem.text.startswith("Projeto Integrador"):
                notas.pop(idx)
            else:
                materias.append(elem.text)

        # Monta estrutura de retorno
        return [
            {"tipo": '', "nome": mat, "nota": nota, 'abc': 'D'}
            for mat, nota in zip(materias, notas)
        ]

    except Exception:
        print("Falha ao coletar notas parciais")
        return []


def notas_historicas(node_id: int) -> list:
    """
    Coleta notas históricas:
    1. Clica na aba "Notas Histórico"
    2. Lê linhas de disciplina e nota
    3. Filtra "Projeto Integrador"
    4. Retorna lista de dicionários com tipo 'h', nome e nota
    """
    driver = arvore.encontra(node_id).obtemDriver()

    try:
        # Seleciona aba histórico
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel8Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel8Span").click()

        # Coleta notas e nomes
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        notas_elems = driver.find_elements(By.XPATH,
            "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        materias_elems = driver.find_elements(By.XPATH,
            "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")

        notas = [n.text for n in notas_elems]
        materias = []

        # Filtra disciplinas de projeto integrador
        for idx, elem in enumerate(materias_elems):
            if elem.text.startswith("Projeto Integrador"):
                notas.pop(idx)
            else:
                materias.append(elem.text)

        # Monta estrutura de retorno
        return [
            {"tipo": 'h', "nome": mat, "nota": nota, 'abc': 'D'}
            for mat, nota in zip(materias, notas)
        ]

    except Exception:
        print("Falha ao coletar notas históricas")
        return []

# ------------------------------------------------------
# Rotas da API
# ------------------------------------------------------

@app.route('/api/login', methods=['POST'])
def receber_login():
    """
    Endpoint: /api/login
    Recebe JSON {usuario, senha}, inicializa WebDriver e realiza login
    Retorna JSON com status e nome do usuário
    """
    data = request.json
    user = data.get('usuario')
    pwd = data.get('senha')

    # Configurações do ChromeDriver
    chrome_opts = Options()
    chrome_opts.add_experimental_option('detach', True)

    # Gera ID e insere nó na árvore
    node_id = ids.geraId()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_opts
    )
    arvore.insere_no(id=node_id, driver=driver)

    # Navega até a página de login
    driver.get('https://siga.cps.sp.gov.br/aluno/login.aspx?')

    # Chama função de login e retorna resultado
    response = login(user, pwd, node_id)
    return response


@app.route('/api/notas', methods=['POST'])
def scrape_notas():
    """
    Endpoint: /api/notas
    Recebe JSON {id}, retorna notas parciais e históricas para o respectivo WebDriver
    """
    data = request.json
    node_id = data.get('id')

    parciais = notas_parciais(node_id)
    historicas = notas_historicas(node_id)

    return json.dumps({
        "parciais": parciais,
        "historicas": historicas
    }, ensure_ascii=False, indent=4)


@app.route('/api/relatorioIA', methods=['POST'])
def relatorio_ia():
    """
    Endpoint: /api/relatorioIA
    Gera relatório em HTML/CSS usando OpenAI
    """
    req = request.json
    notas = req.get('Notas')

    tipo = 'markdown'

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        model="meta-llama/llama-4-maverick:free",
        messages=[
            {
                "role": "user", "content": [
                    {
                        "type": "text",
                        "text": notas
                    },
                    {
                        "type": "text", 
                        "text": f"Me retorne a resposta em {tipo}"
                    }
                ]
            }
        ]
    )
    return completion.choices[0].message.content


if __name__ == '__main__':
    # Executa a aplicação em modo debug
    app.run(debug=True)
