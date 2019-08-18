from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class InstagramBot():
  
  #CONSTRUTOR
  def __init__(self, email, password):

    #WEBDRIVER
    self.browser = webdriver.Chrome('chromedriver.exe')
    self.email = email
    self.password = password

    #LIMITES E INTERVALOS
    self.parar = False                        #FUTURAMENTE PARA BOTÃO QUE PARA INTERAÇÃO
    self.limiteDiario = 200                   #LIMITE DE SEGUIR E PARAR DE SEGUIR POR DIA
    self.seguirPorHora = 30                   #LIMITE DE SEGUIR E PARAR DE SEGUIR POR HORA
    self.intervalo = 60*60/self.seguirPorHora #INTERVALO ENTRE SEGUIR UMA PESSOA E OUTRA

    #HASHTAGS
    self.seguirPorHashtag = 25                #LIMITE DE SEGUIR POR CADA HASHTAG
    self.curtirPorHashtag = 0                 #LIMITE DE CURTIDAS POR CADA HASHTAG
    self.comentarPorHashtag = 0           #LIMITE DE COMENTARIOS POR HASHTAG
    self.comentarios = []

    self.hashtags = []                        #LISTA DE HASHTAGS PARA SEGUIR

#FUNÇÕES UTIL===============================================
  #ESPERA ELEMENTO FICAR VISIVEL
  def checkaElemento (self, css, varios=False):
    wait = WebDriverWait(self.browser, 10)

    try:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
      if varios == True:
        return self.browser.find_elements_by_css_selector(css)
      else:
        return self.browser.find_element_by_css_selector(css)

    except:
      return False

  #IMPEDE QUE APARECE SUGESTÃO DE SEGUIDORES
  def tiraSugestao (self):
    self.checkaElemento('div[role="dialog"] .isgrP')
    self.browser.execute_script('''
    var fDialog = document.querySelector('div[role="dialog"] .isgrP');
    fDialog.scrollTop = fDialog.scrollHeight/5
    ''')
    time.sleep(2)
    self.browser.execute_script('''
    var fDialog = document.querySelector('div[role="dialog"] .isgrP');
    fDialog.scrollTop = -fDialog.scrollHeight
    ''')

  #DA SCROLL CAIXA QUE VOCÊ PASSAR POR CSS, TENDO COMO PADRÃO A DO INSTAGRAM
  def scroll (self, css='div[role="dialog"] .isgrP'):
    self.browser.execute_script(f'''
      var fDialog = document.querySelector('{css}');
      fDialog.scrollTop = fDialog.scrollHeight
      ''')

  #CONFERE SE AÇÃO FOI BLOQUEADA (CASO FOI ESPERA 12H E CONTINUA)
  def acaoBloqueada(self):
    bloqueada = self.checkaElemento('body > div > div > div > div > h3')
    if bloqueada != False:
      print('Ação bloqueada, esperar 12h até recontinuar')
      time.sleep(12*60*60)
      self.checkaElemento('body > div > div > div > div > button').click()
      return True
    else:
      return False

  #TRANSFORMA LISTA DE ELEMENTO EM LISTA DE STRINGS
  def elementoString (self, lista):
    result = []
    for item in lista:
      result.append(item.text)

    return result
#===========================================================

  #LOGA
  def login(self):
    #ACESSA O BOWSER
    self.browser.get('https://www.instagram.com/accounts/login/')

    #ACESSA OS CAMPOS DE LOGIN
    emailInput = self.checkaElemento('form input', True)[0]
    passwordInput = self.checkaElemento('form input', True)[1]

    #INSERE OS DADOS
    emailInput.send_keys(self.email)
    passwordInput.send_keys(self.password)

    #ENVIA O FORM
    passwordInput.send_keys(Keys.ENTER)


    #CASO CHAVE NECESSÁRIA 
    if self.checkaElemento('form span button') != False:
      self.checkaElemento('form span button').click()
      chave = self.checkaElemento('form input')
      chave.send_keys(input('Chave segurança Email/Celular: '))
      chave.send_keys(Keys.ENTER)
    else:
      print('Não Precisa de Chave')
    
    #BOTÃO NAO ATIVAR NOTIFICAÇÕES
    try:
      self.checkaElemento('body > div > div > div > div > button:nth-child(2)').click()
    except:
      print('Botão não encontrado')
    
  #FECHA WEBDRIVE
  def encerra (self):
    print('ENCERROU!')
    self.browser.quit()        
  
  #SEGUE POR SEGUIDORES
  def seguirSeguidores (self, username):
    #ACESSA USUARIO
    self.browser.get(f'https://www.instagram.com/{username}/')

    #CLICA EM SEGUIDORES
    seguir = self.checkaElemento('div > header > section > ul > li:nth-child(2) > a')
    seguir.click()

    #IMPEDE QUE APARECE SUGESTÃO DE SEGUIDORES
    self.tiraSugestao()

    #LISTA INICIAL DE SEGUIDORES
    seguidores_seguir = []

    #SEGUE SEGUIDORES
    pos = 0
    seguil = 0
    while len(seguidores_seguir) >= pos and seguil < self.limiteDiario and self.parar == False:
      
      #PEGA VARIOS PARA IR SEGUINDO
      while len(seguidores_seguir) < self.limiteDiario:
        self.scroll()
        time.sleep(0.3)

        #TIRA PESSOAS QUE JÁ SEGUIMOS
        for i in self.checkaElemento('body > div > div > div > ul > div > li > div > div > button', True):
          if i.text == 'Seguir' and i not in seguidores_seguir:
            seguidores_seguir.append(i)
      
      try:
        #SEGUE UM POR UM
        seguidores_seguir[pos].location_once_scrolled_into_view
        seguidores_seguir[pos].click()
        seguil += 1
        print(f'Seguil: {seguil}')

        time.sleep(self.intervalo)

        print(f'len_seguidores = {len(seguidores_seguir)}')
        if pos < len(seguidores_seguir):
          pos += 1
          print(f'pos = {pos}')
      except:
        self.acaoBloqueada()

  #SEGUE POR HASHTAGS
  def seguirHashtag (self):
    seguil = 0
    for hash in self.hashtags:
      #ACESSA A TAG
      self.browser.get(f'https://www.instagram.com/explore/tags/{hash}/')

      #PEGA A PRIMEIRA IMAGEN DA HASHTAG
      self.checkaElemento('article > div > div > div > div:nth-child(1) > div:nth-child(1) a').click()
      
      seguilHash = 0
      #ENQUANTO NÃO CHEGA NO LIMITE DIARIO
      while seguil < self.limiteDiario and self.parar == False and seguilHash < self.seguirPorHashtag:
        
        botao = self.checkaElemento('article div > div > div > button')
        #CASO O POST SEJA SEU
        if botao == False:
          self.browser.find_element_by_link_text('Próximo').click()
          continue

        if botao.text == 'Seguir':
          botao.click()

          #CONFERE SE AÇÃO NÃO FOI BLOQUEADA
          if self.acaoBloqueada() == False:
            seguilHash += 1
            seguil += 1
            print(f'Seguil {seguil}')
            time.sleep(self.intervalo)
        


        #CASO CHEGOU NO ULTIMO POST DA HASTAG
        try:
          self.browser.find_element_by_link_text('Próximo').click()
        except:
          break
      
  #PARAR DE SEGUIR QUEM NÃO TE SEGUE
  def paraDeSeguir (self):
    #ACESSA SEU PERFIL
    self.browser.get(f'https://www.instagram.com/{self.email}')

    #PRIMEIRO CRIAMOS UMA LISTA COM NOSSOS SEGUIDORES
    #SEGUIDORES
    self.checkaElemento('div > header > section > ul > li:nth-child(2) > a').click()

    self.tiraSugestao()

    while True:
      #PEGA PESSOAS QUE VC SEGUE
      seguidores = self.checkaElemento('body > div > div > div > ul > div > li > div > div > div > div > a', True)

      #DA SCROLL
      self.scroll()

      time.sleep(0.5)

      #CASO TENHO PEGO TODOS AS PESSOAS QUE TE SEGUEM FINALIZA WHILE
      if len(self.checkaElemento('body > div > div > div > ul > div > li', True)) == len(seguidores):
        break

    seguidores = self.elementoString(seguidores)

    #FECHA JANELA
    self.checkaElemento('body > div > div > div:nth-child(1) > div > div:nth-child(3) > button').click()

    
    #==================================================================================

    #SEGUINDO
    self.checkaElemento('div > header > section > ul > li:nth-child(3) > a').click()

    self.tiraSugestao()

    parouDeSeguir = 0
    pos = 0
    pegouTodos = False

    #VAI NAS PESSOAS QUE SEGUIMOS E VEMOS SE ELAS NOS SEGUEM
    while self.limiteDiario > parouDeSeguir and not self.parar:
      
      #PEGA TODOS QUE ESTA SEGUINDO
      while not pegouTodos:
            
        seguindo = self.checkaElemento('body > div > div > div > ul > div > li', True)

        self.scroll()

        time.sleep(0.5)

        if len(seguindo) == len(self.checkaElemento('body > div > div > div > ul > div > li', True)):
          pegouTodos = True

      #CASO TENHO PEGO TODOS AS PESSOAS QUE VC SEGUE FINALIZA WHILE
      print(f'len-seguindo = {len(seguindo)}')
      if pos >= len(seguindo):
        break

      #SE NÃO ME SEGUE PARA DE SEGUIR
      if seguindo[pos].find_element_by_css_selector('div > div > div > div> a').text not in seguidores:
        print(seguindo[pos].find_element_by_css_selector('div > div > div > div> a').text)
        try:

          #VAI ATE O ELEMENTO E RETORNA CORDENADAS
          cords = seguindo[pos].location_once_scrolled_into_view
          print(f'teste vai ate o elemento = {cords}')

          #CLICA EM PARAR DE SEGUIR
          seguindo[pos].find_element_by_css_selector('button').click()
          #CONFIRMA
          self.checkaElemento('body > div:nth-child(20) > div > div > div > button').click()
          parouDeSeguir += 1

          print(f'Parou de seguir = {parouDeSeguir}')
          time.sleep(self.intervalo)

        except:
          print('exeção')
          self.acaoBloqueada()

      if pos < len(seguindo):
        pos += 1

      print(f'pos = {pos}')

      
      
