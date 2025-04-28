from flask import Flask, request, jsonify
from flask_cors import CORS

import uuid
import json
from flask import jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import btreeDriver
import geraId


# Instanciar o gerador de ID
ids = geraId.GeraId()

# Instanciar o primeiro nó
arvore = btreeDriver.ArvDriver(id = ids.geraId())

def login(u: str, s: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).getDriver()
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.ID, "vSIS_USUARIOID"))
        )
        driver.find_element(By.ID, "vSIS_USUARIOID").send_keys(u)
        driver.find_element(By.ID, "vSIS_USUARIOSENHA").send_keys(s)
        driver.find_element(By.NAME, "BTCONFIRMA").click()
        try:
            WebDriverWait(driver, 4).until(
                EC.presence_of_all_elements_located((By.ID, "span_MPW0041vPRO_PESSOALNOME"))
            )
            nome = driver.find_element(By.ID, 'span_MPW0041vPRO_PESSOALNOME').text
            nome = nome[0:-2]
            nome = nome.title().split()[0]

            resposta = {'bool': True, 'nome': nome, 'id': id}
            resposta = json.dumps(resposta, ensure_ascii=False, indent=4)

            # print('Sucesso no login, retornando True')  # Adicionar em caso de testes
            return resposta
        except:
            # print("Falha no login, retornando False")  # Adicionar em caso de testes
            return {'bool': False}
    except:
        print("Login não encontrado")


def notas_parciais(id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    # print(f'Pegando notas parciais do driver ID: {arvore.encontra(id).obtemId()}, Driver: {driver}') # Adicionar em caso de testes
    # Clicar no aba Notas Parciais
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel10Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel10Span").click()
    except:
        print("Botão não encontrado")

    # Pegar notas parciais
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        
        notas_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        notas = [nota.text for nota in notas_ele]
        mates_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")
        mates = []
        
        for i in range(len(mates_ele)):
            if mates_ele[i].text.startswith("Projeto Integrador"):
                notas.pop(i)
            else:
                mates.append(mates_ele[i].text)

        # print("Notas parciais obtidas") # Adicionar em caso de testes

        parcial = [{ "tipo": '', "nome": materia, "nota": nota, 'abc': 'D'} for materia, nota in zip(mates, notas)]
        return parcial
    except:
        print("Os elementos com as notas parciais não foram encontrados.")
        return 'Falha parciais' # Em caso desse return, pode haver erros. Arrumar depois (1/2)

def notas_historicas(id: int):
    # Clicar no aba Notas Histórico
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel8Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel8Span").click()
    except:
        print("Botão Histórico não encontrado")

    # Pegar notas históricas
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        
        notas_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        notas = [nota.text for nota in notas_ele]
        mates_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")
        mates = []
        
        for i in range(len(mates_ele)):
            if mates_ele[i].text.startswith("Projeto Integrador"):
                notas.pop(i)
            else:
                mates.append(mates_ele[i].text)

        # print("Notas históricas obtidas") # Adicionar em caso de testes

        historico = [{ "tipo": 'h', "nome": materia, "nota": nota, 'abc': 'D'} for materia, nota in zip(mates, notas)]
        
        return historico
    except:
        # print("Os elementos com as notas parciais não foram encontrados.") # Adicionar em caso de testes
        return 'Falha historicas' # Em caso desse return, pode haver erros. Arrumar depois (2/2)


app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def receber_login():
    print('\n\n\n\ndados recebidos para login')
    dados = request.json 
    u = dados['usuario']
    s = dados['senha']
    # print(dados)  # Adicionar em caso de testes
    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)

    id = ids.geraId()
    # Inserir primeira árvore que possui Driver
    arvore.insere_no(id = id, driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                                options=chrome_options))
    # print('inserido uma nova árvore') # Adicionar em caso de testes
    arvore.encontra(id).obtemDriver().get('https://siga.cps.sp.gov.br/aluno/login.aspx?')

    # print('Árvore') # Adicionar em caso de testes
    # arvore.mostra_EmOrdem() # Adicionar em caso de testes
    # print('Return') # Adicionar em caso de testes
    return login(u, s, id)

@app.route('/api/notas', methods=['POST'])
def scrape_notas():
    print('\n\n\n\nDados recebidos para pegar notas')
    dados = request.json
    # print(dados)  # Adicionar em caso de testes
    id = dados['id']

    notas_a = notas_parciais(id)
    notas_h = notas_historicas(id)

    notas = {
        "parciais": notas_a,
        "historicas": notas_h
    }

    notas = json.dumps(notas, ensure_ascii=False, indent=4)
    # print(notas) # Adicionar em caso de testes
    return notas

if __name__ == '__main__':
    app.run(debug=True)