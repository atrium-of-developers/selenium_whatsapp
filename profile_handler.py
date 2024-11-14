import sqlite3
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

# Async function to wait for elements using `execute_async_script`
async def wait_for_element(driver, by, value, timeout=30):
    """Wait for an element to appear using JavaScript promises."""
    script = f"""
    var callback = arguments[arguments.length - 1];
    new Promise((resolve, reject) => {{
        var checkExist = setInterval(function() {{
            if (document.querySelector('{value}')) {{
                clearInterval(checkExist);
                resolve();
            }}
        }}, 100);
        setTimeout(() => {{
            clearInterval(checkExist);
            reject(new Error('Element not found within timeout.'));
        }}, {timeout * 1000});
    }}).then(callback).catch(callback);
    """
    try:
        await driver.execute_async_script(script)
        print(f"Element {value} is now available.")
        return driver.find_element(by, value)
    except Exception as e:
        print(f"Element {value} not found: {e}")
        return None

async def async_find_elements(driver, by, value, timeout=30):
    """Async wrapper to find multiple elements using JavaScript promises."""
    elements_script = f"""
    var callback = arguments[arguments.length - 1];
    new Promise((resolve, reject) => {{
        var checkExist = setInterval(function() {{
            if (document.querySelectorAll('{value}').length > 0) {{
                clearInterval(checkExist);
                resolve(document.querySelectorAll('{value}'));
            }}
        }}, 100);
        setTimeout(() => {{
            clearInterval(checkExist);
            reject(new Error('Elements not found within timeout.'));
        }}, {timeout * 1000});
    }}).then(callback).catch(callback);
    """
    try:
        elements = await driver.execute_async_script(elements_script)
        return elements
    except Exception as e:
        print(f"Elements not found: {e}")
        return []

async def async_click_element(driver, element):
    """Async wrapper to click an element using JavaScript."""
    try:
        await driver.execute_async_script("arguments[0].click();", element)
        print("Element clicked.")
    except Exception as e:
        print(f"Error clicking element: {e}")

async def track_chats(driver):
    """Monitor new messages and save profiles if it's the first interaction."""
    while True:
        await asyncio.sleep(5)  # Async sleep for non-blocking wait
        
        try:
            # Find unread messages button and click it
            unread_chats = await async_find_elements(driver, By.XPATH, './/div[contains(@class, "unread")]')
            
            for chat in unread_chats:
                await async_click_element(driver, chat)
                await asyncio.sleep(2)  # Allow the chat to open
                
                # Get the sender's name or phone number
                contact_name_element = await wait_for_element(driver, By.XPATH, '//header//span[@title]')
                contact_name = contact_name_element.get_attribute('title') if contact_name_element else "Unknown"
                
                # Get the last message sent by the person
                message_elements = await async_find_elements(driver, By.XPATH, '//div[contains(@class, "message-in")]//span[@class="selectable-text"]')
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

async def main_(driver):
    await asyncio.sleep(15)  # Adjust this based on how long you need for the scan
    
    # Start tracking chats
    await track_chats(driver)

# Initialize the WebDriver and run the main function
if __name__ == "__main__":
    asyncio.run(main_(driver))
