
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

options = Options() 
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
# Create WebDriver instance
driver = webdriver.Chrome(options=options)

# Set up the WebDriver (use the appropriate driver for your browser, e.g., ChromeDriver)
# Replace with the appropriate WebDriver (e.g., webdriver.Firefox() for Firefox)
driver.get("https://web.whatsapp.com")
# XPath selector for unread chats button
UNREAD_CHATS_SELECTOR = './/div[contains(text(), "Unread")]'

# XPath selector for the contact name or phone number in the header
CONTACT_NAME_SELECTOR = '//header//span[@title]'

# XPath selector for the latest incoming message content
LATEST_MESSAGE_SELECTOR = '//div[contains(@class, "message-in")]//span[@class="selectable-text"]'
