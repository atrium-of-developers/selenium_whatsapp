from config import *

# Async function to wait for an element using `execute_async_script`
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

# Check if already logged in (check for the QR code canvas)
async def is_logged_in():
    try:
        await wait_for_element(driver, By.CSS_SELECTOR, "canvas")
        print("Not logged in. Attempting phone login...")
        return False
    except Exception:
        print("Already logged in.")
        return True

# Phone login process
async def phone_login():
    # Wait for "Log in with phone number" button and click it
    phone_login_button = await wait_for_element(driver, By.XPATH, '//div[contains(text(), "Log in with phone number")]')
    if phone_login_button:
        phone_login_button.click()

    await asyncio.sleep(60)  # Assuming we wait for QR code scanning or phone number login flow

    # Input phone number
    phone_number = "+233535372400"
    phone_input_field = await wait_for_element(driver, By.XPATH, '//input[@type="text"]')
    if phone_input_field:
        phone_input_field.send_keys(Keys.CONTROL + "a")
        phone_input_field.send_keys(Keys.DELETE)
        phone_input_field.send_keys(phone_number)
        phone_input_field.send_keys(Keys.ENTER)
    
    await asyncio.sleep(6)  # Wait for the input to process

    # Get the confirmation code
    code_element = await wait_for_element(driver, By.XPATH, "//div[@data-link-code]")
    if code_element:
        data_link_code = code_element.get_attribute("data-link-code")
        data_link_code = data_link_code.replace(",", ' ')
        print(f"Confirmation Code: {data_link_code[:7] + ' -' + data_link_code[7:]}")

    # Wait for confirmation from the user to proceed
    input("Press Enter if you have linked the device")
    print("Code entered. You should be logged in shortly.")
    
# Main async function
async def main():
    # Wait for the page to load
    print("Waiting for the WhatsApp Web to load...")
    await asyncio.sleep(15)  # Allow some initial page loading time (if needed)

    # Check if the user is already logged in
    logged_in = await is_logged_in()
    if not logged_in:
        await phone_login()


    # Quit the driver after everything is done
    #driver.quit()

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
    import profile_handler
