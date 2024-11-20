import sqlite3
import time
from selenium.webdriver.common.by import By
from config import *

# Database helper functions
def create_table():
    """Create clients table if it doesn't exist."""
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone_number TEXT,
            messages TEXT
        )
        ''')
        conn.commit()

def is_new_client(phone_number):
    """Check if the client already exists in the database."""
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE phone_number = ?', (phone_number,))
        result = cursor.fetchone()
    return result is None

def save_client_profile(name, phone_number, initial_message):
    """Save a new client's profile to the database."""
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clients (name, phone_number, messages) VALUES (?, ?, ?)', 
                       (name, phone_number, initial_message))
        conn.commit()

def update_client_messages(phone_number, new_message):
    """Update the chat history for an existing client."""
    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT messages FROM clients WHERE phone_number = ?', (phone_number,))
        existing_messages = cursor.fetchone()[0]
        updated_messages = existing_messages + '\n' + new_message
        cursor.execute('UPDATE clients SET messages = ? WHERE phone_number = ?', 
                       (updated_messages, phone_number))
        conn.commit()

# Create the table on first run
create_table()

def wait_for_element(driver, by, value, timeout=30):
    """Wait for an element to appear."""
    for _ in range(timeout * 10):  # Loop to wait for up to 'timeout' seconds
        try:
            element = driver.find_element(by, value)
            if element:
                print(f"Element {value} is now available.")
                return element
        except:
            pass
        time.sleep(0.1)
    print(f"Element {value} not found within {timeout} seconds.")
    return None

def find_elements(driver, by, value, timeout=30):
    """Find multiple elements, waiting for them if necessary."""
    for _ in range(timeout * 10):  # Loop to wait for up to 'timeout' seconds
        try:
            elements = driver.find_elements(by, value)
            if elements:
                return elements
        except:
            pass
        time.sleep(0.1)
    print(f"Elements {value} not found within {timeout} seconds.")
    return []

def click_element(driver, element):
    """Click an element."""
    try:
        driver.execute_script("arguments[0].click();", element)
        print("Element clicked.")
    except Exception as e:
        print(f"Error clicking element: {e}")

def track_chats(driver):
    """Monitor new messages and save profiles if it's the first interaction."""
    while True:
        time.sleep(5)  # Sleep for 5 seconds between scans
        
        try:
            # Find unread messages button and click it
            unread_chats = find_elements(driver, By.XPATH, './/div[contains(text(), "Unread")]')
            
            for chat in unread_chats:
                click_element(driver, chat)
                time.sleep(2)  # Allow the chat to open
                
                # Get the sender's name or phone number
                contact_name_element = wait_for_element(driver, By.XPATH, '//header//span[@title]')
                contact_name = contact_name_element.get_attribute('title') if contact_name_element else "Unknown"
                
                # Get the last message sent by the person
                message_elements = find_elements(driver, By.XPATH, '//div[contains(@class, "message-in")]//span[@class="selectable-text"]')
                last_message = message_elements[-1].text if message_elements else "No message found"
                
                # If contact_name is a phone number, it's likely an unknown contact
                phone_number = contact_name if contact_name.startswith('+') else "Unknown"
                
                # Check if this is a new client
                if is_new_client(phone_number):
                    # Save the client's profile
                    save_client_profile(contact_name, phone_number, last_message)
                    print(f"New client added: {contact_name} - {phone_number}")
                else:
                    # Update the client's chat session
                    update_client_messages(phone_number, last_message)
                    print(f"Message updated for {contact_name} - {phone_number}")
        
        except Exception as e:
            print(f"An error occurred: {e}")

def main_(driver):
    time.sleep(15)  # Adjust this based on how long you need for the scan
    
    # Start tracking chats
    track_chats(driver)

# Initialize the WebDriver and run the main function
if __name__ == "__main__":
    main_(driver)
