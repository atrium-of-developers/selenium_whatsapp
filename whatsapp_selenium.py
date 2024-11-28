from config import *
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Check if already logged in (check for the QR code canvas)
def is_logged_in(driver):
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "canvas")
        print("Not logged in. Attempting phone login...")
        return False
    except Exception:
        print("Already logged in.")
        return True

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def wait_for_element(driver, by, value, timeout=30):
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
        driver.execute_async_script(script)
        print(f"Element {value} is now available.")
        return driver.find_element(by, value)
    except Exception as e:
        print(f"Element {value} not found: {e}")
        return None

# Polling function to catch dynamic attribute change
def poll_for_dynamic_attribute(driver, xpath, timeout=30, poll_interval=1):
    try:
        # Get the initial element
        element = driver.find_element(By.XPATH, xpath)
        old_value = element.get_attribute('data-link-code')

        end_time = time.time() + timeout
        while time.time() < end_time:
            time.sleep(poll_interval)
            element = driver.find_element(By.XPATH, xpath)
            new_value = element.get_attribute('data-link-code')

            if new_value != old_value:
                old_value = new_value
                data_link_code = new_value.replace(",", ' ')
                print(f"Updated Confirmation Code: {data_link_code[:7] + ' -' + data_link_code[7:]}")
                
        print("Timeout reached, no further changes detected.")
    except Exception as e:
        print(f"Error: {e}")


# Phone login process
def phone_login(driver):
    # Wait for "Log in with phone number" button and click it
    phone_login_button = wait_for_element(driver, By.XPATH, '//div[contains(text(), "Log in with phone number")]')
    if phone_login_button:
        phone_login_button.click()

    time.sleep(30)  # Assuming we wait for QR code scanning or phone number login flow

    # Input phone number
    phone_number = "+233509119224"
    phone_input_field = wait_for_element(driver, By.XPATH, '//input[@type="text"]')
    if phone_input_field:
        phone_input_field.send_keys(Keys.CONTROL + "a")
        phone_input_field.send_keys(Keys.DELETE)
        phone_input_field.send_keys(phone_number)
        phone_input_field.send_keys(Keys.ENTER)
    
    time.sleep(15)  # Wait for the input to process

    # Get the confirmation code
    poll_for_dynamic_attribute(driver, "//div[@data-link-code]")
    # Wait for confirmation from the user to proceed
    input("Press Enter if you have linked the device")
    print("Code entered. You should be logged in shortly.")
    
# Main function
def main(driver):
    # Wait for the page to load
    print("Waiting for the WhatsApp Web to load...")
    time.sleep(15)  # Allow some initial page loading time (if needed)

    # Check if the user is already logged in
    logged_in = is_logged_in(driver)
    if not logged_in:
        phone_login(driver)

    # Quit the driver after everything is done
    # driver.quit()

# Run the main function
if __name__ == "__main__":
    main(driver)
    import interface_handler
