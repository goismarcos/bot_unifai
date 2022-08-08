import os
import time
import re
import requests
import json
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
from requests_html import HTMLSession
import re
import emoji 

class wppbot:

    dir_path = os.getcwd()

    def __init__(self, nome_bot):
        print(self.dir_path)
        self.bot = ChatBot(nome_bot, storage_adapter='chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///database.sqlite3')
        self.bot.set_trainer(ListTrainer)

        self.chrome = self.dir_path+'\\chromedriver.exe'

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(r"user-data-dir="+self.dir_path+"\profile\wpp")
        self.driver = webdriver.Chrome(self.chrome, chrome_options=self.options)

    def inicia(self,nome_contato):
        #abre o whats web
        self.driver.get('https://web.whatsapp.com/')
        self.driver.implicitly_wait(15)
        #procura pela tag na busca de contatos do whats
        self.caixa_de_pesquisa = self.driver.find_element_by_class_name('_2zCfw')
        self.caixa_de_pesquisa.send_keys(nome_contato)
        time.sleep(1)
        print(nome_contato)
        #entra na conversa do contato _2WP9Q
        self.contato = self.driver.find_element_by_class_name('_2WP9Q')
        self.contato.click()
        time.sleep(1)

    def saudacao(self,frase_inicial):
        #busca a tag de caixa de texto no whats web
        self.caixa_de_mensagem = self.driver.find_element_by_class_name('_13mgZ')

        #escreve a frase de saudação que está na list vinda por parametro
        if type(frase_inicial) == list:
            for frase in frase_inicial:
                frase = emoji.demojize(frase)
                self.caixa_de_mensagem.send_keys(str(frase))
                time.sleep(1)
                self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
                self.botao_enviar.click()
                time.sleep(1)
        else:
            return False

    def escuta(self):
        try:
            post = self.driver.find_elements_by_class_name('message-in')
            ultimo = len(post) - 1
            texto = post[ultimo].find_element_by_css_selector('span.selectable-text').text
            return texto
        except:
            return

    def aprender(self,ultimo_texto,frase_inicial,frase_final,frase_erro):
        self.caixa_de_mensagem = self.driver.find_element_by_class_name('_13mgZ')
        self.caixa_de_mensagem.send_keys(frase_inicial)
        time.sleep(1)
        self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
        self.botao_enviar.click()
        self.x = True
        while self.x == True:
            texto = self.escuta()

            if texto != ultimo_texto and re.match(r'^::', texto):
                if texto.find('?') != -1:
                    ultimo_texto = texto
                    texto = texto.replace('::', '')
                    texto = texto.lower()
                    texto = texto.replace('?', '?*')
                    texto = texto.split('*')
                    novo = []
                    for elemento in texto:
                        elemento = elemento.strip()
                        novo.append(elemento)

                    self.bot.train(novo)
                    self.caixa_de_mensagem.send_keys(frase_final)
                    time.sleep(1)
                    self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
                    self.botao_enviar.click()
                    self.x = False
                    return ultimo_texto
                else:
                    self.caixa_de_mensagem.send_keys(frase_erro)
                    time.sleep(1)
                    self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
                    self.botao_enviar.click()
                    self.x = False
                    return ultimo_texto
            else:
                ultimo_texto = texto

    def noticias(self):
        #busca as noticias em uma api
        req = requests.get('https://newsapi.org/v2/top-headlines?sources=globo&pageSize=5&apiKey=f6fdb7cb0f2a497d92dbe719a29b197f')
        noticias = json.loads(req.text)

        #percorre as noticias
        for news in noticias['articles']:
            titulo = news['title']
            link = news['url']
            new = 'Alan: ' + titulo + ' ' + link + '\n'
            #coloca as noticias na caixa de texto e envia
            self.caixa_de_mensagem.send_keys(new)
            time.sleep(1)
    
    def previsao(self):
        local=''
        #pega a sessao html
        session = HTMLSession()
        #faz a busca no google
        url = 'https://www.google.com.br/search?q=previsao+do+tempo&oq=previsao+do+tempo&ie=UTF-8'
        r = session.get(url)
        #indica a tag a ser buscada para cidade
        selector_city = '#wob_loc'
        city = r.html.find(selector_city, first=True).text
        #indica a tag a ser buscada para clima
        selector_state = '#wob_dc'
        state = r.html.find(selector_state, first=True).text
        #plantando na string
        response = 'Alan: Em '+ city +' está ' + state

        #colocando na caixa de texto 
        self.caixa_de_mensagem = self.driver.find_element_by_class_name('_3u328')
        self.caixa_de_mensagem.send_keys(response)
        time.sleep(1)
        #enviando para o usuário
        self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
        self.botao_enviar.click()

    def naoEntendeu(self, texto):
        texto = texto.replace(' ', '+')
        session = HTMLSession()
        #busca no google a palavra que ele nao entendeu
        url = 'https://www.google.com.br/search?q='+texto+'&oq='+texto+'a&ie=UTF-8'

        #ele irá tenta achar a tag que contém os dados para a busca, caso nao consiga sua execeção será uma busca no google do que foi digitado
        r = session.get(url)
        selector = '.e24Kjd'
        busca = ''
        try:
            busca = r.html.find(selector, first=True).text
        except:
            busca = 'Não consegui entender o que você escreveu, por isso aqui está um link para buscar no meu amigo google \n'+ url

        response = 'Alan: '+ busca
        #preparando retorno, colocando na caixa de texto
        self.caixa_de_mensagem = self.driver.find_element_by_class_name('_3u328')
        self.caixa_de_mensagem.send_keys(response)
        time.sleep(3)
        #enviando para o usuário
        self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
        self.botao_enviar.click()
        
    def responde(self,texto):
        #pega a possivel resposta
        response = self.bot.get_response(texto)
        # verifica se ela é confiavel
        if float(response.confidence) > 0.5:
            response = str(response)
        # se nao chama a funcao de nao entendeu para filtrar melhor o texto
        else:
            response = "Desculpe, não compreendi sua colocação seja mais claro por favor. Obrigado" 
        #caso se ja confiavel
        #prepara a tag de caixa de texto para receber o texto de resposta
        self.caixa_de_mensagem = self.driver.find_element_by_class_name('_13mgZ')
        self.caixa_de_mensagem.send_keys(response)
        time.sleep(1)
        #envia a resposta
        self.botao_enviar = self.driver.find_element_by_class_name('_3M-N-')
        self.botao_enviar.click()

    def treina(self):
        #Busca o arquivo txt que contém conversas e treina com ele
        for arq in os.listdir('arq'):
            conv = open('arq/'+arq , encoding="utf8").readlines()
            self.bot.train(conv)
