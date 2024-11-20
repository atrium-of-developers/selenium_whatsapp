import sqlite3
import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from config import *

db_name = "study_bot.db"
user_data_file = "user_profiles.json"
UNREAD_BUTTON_SELECTOR = "//*[@id="side"]//button[contains(., 'Unread')]"
CONTACT_NAME_SELECTOR = '//div[@role="row" and contains(@class, "focusable-list-item")]//span[@title]'
LATEST_MESSAGE_SELECTOR = '//div[contains(@class, "message-in")]//span[contains(@class, "selectable-text")]'

# Utility functions for user data
def load_user_data():
    try:
        with open(user_data_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(user_data_file, "w") as file:
        json.dump(data, file)

# Database functions
def get_menu():
    """Fetch the main menu from the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM topics")
        topics = cursor.fetchall()
        conn.close()
        return "Welcome! Choose a lesson:\n" + "\n".join([f"{topic[0]}. {topic[1]}" for topic in topics])
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "Error retrieving menu. Please try again later."

def get_subtopics(topic_id):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subtopics WHERE topic_id = ?", (topic_id,))
        subtopics = cursor.fetchall()
        conn.close()
        return subtopics
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def get_content(subtopic_id):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, text FROM content WHERE subtopic_id = ?", (subtopic_id,))
        content = cursor.fetchall()
        conn.close()
        return content
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

# Message handling functions
def send_message(user, message):
    try:
        search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
        search_box.click()
        search_box.clear()
        search_box.send_keys(user, Keys.ENTER)

        message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='1']")
        message_box.click()
        message_box.send_keys(message, Keys.ENTER)
    except Exception as e:
        print(f"Error sending message: {e}")
        traceback.print_exc()

def press_unread_button():
    """Press the 'Unread' button to navigate to the unread messages section."""
    try:
        unread_button = driver.find_element(By.XPATH, UNREAD_BUTTON_SELECTOR)
        unread_button.click()
        print("Clicked on 'Unread' button.")
        time.sleep(2)  # Allow time for the section to load
    except NoSuchElementException:
        print("No 'Unread' button found.")


def click_on_unread_and_get_message():
    """Click on the first unread contact and retrieve the last message."""
    try:
        # Identify the unread contact by its XPath (adjust selector based on actual page structure)
        unread_contacts = driver.find_elements(By.XPATH, CONTACT_NAME_SELECTOR)
        if unread_contacts:
            # Click on the first unread contact
            unread_contact = unread_contacts[0]
            unread_contact.click()

            # Wait for the conversation to load
            time.sleep(2)

            # Now retrieve the last message in the conversation
            last_message = driver.find_element(By.XPATH, '//*[@id="main"]/footer//div[@class="_2_1wd copyable-text selectable-text"]')
            return last_message.text.strip()
        else:
            print("No unread contacts found.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
# Main logic to listen and respond
def listen_and_respond():
    user_data = load_user_data()
    admin_number = "+233206814915"  # Replace with the actual admin number
    wait = WebDriverWait(driver, 60)

    while True:
        try:
            print("Navigating to 'Unread' messages...")
            press_unread_button()

            # Get the last sender and message
            sender, last_message = get_sender_and_last_message()
            if not sender or not last_message:
                time.sleep(5)
                continue

            # Handle admin messages
            if sender == admin_number:
                try:
                    data = json.loads(last_message)
                    if isinstance(data, dict):
                        add_data(data)
                        send_message(sender, "Data added successfully!")
                    else:
                        send_message(sender, "Invalid data format. Please send a JSON object.")
                except json.JSONDecodeError as je:
                    print(f"JSON decode error: {je}")
                    send_message(sender, "Error: Invalid JSON format.")
                continue

            # Handle user messages
            if sender not in user_data:
                user_data[sender] = {"topic": None, "subtopic": None, "content_index": 0}
                save_user_data(user_data)
                send_message(sender, get_menu())
                continue

            user_state = user_data[sender]

            if last_message.lower() == "menu":
                user_state.update({"topic": None, "subtopic": None, "content_index": 0})
                save_user_data(user_data)
                send_message(sender, get_menu())
            elif user_state["topic"] is None:
                try:
                    topic_id = int(last_message)
                    subtopics = get_subtopics(topic_id)
                    if subtopics:
                        user_state["topic"] = topic_id
                        save_user_data(user_data)
                        subtopics_menu = "Choose a subtopic:\n" + "\n".join([f"{st[0]}. {st[1]}" for st in subtopics])
                        send_message(sender, subtopics_menu)
                    else:
                        send_message(sender, "Invalid topic. Please try again.")
                except ValueError:
                    send_message(sender, "Please enter a valid topic number.")
            elif user_state["subtopic"] is None:
                try:
                    subtopic_id = int(last_message)
                    content = get_content(subtopic_id)
                    if content:
                        user_state["subtopic"] = subtopic_id
                        user_state["content_index"] = 0
                        save_user_data(user_data)
                        send_message(sender, content[0][1])
                    else:
                        send_message(sender, "Invalid subtopic. Please try again.")
                except ValueError:
                    send_message(sender, "Please enter a valid subtopic number.")
            else:
                content = get_content(user_state["subtopic"])
                if last_message.lower() == "n":
                    if user_state["content_index"] < len(content) - 1:
                        user_state["content_index"] += 1
                        save_user_data(user_data)
                        send_message(sender, content[user_state["content_index"]][1])
                    else:
                        send_message(sender, "You've reached the end of this subtopic.")
                elif last_message.lower() == "b":
                    if user_state["content_index"] > 0:
                        user_state["content_index"] -= 1
                        save_user_data(user_data)
                        send_message(sender, content[user_state["content_index"]][1])
                    else:
                        send_message(sender, "You're at the beginning of this subtopic.")
                else:
                    send_message(sender, "Invalid command. Use 'n' for next, 'b' for back, or 'menu' to return to the main menu.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

# Start listening
listen_and_respond()
