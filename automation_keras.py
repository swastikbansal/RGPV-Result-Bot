
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from PIL import Image
import keras_ocr 

import time

pipeline = keras_ocr.pipeline.Pipeline()

def get_captcha(driver, element, path):
    pipeline = keras_ocr.pipeline.Pipeline()
    location = element.location_once_scrolled_into_view

    size = element.size
    
    driver.save_screenshot(path)
    image = Image.open(path)

    left = location['x'] - 20
    top = location['y']
    right = location['x'] + size['width'] + 20
    bottom = location['y'] + size['height']

    image = image.crop((left, top, right, bottom))   
    image.save(path, 'png')  

    images = ['captcha.png']
    prediction_groups = pipeline.recognize(images)

    predicted_image_1 = prediction_groups[0]

    captcha = ''

    for text, box in predicted_image_1:
        captcha+=text
    
    captcha = captcha.replace(" ", "").strip()
    captcha = captcha.upper()
    
    print(captcha)

    return captcha


service = Service()
options = webdriver.EdgeOptions()
# options.add_argument('--headless')
driver = webdriver.Edge(service=service, options=options)
driver.get('http://result.rgpv.ac.in/result/ProgramSelect.aspx')

program = driver.find_element(By.XPATH,'//*[@id="radlstProgram_1"]')
program.click()

def open_result(roll_no):

    #Entering Roll No.
    roll_no_b = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtrollno')
    roll_no_b.send_keys(roll_no)

    #Selecting Sem
    sem = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_drpSemester')
    drop = Select(sem)
    drop.select_by_visible_text("2")

    
    captcha_input=driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]')
    img = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_pnlCaptcha"]/table/tbody/tr[1]/td/div/img')
    cap = get_captcha(driver, img, "captcha.png")

    captcha_input.send_keys(cap.upper())

    result_but = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]')
    result_but.click()

    time.sleep(2)

    alert = driver.switch_to.alert

    # Get text from the alert and print it
    alert_text = alert.text
    print("Alert Text:", alert_text)

    # Accept the alert (click "OK")
    alert.accept()

    time.sleep(3)
        
    reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]')
    reset.click()



for i in range(1135,1137):
    roll_number = "0827AL22"+str(i)
    open_result(roll_number)


time.sleep(250)
