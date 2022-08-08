from selenium import webdriver
driver = webdriver.Firefox(executable_path=r'geckodriver.exe')
driver.get('http://inventwithpython.com')