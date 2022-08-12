from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import asyncio

# TODO: Possibly optimize this? Maybe using arguments[0] for everything
def ValidationBS(driver, url):
    driver.get(url)
    print("Accepting cookies")
    driver.find_element(By.ID,'onetrust-accept-btn-handler').click()

    print("Choosing dropdowns")
    dropdown1 = Select(driver.find_element(By.ID, 'wpModal-language'))
    dropdown1.select_by_index(0)
    dropdown2 = Select(driver.find_element(By.ID, 'wpModal-gemeTitle'))
    dropdown2.select_by_index(1)
    dropdown3 = Select(driver.find_element(By.ID, 'wpModal-country'))
    dropdown3.select_by_index(0)

    print("Accepting privacy policy")
    driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[2]/div/div[4]/button').click()
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmPrivacyPolicy'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))

    print("Accepting TOS")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmTos'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))

async def getPage(driver, num):
    print("Getting page " + num)
    url = "https://www.bandai-tcg-plus.com/card/" + num
    time.sleep(5)
    driver.get(url)
    WebDriverWait(driver, 1000).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div[2]/div/div[1]/div/div[2]/div[2]/button')))
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
    
    # TODO: Rewrite this whole section. Similar to format above
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
    return digimon

async def main():
    url = "https://www.bandai-tcg-plus.com/card/35750"
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.add_argument('--headless')
    fireFoxOptions.add_argument('--lang=en_US')
    driver = webdriver.Firefox(options=fireFoxOptions)
    driver.implicitly_wait(10)
    ValidationBS(driver, url)
    
    pageNums = [5923, 5928, 5932, 5993, 5995, 6732, 6736, 6767, 20396, 20498, 20570, 20713, 24683, 24901, 25315, 25418, 35715, 35850, 35987, 35991, 36037, 36068, 36133, 36244, 36260, 36283]
    allDigimon = []
    i = 0
    startPage, endPage = 0, 0

    startTime = time.perf_counter()
    while (i < len(pageNums)):
        startPage, endPage = pageNums[i], (pageNums[i + 1] + 1)
        i += 2
        for num in range(startPage, endPage):
            # TODO: Find out if await and WebDriverWait help at all
            allDigimon.append(await getPage(driver, str(num)))
    
    with open("digimon.json", "w") as file:
        print(json.dumps(allDigimon, indent=4), file=file)
        file.close()
    endTime = time.perf_counter()

    # TODO: Fix calculations
    elapsedTime = str(endTime - startTime)
    elapsedPage = str(endPage - startPage)
    print("It took " + elapsedTime + " seconds to run " + elapsedPage + " pages.")
    print("Approximately " + str(float(elapsedTime) / float(elapsedPage)) + " seconds per page.")

    # Range of all pages that have Digimon, with the number of pages in that range
    # 5923, 5928 - 6
    # 5932, 5993 - 62
    # 5995, 6732 - 738
    # 6736, 6767 - 32
    # 20396, 20498 - 103
    # 20570, 20713 - 144
    # 24683, 24901 - 219
    # 25315, 25418 - 104
    # 35715, 35850 - 136
    # 35987, 35991 - 5
    # 36037, 36068 - 32
    # 36133, 36244 - 112
    # 36260, 36283 - 24
    # TOTAL: 1717

if __name__ == "__main__":
    asyncio.run(main())