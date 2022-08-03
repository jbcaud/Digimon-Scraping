from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import json

def ValidationBS(driver, url):
    driver.get(url)
    print("Accepting cookies")
    driver.find_element(By.ID,'onetrust-accept-btn-handler').click()
    print("Choosing dropdowns")
    dropdown1 = Select(driver.find_element(By.ID, 'wpModal-language'))
    dropdown1.select_by_index(0)
    dropdown1 = Select(driver.find_element(By.ID, 'wpModal-gemeTitle'))
    dropdown1.select_by_index(1)
    dropdown1 = Select(driver.find_element(By.ID, 'wpModal-country'))
    dropdown1.select_by_index(0)
    print("Accepting privacy policy")
    driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[2]/div/div[4]/button').click()
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmPrivacyPolicy'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))
    print("Accepting TOS")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmTos'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))

if __name__ == "__main__":
    num = "35750"
    url = "https://www.bandai-tcg-plus.com/card/" + num
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.add_argument('-headless')
    driver = webdriver.Firefox(options=fireFoxOptions)
    driver.implicitly_wait(10)
    ValidationBS(driver, url)
    print("Getting page")
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    digimon = {}
    digimon["ID"] = num
    cardName = soup.find("p", class_="cardName").text
    digimon["Card Name"] = cardName
    cardNum = soup.find("p", class_="cardNumber").text
    digimon["Card Number"] = cardNum

    info = soup.find_all("div", {"class": "flexContainer borderDashed"}, limit=20)
    for a in info:
        b = str(a.text).strip().split("\n", 1)
        if len(b) == 1 or b[1] == "\uff0d":
            key, val = b[0], ''
        else: key, val = key, val = b[0], b[1].strip()
        digimon[key] = val
    
    regulations = soup.find("dl", class_="detalistFlat").text
    footer = regulations.strip().split("\n")
    digimon["Legal Regulations"] = []
    digimon["Card Set(s)"] = []
    i = 1
    while footer[i].strip() != "Card Set(s)":
        if len(footer[i].strip()) != 0:
            digimon["Legal Regulations"].append(footer[i].strip())
        i += 1
    i += 1
    while (i < len(footer)):
        if len(footer[i].strip()) != 0:
            digimon["Card Set(s)"].append(footer[i].strip())
        i += 1
    
    json_object = json.dumps(digimon, indent=4)
    print(json_object)