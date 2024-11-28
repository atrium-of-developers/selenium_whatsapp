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

def send_batch_overview():
    """
    Sends an overview of available batches to the user.
    """
    batch_overview = (
        "Welcome programmer! %0aDo Join the Club for indepth learning and collab https://chat.whatsapp.com/F53Wm8JNpskGQrU0Wpk6fr %0a"
        "Choose matching roman numeral to view its topics:%0a"
        "i.)   1-25 Entry Level%0a"
        "ii.)  26-48 Mid Level%0a"
        "iii.) 49-59 Web with Flask1%0a"
        "iv.)  60-73 Basic API%0a"
        "v.)   74-86 Flask2%0a"
        "vi.)  87-102 Flask Final%0a"
        "vii.) 103-119 Web Top Up%0a"
    )
    return batch_overview


def send_menu_for_batch(sender, batch_id):
    """
    Sends topics for a specific batch to the user based on the batch identifier.
    """
    menu_batches = {
        "i": (1, 25, "1-25 Entry Level"),
        "ii": (26, 48, "26-48 Mid Level"),
        "iii": (49, 59, "49-59 Web with Flask1"),
        "iv": (60, 73, "60-73 Basic API"),
        "v": (74, 86, "74-86 Flask2"),
        "vi": (87, 102, "87-102 Flask Final"),
        "vii": (103, 119, "103-119 Web Top Up"),
    }

    if batch_id not in menu_batches:
        send_message(sender, "Invalid batch identifier. Please choose a valid batch (i-vii).")
        return

    start_id, end_id, batch_name = menu_batches[batch_id]

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        # Fetch topics for the selected batch
        cursor.execute(
            "SELECT id, name FROM topics WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id),
        )
        topics = cursor.fetchall()

        if topics:
            topics_message = (
                f"Topics in {batch_name}:%0a"
                + "%0a".join([f"({topic_id}) {topic_name}" for topic_id, topic_name in topics])
            )
            send_message(sender, topics_message)
        else:
            send_message(sender, f"No topics found in {batch_name}.")
    except sqlite3.Error as e:
        print(f"Database error while fetching batch topics: {e}")
        send_message(sender, "Error retrieving topics for this batch. Please try again later.")
    finally:
        conn.close()


# Database functions
def get_menu():
    """Fetch the main menu from the database using dynamic row numbering."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Use ROW_NUMBER to dynamically generate menu order
        cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY id) AS row_num, name 
            FROM topics
        """)
        topics = cursor.fetchall()
        conn.close()

        # Format the menu output
        if topics:
            menu = "Welcome programmer! %0aPlease Join https://chat.whatsapp.com/F53Wm8JNpskGQrU0Wpk6fr if you haven't yet%0a Choose a lesson:%0a" + "%0a".join(
                [f"({topic[0]}.) {topic[1]}" for topic in topics]
            )
        else:
            menu = "No topics available. Please check back later."

        return menu
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "Error retrieving menu. Please try again later."


def get_subtopics(topic_id):
    """Fetch subtopics for a specific topic, dynamically numbering them."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Use ROW_NUMBER to dynamically generate subtopic numbering within the topic
        cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY id) AS row_num, name
            FROM subtopics
            WHERE topic_id = ?
        """, (topic_id,))
        subtopics = cursor.fetchall()
        conn.close()

        # If subtopics exist, return them with numbering
        if subtopics:
            return [(subtopic[0], subtopic[1]) for subtopic in subtopics]
        else:
            return []

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_content(subtopic_id):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM content WHERE subtopic_id = ?", (subtopic_id,))
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
        for line in message.split('%0a'):
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

def reset_user_state(user_state):
    """
    Resets the user's state to its initial condition.

    :param user_state: The user's current state dictionary.
    """
    user_state.update({"topic": None, "subtopic": None, "content_index": 0})


def get_sender_and_last_message():
    """Click on the first unread contact and retrieve the last message."""
    try:
        # Identify the unread contact by its XPath (adjust selector based on actual page structure)
        wait_message = WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, CONTACT_NAME_SELECTOR)))
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
            messages = driver.find_elements(By.XPATH, LATEST_MESSAGE_SELECTOR)

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
    """
    Main logic to listen to user inputs and respond appropriately.
    Handles navigation through topics, subtopics, and content.
    """
    user_data = load_user_data()
    wait = WebDriverWait(driver, 60)

    while True:
        try:

            # Get the last sender and message
           # wait_message = WebDriverWait(driver, 1200).until(EC.presence_of_element_located((By.XPATH, CONTACT_NAME_SELECTOR)))
            sender, last_message = get_sender_and_last_message()
            if not sender or not last_message:
                time.sleep(5)
                continue

            # Admin Message Handling
            if sender == admin_number:
                handle_admin_message(sender, last_message)
                continue

            # Initialize user state if new user
            if sender not in user_data:
                user_data[sender] = {"topic": None, "subtopic": None, "content_index": 0}
                save_user_data(user_data)
                send_message(sender, send_batch_overview())
                continue

            # Process user message
            process_user_message(sender, last_message, user_data)
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

def process_user_message(sender, message, user_data):
    """
    Processes user messages and manages navigation through the topics and content.
	    """
    user_state = user_data[sender]

    if message.lower() == "menu":
        reset_user_state(user_state)
        send_message(sender, send_batch_overview())
    elif message.lower() == "info":
        send_message(sender, get_info_message())
    elif message.lower() in ['i','ii','iii','iv','v','vi','vii']:
        reset_user_state(user_state)
        send_menu_for_batch(sender, message.lower())
        reset_user_state(user_state)
    elif user_state["topic"] is None:
        handle_topic_selection(sender, message, user_state)
    elif user_state["subtopic"] is None:
        handle_subtopic_selection(sender, message, user_state)
    elif message.lower().startswith("topic"):
        handle_topic_selection(sender, message, user_state)
    else:
        handle_content_navigation(sender, message, user_state)

def get_info_message():
    """
    Returns a string detailing all available commands.
    """
    return (
        "Here's what you can do %0a"
        "- 'menu': Go back to the main menu.%0a"
        "- 'topic <<number>>' eg. topic 5 moves straight the fifth topic%0a"
        "- 'n': Move to the next piece of content (or next topic/subtopic).%0a"
        "- 'b': Move to the previous piece of content (or previous topic/subtopic).%0a"
        "- 'next': Jump to the next subtopic.%0a"
        "- 'back': Jump to the previous subtopic.%0a"
        "- 'info': Show this help message.%0a%0a"
        "Explore and enjoy learning"
    )

def handle_topic_selection(sender, message, user_state):
    """
    Handles the "topic {number}" command to navigate to a specific topic and present its subtopics.

    :param sender: The sender's identifier (e.g., phone number).
    :param message: The message text received from the sender.
    :param user_state: The user's current state as a dictionary.
    """
    try:
        # Extract the topic number from the message
        if message.lower().startswith("topic"):
            topic_parts = message.split()
            if len(topic_parts) < 2:
                send_message(sender, "Please specify a topic number. For example: 'topic 1'.")
                return

            topic_id = int(topic_parts[1])  # Extract the topic ID from the message
            subtopics = get_subtopics(topic_id)

            if subtopics:
                # Update user state with the new topic and reset subtopic/content indices
                user_state.update({"topic": topic_id, "subtopic": None, "content_index": 0})
                save_user_data(user_state)

                # Build and send the subtopics menu
                subtopics_menu = "Choose a subtopic:%0a" + "%0a".join([f"({st[0]}) {st[1]}" for st in subtopics])
                send_message(sender, subtopics_menu)
            else:
                send_message(sender, f"Topic {topic_id} does not exist or has no subtopics. Please try again.")

        elif int(message.strip()):
            topic_parts = message.strip()
           

            topic_id = int(topic_parts)  # Extract the topic ID from the message
            subtopics = get_subtopics(topic_id)

            if subtopics:
                # Update user state with the new topic and reset subtopic/content indices
                user_state.update({"topic": topic_id, "subtopic": None, "content_index": 0})
                save_user_data(user_state)

                # Build and send the subtopics menu
                subtopics_menu = "Choose a subtopic:%0a" + "%0a".join([f"({st[0]}) {st[1]}" for st in subtopics])
                send_message(sender, subtopics_menu)
            else:
                send_message(sender, f"Topic {topic_id} does not exist or has no subtopics. Please try again.")

        else:
            # Delegate to content navigation handler for unrecognized messages
            handle_content_navigation(sender, message, user_state)
    except ValueError:
        send_message(sender, "Please specify a valid numeric topic ID. For example: 'topic 1'.")
    except IndexError:
        send_message(sender, "Error processing your request. Make sure your message is in the correct format (e.g., 'topic 1').")
    except Exception as e:
        print(f"Unexpected error in handle_topic_selection: {e}")
        traceback.print_exc()
        send_message(sender, "An unexpected error occurred. Please try again.")


def handle_subtopic_selection(sender, message, user_state):
    """
    Handles the selection of a subtopic by the user.
    """
    try:
        subtopic_id = int(message)
        query = """
        SELECT id
        FROM subtopics
        WHERE topic_id = ?
        ORDER BY id
        LIMIT 1 OFFSET ?;
        """
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            topic_id = user_state["topic"]
            # Execute the query with the provided topic_id and index
            cursor.execute(query, (topic_id, subtopic_id))
            result = cursor.fetchone()

            # Return the ID if found
            subtopic_id = result[0] if result else None
            conn.close()

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            conn.close()
            return None


        content = get_content(subtopic_id)
        if content:
            user_state.update({"subtopic": subtopic_id, "content_index": 0})
            save_user_data(user_state)
            send_message(sender, content[user_state["content_index"]][0])  # Send the first piece of content
        else:
            send_message(sender, "Invalid subtopic. Please try again.")
    except ValueError:
        send_message(sender, "Please enter a valid subtopic number.")


def handle_content_navigation(sender, message, user_state):
    """
    Handles content navigation (next, back, next topic, etc.) based on user input.
    """
    content = get_content(user_state["subtopic"])
    subtopics = get_subtopics(user_state["topic"])

    if message.lower() == "n":
        if user_state["content_index"] < len(content) - 1:
            user_state["content_index"] += 1
            save_user_data(user_state)
            send_message(sender, content[user_state["content_index"]][0])
        else:
            # At the end of the subtopic; move to the next subtopic/topic
            current_subtopic_index = next((i for i, st in enumerate(subtopics) if st[0] == user_state["subtopic"]), -1)
            if current_subtopic_index < len(subtopics) - 1:
                next_subtopic_id = subtopics[current_subtopic_index + 1][0]
                user_state.update({"subtopic": next_subtopic_id, "content_index": 0})
                save_user_data(user_state)
                next_content = get_content(next_subtopic_id)
                send_message(sender, f"You've reached the end of this subtopic!  Moving to the next one:%0a%0a{next_content[0]}")
            else:
                send_message(sender, "You're at the last subtopic! Moving to the next topic...")
                handle_next_topic(sender, user_state)

    elif message.lower() == "b":
        if user_state["content_index"] > 0:
            user_state["content_index"] -= 1
            save_user_data(user_state)
            send_message(sender, content[user_state["content_index"]][0])
        else:
            # At the start of the subtopic; move to the previous subtopic/topic
            current_subtopic_index = next((i for i, st in enumerate(subtopics) if st[0] == user_state["subtopic"]), -1)
            if current_subtopic_index > 0:
                prev_subtopic_id = subtopics[current_subtopic_index - 1][0]
                prev_content = get_content(prev_subtopic_id)
                user_state.update({"subtopic": prev_subtopic_id, "content_index": len(prev_content) - 1})
                save_user_data(user_state)
                send_message(sender, f"You're moving back to the previous subtopic.  Here's where you left off:%0a%0a{prev_content[-1]}")
            else:
                send_message(sender, "You're at the first subtopic! Moving to the previous topic...")
                handle_previous_topic(sender, user_state)

    elif message.lower() == "next":
        handle_next_topic(sender, user_state)
    elif message.lower() == "back":
        handle_previous_topic(sender, user_state)
    else:
        send_message(sender, "Invalid command. Send 'info' for more details")

# Helper functions for topic transitions (handle_next_topic, handle_previous_topic) remain similar
def handle_next_subtopic(sender, user_state):
    """
    Moves the user to the next topic and its first subtopic.

    :param sender: The sender's identifier (e.g., phone number).
    :param user_state: The user's current state as a dictionary.
    """
    try:
        topic_id = user_state["topic"]
        next_subtopic = user_state["subtopic"] + 1

        if next_subtopic:
            user_state.update({"subtopic": next_subtopic, "content_index": 0})
            save_user_data(user_state)
	    
            # Notify user and send first subtopic content
	    try:
                first_content = get_content(next_subtopic)
	    except:
		first_content= get_content(2)
		next_subtopic = 1
	        user_state.update({"topic":2, "subtopic": 1, "content_index": 0})
                save_user_data(user_state)
		
            if first_content:
                send_message(
                sender,
                f" You've moved to the next subtopic (Topic {next_subtopic}).%0a%0aStarting subtopic:%0a{first_content[0][0]}"
            )
            else:
                send_message(sender, "No content available in the first subtopic.")
        else:
            send_message(sender, "There are no more topics to move to.")
    except Exception as e:
        print(f"Error in handle_next_topic: {e}")
        traceback.print_exc()
        send_message(sender, " An error occurred while navigating to the next topic. Please try again.")


def handle_previous_topic(sender, user_state):
    """
    Moves the user to the previous topic and its last subtopic.

    :param sender: The sender's identifier (e.g., phone number).
    :param user_state: The user's current state as a dictionary.
    """
    try:
	prev_topic_id = user_state["topic"] - 1
        prev_subtopic = user_state["subtopic"] - 1
        if prev_topic_id <= 0:
            send_message(sender, "There are no previous topics to move to.")
            return

        if prev_subtopic:
            user_state.update({"subtopic": prev_subtopic, "content_index": 0})
            save_user_data(user_state)

            # Notify user and send last subtopic content
	    try:
                last_content = get_content(prev_subtopic)
	    except:
		last_content= get_content(2)
		prev_subtopic = 1
	        user_state.update({"topic":2, "subtopic": 1, "content_index": 0})
                save_user_data(user_state)
		    
            if last_content:
                send_message(
                sender,
                f" You've moved to the previous subtopic (Topic {prev_subtopic}).%0a%0aStarting from the last subtopic:%0a{last_content[0][0]}"
            )
            else:
                send_message(sender, "No content available in the last subtopic.")
        else:
            send_message(sender, "The previous topic has no subtopics.")
    except Exception as e:
        print(f"Error in handle_previous_topic: {e}")
        traceback.print_exc()
        send_message(sender, " An error occurred while navigating to the previous topic. Please try again.")

 
# Start listening
press_unread_button()
listen_and_respond()
