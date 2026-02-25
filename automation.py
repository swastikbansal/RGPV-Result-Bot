from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import csv
from tqdm import tqdm
from PIL import Image
import pytesseract 
import time
import re

# Bugs
# Random 0 being added at the end of roll no.

# 89, 91 , 92, 95 , 109 , 118, 136, 145, 149, 152

# Hyperparameters
selected_sem = "7"
subjects = 3
roll_no_range = range(1080,1158)

def get_captcha(driver, element, path):
    try:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    except:
        print("Tesseract OCR not found. Please install it and set the path correctly.")
        return None
    
    location = element.location_once_scrolled_into_view
    size = element.size
    
    driver.save_screenshot(path)
    image = Image.open(path)

    left = max(location['x'] - 20, 0)
    top = location['y']
    right = location['x'] + size['width'] + 20
    bottom = location['y'] + size['height']

    image = image.crop((left, top, right, bottom))
    image.save(path, 'png')

    captcha = pytesseract.image_to_string(image)
    # Normalize OCR noise: keep alphanumerics and fix common confusions
    captcha = re.sub(r'[^A-Za-z0-9]', '', captcha).upper().replace('O', '0').replace('I', '1').strip()
    return captcha

def open_result(driver, roll_no):
    #Entering Roll No.
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_txtrollno')))
    roll_no_b = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtrollno')
    roll_no_b.send_keys(roll_no)

    #Selecting Sem
    sem = driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_drpSemester')
    drop = Select(sem)
    drop.select_by_visible_text(selected_sem)
    
    # Entering Captcha
    captcha_input=driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]')
    img = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_pnlCaptcha"]/table/tbody/tr[1]/td/div/img')
    cap = get_captcha(driver, img, "captcha.png")
    captcha_input.clear()
    captcha_input.send_keys(cap)

    # Clicking on Result Button
    result_but = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]')
    result_but.click()

    #2 - Invalid Captcha
    #1 - Page doesn't respond for some reason
    #0 - Result Opened
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(EC.alert_is_present())
        driver.switch_to.alert.accept() 
        return 2
    except TimeoutException:
        try:
            reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]')
            reset.click()
            return 1
        except:
            trial = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]').is_displayed()
            if trial:
                result_but = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]')
                result_but.click()
                return 0

#__main__
if __name__ == "__main__":
    #Setting up driver
    service = Service()
    options = webdriver.EdgeOptions()
    options.add_argument('--headless') 
    options.add_argument('--enable-chrome-browser-cloud-management')
    
    # Suppress Chromium USB and verbose logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    
    try:    
        driver = webdriver.Edge(service=service, options=options)
    except:
        print("Edge WebDriver not found. Please install it and set the path correctly.")
        exit(1)
    driver.get('http://result.rgpv.ac.in/result/ProgramSelect.aspx')

    program = driver.find_element(By.XPATH,'//*[@id="radlstProgram_1"]')
    program.click()

    file = open("results.csv",'a',newline='', encoding='utf-8')
    file_data = set(tuple(i) for i in csv.reader(open("results.csv","r", encoding='utf-8')))  # faster duplicate checks
    csvwriter = csv.writer(file)

    for i in tqdm(roll_no_range):
        roll_number = f"0827AL22{i}"
        
        # if roll_number in ["0827AL22089", "0827AL22091", "0827AL22092", "0827AL22094", "0827AL22136"]:
        #     continue
        
        res = open_result(driver, roll_number)
        
        while res == 2:
            res = open_result(driver, roll_number) 

        # Retrieving data if everything is fine
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
                        
                        #Result
                        result = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblResultNewGrading"]')
                        result = result.text
                        data.append(result)
                        
                        #SGPA
                        sgpa = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblSGPA"]')
                        sgpa = sgpa.text
                        data.append(sgpa)
                        
                        #CGPA
                        cgpa = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_lblcgpa"]')
                        cgpa = cgpa.text
                        data.append(cgpa)

                        # Adding grade for n subject                        
                        for i in range(2,  subjects+2):
                            subj = driver.find_element(By.XPATH,f'//*[@id="ctl00_ContentPlaceHolder1_pnlGrading"]/table/tbody/tr[3]/td/table[{i}]/tbody/tr/td[4]')
                            subj = subj.text
                            data.append(subj)
                                                
                        # Preventing duplicate entries
                        if tuple(data) not in file_data:
                            print(data)
                            file_data.add(tuple(data))
                            csvwriter.writerow(data)
                            continue

                        reset = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_btnReset"]')
                        reset.click()
                except:
                    res = open_result(driver, roll_number)
                    
            except:
                alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert.accept()
                res = open_result(driver, roll_number) 
                print(res)

    driver.quit()
