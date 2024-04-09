from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

print(time.localtime())
file = open('test.txt','w')

#specify where your chrome driver present in your pc
service = Service()
options = webdriver.EdgeOptions()
# options.add_argument('--headless')
driver = webdriver.Edge(service=service, options=options)

#provide website url here
driver.get("https://www.google.co.in/")


#get button and click on it to get alert
entry = driver.find_element(By.XPATH,'//*[@id="searchInput"]')
entry.send_keys("Möbius strip")
entry.send_keys(Keys.ENTER)

text = driver.find_element(By.XPATH,'//*[@id="mw-content-text"]/div[1]/p[3]')
file.write(text.text)


#sleep for a second
time.sleep(10)

