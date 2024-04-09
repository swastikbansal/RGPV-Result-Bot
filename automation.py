from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import csv

from PIL import Image
import pytesseract 

import time

def get_captcha(driver, element, path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    location = element.location_once_scrolled_into_view

    size = element.size
    
    driver.save_screenshot(path)
    image = Image.open(path)

    left = location['x'] - 20
    top = location['y']
    right = location['x'] + size['width'] + 20
    bottom = location['y'] + size['height']

    image = image.crop((left, top, right, bottom))  # defines crop points
    image.save(path, 'png')  # saves new cropped image

    captcha = pytesseract.image_to_string(image) 
    captcha = captcha.replace(" ", "").strip()
    print(captcha)
    
    time.sleep(2)

    return captcha

def open_result(roll_no):
        
    #Entering Roll No.
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_txtrollno')))
    roll_no_b = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtrollno')
    roll_no_b.send_keys(roll_no)

    #Selecting Sem
    sem = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_drpSemester')
    drop = Select(sem)
    drop.select_by_visible_text("3") # Change the sem here 
    
    # Entering Captcha
    captcha_input=driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]')
    img = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_pnlCaptcha"]/table/tbody/tr[1]/td/div/img')
    cap = get_captcha(driver, img, "captcha.png")
    captcha_input.clear()
    captcha_input.send_keys(cap.upper())

    # Clicking on Result Button
    result_but = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]')
    result_but.click()
    # pyautogui.click(516,536)

    print('Button Clicked \n')

    try:
        wait = WebDriverWait(driver, 5)
        wait.until(EC.alert_is_present())
        driver.switch_to.alert.accept() 
        return 2

    except:
        try: 
            # time.sleep(2)
            reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]')
            reset.click()
            return 1
        
        except :
            trial = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]').is_displayed()
            if trial:
                result_but = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]')
                result_but.click()
                # time.sleep(3)
                return 0


#__main__
if __name__ == "__main__":
    #Setting up driver
    service = Service()
    options = webdriver.EdgeOptions()
    options.add_argument('--headless') 
    options.add_argument('--enable-chrome-browser-cloud-management')
    driver = webdriver.Edge(service=service, options=options)
    driver.get('http://result.rgpv.ac.in/result/ProgramSelect.aspx')

    program = driver.find_element(By.XPATH,'//*[@id="radlstProgram_1"]')
    program.click()

    file = open("results.csv",'a')
    csvwriter = csv.writer(file)

    for i in range(1066,1082): # Range of Roll No
        roll_number = "0827AL22"+str(i)
        res = open_result(roll_number)
        print(res)
        
        while res == 2:
            res = open_result(roll_number) 
            print(res)

        while (res == 0):
           
            try :
                time.sleep(1)
                try : 
                    ch_reset = reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]').is_displayed()
                    if ch_reset:
                        data = []
                        
                        #Roll No
                        roll_no = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblRollNoGrading"]')
                        roll_no = roll_no.text
                        data.append(roll_no)

                        #Name
                        name = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblNameGrading"]')
                        name = name.text
                        data.append(name)
                        # print(name)
                        
                        #Result
                        result = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblResultNewGrading"]')
                        result = result.text
                        data.append(result)
                        # print(result)
                        
                        #SGPA
                        sgpa = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblSGPA"]')
                        sgpa = sgpa.text
                        data.append(sgpa)
                        # print(sgpa)
                        
                        #CGPA
                        cgpa = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblcgpa"]')
                        cgpa = cgpa.text
                        data.append(cgpa)
                        # print(cgpa)
                        
                        subjects = 5
                        
                        for i in range(2,  subjects+2):
                            subj = driver.find_element(By.XPATH,f'//*[@id="ctl00_ContentPlaceHolder1_pnlGrading"]/table/tbody/tr[3]/td/table[{i}]/tbody/tr/td[4]')
                            subj = subj.text
                            data.append(subj)
                            # print(subj)                      
                        
                        print(data)

                        csvwriter.writerow(data)

                        reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]')
                        reset.click()
                except:
                    res = open_result(roll_number)
                    pass
            except:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.alert_is_present())
                driver.switch_to.alert.accept() 
                res = open_result(roll_number) 
                print(res)

        print(roll_number)

    driver.close()
