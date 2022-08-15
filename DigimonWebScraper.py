from tracemalloc import start
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
# Jumps through the many hoops of accessing the Digimon card list
def ValidationBS(driver, url):
    # Starts by going to page and accepting cookies (security blah blah I know, I will find the object to reject them sometime)
    driver.get(url)
    print("Accepting cookies")
    driver.find_element(By.ID,'onetrust-accept-btn-handler').click()

    # Selects the numerous cumbersome dropdowns that appear next
    print("Choosing dropdowns")
    dropdown1 = Select(driver.find_element(By.ID, 'wpModal-language'))
    dropdown1.select_by_index(0)
    dropdown2 = Select(driver.find_element(By.ID, 'wpModal-gemeTitle'))
    dropdown2.select_by_index(1)
    dropdown3 = Select(driver.find_element(By.ID, 'wpModal-country'))
    dropdown3.select_by_index(0)

    # Accepts Bandai's privacy policy that they make you read on their website for some reason??
    print("Accepting privacy policy")
    driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[2]/div/div[4]/button').click()
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmPrivacyPolicy'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))

    # Why is web TOS a thing - Bandai please I just want to look at cute Veemon alt art
    print("Accepting TOS")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID,'confirmTos'))
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div[3]/button'))

# Gets a single page and puts it into dictionary using Selenium and BS4
async def getPage(driver, num):
    print("Getting page " + num)
    url = "https://www.bandai-tcg-plus.com/card/" + num
    # The only way I've actually been able to get it to fully load each page
    time.sleep(5)
    driver.get(url)
    # This wait probably does nothing
    WebDriverWait(driver, 1000).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/main/div/div[2]/div/div[1]/div/div[2]/div[2]/button')))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Basic card info
    digimon = {}
    digimon["ID"] = num
    cardName = soup.find("p", class_="cardName").text
    digimon["Card Name"] = cardName
    cardNum = soup.find("p", class_="cardNumber").text
    digimon["Card Number"] = cardNum

    # Loops through all info listed in table
    info = soup.find_all("div", {"class": "flexContainer borderDashed"}, limit=20)
    for a in info:
        b = str(a.text).strip().split("\n", 1)
        if len(b) == 1 or b[1] == "\uff0d":
            key, val = b[0], ''
        else: key, val = key, val = b[0], b[1].strip()
        digimon[key] = val
    
    # TODO: Rewrite this whole section. Similar to format above
    # Pull stuff at bottom of page. Very nasty
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
    # Setup for connecting Selenium to website
    url = "https://www.bandai-tcg-plus.com/card/35750"
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.add_argument('--headless')
    fireFoxOptions.add_argument('--lang=en_US')
    driver = webdriver.Firefox(options=fireFoxOptions)
    driver.implicitly_wait(10)
    ValidationBS(driver, url)
    
    # Instantiate main vars and start timer
    pageNums = [5923, 5928, 5932, 5993, 5995, 6732, 6736, 6767, 20396, 20498, 20570, 20713, 24683, 24901, 25315, 25418, 35715, 35850, 35987, 35991, 36037, 36068, 36133, 36244, 36260, 36283]
    allDigimon = []
    i = 0
    totalPages = 0
    startTime = time.perf_counter()

    # Main loop - gets all pages in range listed in pageNums
    while (i < len(pageNums)):
        startPage, endPage = pageNums[i], (pageNums[i + 1] + 1)
        totalPages += endPage - startPage
        i += 2
        for num in range(startPage, endPage):
            # TODO: Find out if await and WebDriverWait help at all
            allDigimon.append(await getPage(driver, str(num)))
    
    # Prints digimon list to JSON file and stops timer
    with open("digimon.json", "w") as file:
        print(json.dumps(allDigimon, indent=4), file=file)
        file.close()
    endTime = time.perf_counter()

    # Time stats and such
    elapsedTime = str(endTime - startTime)
    print("It took " + elapsedTime + " seconds to run " + totalPages + " pages.")
    print("Approximately " + str(float(elapsedTime) / float(totalPages)) + " seconds per page.")

    # Range of all pages that have Digimon, with the number of pages in that range
    # There may be a way to find these automatically, but that seems slow and boring to implement
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
    # The await and async is probably useless tbh
    asyncio.run(main())