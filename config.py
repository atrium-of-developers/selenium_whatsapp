
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

admin_number = "+233206814915"
phone_number = "+233509119224"

db_name = "study_bot.db"
user_data_file = "user_profiles.json"

# Set up the WebDriver (use the appropriate driver for your browser, e.g., ChromeDriver)
# Replace with the appropriate WebDriver (e.g., webdriver.Firefox() for Firefox)
driver.get("https://web.whatsapp.com")
# XPath selector for unread chats button
UNREAD_BUTTON_SELECTOR = '//*[@id="side"]/div[2]/button[2]'
CONTACT_NAME_SELECTOR = "//*[@id='pane-side']/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/div/span"

# XPath selector for the latest incoming message content
LATEST_MESSAGE_SELECTOR = '//div[contains(@class, "message-in")]//span[@class="selectable-text"]'
