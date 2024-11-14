from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import asyncio

options = Options()
options.add_argument("--headless")
# Set up the WebDriver (use the appropriate driver for your browser, e.g., ChromeDriver)
driver = webdriver.Chrome(options=options)  # Replace with the appropriate WebDriver (e.g., webdriver.Firefox() for Firefox)
driver.get("https://web.whatsapp.com")
