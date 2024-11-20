from config import *
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Helper function to wait for an element
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

# Check if already logged in (check for the QR code canvas)
def is_logged_in(driver):
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "canvas")
        print("Not logged in. Attempting phone login...")
        return False
    except Exception:
        print("Already logged in.")
        return True

# Phone login process
def phone_login(driver):
    # Wait for "Log in with phone number" button and click it
    phone_login_button = wait_for_element(driver, By.XPATH, '//div[contains(text(), "Log in with phone number")]')
    if phone_login_button:
        phone_login_button.click()

    time.sleep(30)  # Assuming we wait for QR code scanning or phone number login flow

    # Input phone number
    phone_number = "+233535372400"
    phone_input_field = wait_for_element(driver, By.XPATH, '//input[@type="text"]')
    if phone_input_field:
        phone_input_field.send_keys(Keys.CONTROL + "a")
        phone_input_field.send_keys(Keys.DELETE)
        phone_input_field.send_keys(phone_number)
        phone_input_field.send_keys(Keys.ENTER)
    
    time.sleep(15)  # Wait for the input to process

    # Get the confirmation code
    code_element = wait_for_element(driver, By.XPATH, "//div[@data-link-code]")
    if code_element:
        data_link_code = code_element.get_attribute("data-link-code")
        data_link_code = data_link_code.replace(",", ' ')
        print(f"Confirmation Code: {data_link_code[:7] + ' -' + data_link_code[7:]}")

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
