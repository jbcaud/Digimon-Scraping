# Digimon-Scraping

This is a basic web scraper built in Python that was made to pull information about all cards in the Digimon TCG from Bandai's official website and format them to a JSON file. 

## Description

This was made because I have not been able to find a full set of all cards online yet. It is built using Selenium and BeautifulSoup4. There is also a copy of the full JSON file included in case you just want the data without having to use the script.

## Getting Started

### Dependencies

Currently, this only uses the external libraries Selenium and BS4. Note that in order for Selenium to work, you must install the browser drivers, such as GeckoDriver for Firefox and ChromeDriver for Chrome. Note that this was built using Python 3.10 and may require this version of Python to work properly.

### Executing the program

Using this should be very simple, given you have installed Python and the necessary libraries. Just download "DigimonWebScraper.py", and in a commandline environment, use the command:
```
python DigimonWebScraper.py
```

If you want to edit what pages or cards are pulled, just change the numbers in the pageNums array. Any even index will be the start page, and any odd index will be the end page.

## Acknowledgments

All cards and information pulled using this program is the intellectual property of Bandai Namco. I do not claim to own any of the information on their website.
