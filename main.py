import re
from bot import wppbot
import sys


#nome do usuário do whatsapp
nome = 'TesteChat' #grupo para teste
#nome = str(input('Informe o usuário a se conversar: '))

#inicia a classe do bot
bot = wppbot('Alan')
#faz o seu treinamento
#bot.treina()
#inicia uma conversa
bot.inicia(nome)
#escreve uma saudação para o usuário
bot.saudacao(['Olá '+ nome +', sou um assistente de consórcio, tire suas dúvidas comigo'])
ultimo_texto = ''
i = 0
while True:

    #espera receber o texto do usuário
    texto = bot.escuta()

    if texto != None and texto != ultimo_texto and i != 0:
        ultimo_texto = texto
        texto = texto.lower()
        bot.responde(texto)
    if(i == 0):
        ultimo_texto = texto
    i = i + 1
        


    
