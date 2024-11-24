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
from add_data import *
db_name = "study_bot.db"
user_data_file = "user_profiles.json"

UNREAD_BUTTON_SELECTOR = '//*[@id="side"]/div[2]/button[2]'
CONTACT_NAME_SELECTOR = "//*[@id='pane-side']/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/div/span"

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
        cursor.execute("SELECT id, content FROM content WHERE subtopic_id = ?", (subtopic_id,))
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

        message_box = driver.find_element(By.XPATH, "//*[@aria-placeholder='Type a message']")
        message_box.click()  # Focus on the message box

# Split the message into lines for multi-line support
        for line in message.split('\n'):
            message_box.send_keys(line)  # Type the current line
            message_box.send_keys(Keys.SHIFT, Keys.ENTER)  # Add a newline (without sending)

# Send the entire message by pressing Enter
        
        message_box.send_keys(Keys.ENTER)

# Close the chat box with ESCAPE if needed
        message_box.send_keys(Keys.ESCAPE)
        time.sleep(0.4)
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

def get_sender_and_last_message():
    """Click on the first unread contact and retrieve the last message."""
    try:
        # Identify the unread contact by its XPath (adjust selector based on actual page structure)
        unread_contacts = driver.find_elements(By.XPATH, CONTACT_NAME_SELECTOR)
        if unread_contacts:
            # Click on the first unread contact
            unread_contact = unread_contacts[-1]
            unread_contact.click()

            # Wait for the conversation to load
            
            cont = unread_contact.get_attribute('title').strip()
            # Now retrieve the last message in the conversation
            time.sleep(1)
            buttons = driver.find_elements(By.CLASS_NAME, "read-more-button")
            if buttons:
                buttons[-1].click()
            messages = driver.find_elements(By.XPATH, "//*[@id='main']//div[contains(@class, '_amk4')]/div[contains(@class, '_amk6')]//div[contains(@class, '_akbu')]/span[contains(@class, 'selectable-text')]")

            parent_element = messages[-1]
            span_elements = parent_element.find_elements(By.TAG_NAME, "span")
            last_message = ''.join([span.text for span in span_elements	]) 
            #message_elements = driver.find_elements(By.XPATH, "//*[@data-pre-plain-text]")
            #for element in message_elements:
            #    print(element.get_attribute("data-pre-plain-text"))

            return unread_contact.get_attribute('title').strip(), last_message.strip()

        else:
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None

#Unnecessary
def click_unread_button():
    """Click the 'Unread' button if it's not already active."""
    try:
        # Locate the 'Unread' button by its XPath (you can adjust this based on your needs)
        unread_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, UNREAD_BUTTON_SELECTOR))
        )

        # Check the status of the button (e.g., using 'aria-pressed' attribute or other indicators)
        # Assuming the button has the attribute 'aria-pressed' that is 'true' when active.
        is_clicked = unread_button.get_attribute('aria-pressed')

        # If 'aria-pressed' is not 'true' (meaning the button is not clicked/active), click the button again
        if is_clicked != 'true':
            unread_button.click()
            print("Unread button clicked again!")
        else:
            print("Unread button is already clicked, no action needed.")

    except NoSuchElementException:
        print("Unread button not found!")
    except Exception as e:
        print(f"An error occurred: {e}")

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
                time.sleep(1)
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

            elif last_message.lower().startswith("topic"):
                try:
                    topic_id = int(last_message.split(" ")[1])
                    subtopics = get_subtopics(topic_id)
                    if subtopics:
                        user_state.update({"topic": topic_id, "subtopic": None, "content_index": 0})
                        save_user_data(user_data)
                        subtopics_menu = "Choose a subtopic:\n" + "\n".join([f"{st[0]}. {st[1]}" for st in subtopics])
                        send_message(sender, subtopics_menu)
                    else:
                        send_message(sender, "Invalid topic. Please try again.")
                except (ValueError, IndexError):
                    send_message(sender, "Please specify a valid topic number. For example: 'topic 1'.")

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
                        # Move to the next subtopic if available
                        subtopics = get_subtopics(user_state["topic"])
                        current_subtopic_ids = [st[0] for st in subtopics]
                        next_index = current_subtopic_ids.index(user_state["subtopic"]) + 1
                        if next_index < len(current_subtopic_ids):
                            user_state["subtopic"] = current_subtopic_ids[next_index]
                            user_state["content_index"] = 0
                            save_user_data(user_data)
                            new_content = get_content(user_state["subtopic"])
                            send_message(sender, new_content[0][1])
                        else:
                            send_message(sender, "You've reached the end of this topic.")

                elif last_message.lower() == "b":
                    if user_state["content_index"] > 0:
                        user_state["content_index"] -= 1
                        save_user_data(user_data)
                        send_message(sender, content[user_state["content_index"]][1])
                    else:
                        # Move to the previous subtopic if available
                        subtopics = get_subtopics(user_state["topic"])
                        current_subtopic_ids = [st[0] for st in subtopics]
                        prev_index = current_subtopic_ids.index(user_state["subtopic"]) - 1
                        if prev_index >= 0:
                            user_state["subtopic"] = current_subtopic_ids[prev_index]
                            user_state["content_index"] = 0
                            save_user_data(user_data)
                            new_content = get_content(user_state["subtopic"])
                            send_message(sender, new_content[0][1])
                        else:
                            send_message(sender, "You're at the beginning of this topic.")

                elif last_message.lower() == "next":
                    # Move to the next topic
                    topics = get_menu()
                    current_topic_ids = [int(line.split(".")[0]) for line in topics.splitlines()[1:]]
                    next_topic_id = current_topic_ids.index(user_state["topic"]) + 1
                    if next_topic_id < len(current_topic_ids):
                        user_state.update({"topic": current_topic_ids[next_topic_id], "subtopic": None, "content_index": 0})
                        save_user_data(user_data)
                        send_message(sender, get_subtopics(current_topic_ids[next_topic_id]))
                    else:
                        send_message(sender, "You're at the last topic.")

                elif last_message.lower() == "back":
                    # Move to the previous topic
                    topics = get_menu()
                    current_topic_ids = [int(line.split(".")[0]) for line in topics.splitlines()[1:]]
                    prev_topic_id = current_topic_ids.index(user_state["topic"]) - 1
                    if prev_topic_id >= 0:
                        user_state.update({"topic": current_topic_ids[prev_topic_id], "subtopic": None, "content_index": 0})
                        save_user_data(user_data)
                        send_message(sender, get_subtopics(current_topic_ids[prev_topic_id]))
                    else:
                        send_message(sender, "You're at the first topic.")

                else:
                    send_message(sender, "Invalid command. Use 'n' for next, 'b' for back, 'next' for the next topic, 'back' for the previous topic, or 'menu' to return to the main menu.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()
                        
# Start listening
press_unread_button()
listen_and_respond()
