import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
import os
import re
from urllib.parse import urlparse
import random
import string

# Firefox profile path
PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/wovqm2hm.CHAccGen"

# Capsolver API key
CAPSOLVER_API_KEY = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"

# Function to initialize Selenium WebDriver with the specific profile
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)
    
    # Set user agent to appear more like a regular browser
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    
    service = FirefoxService(GeckoDriverManager().install(), log_output=None)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

# Function to wait for user input to continue (debugging helper)
def wait_for_user_input(driver, message="Press Enter in console to continue..."):
    print(message)
    input()  # Wait for user to press Enter
    return driver

# Function to wait for page to be fully loaded
def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("Page fully loaded")

# Function to get a temporary email from temp-mail.io
def get_temp_email():
    driver = setup_driver()
    
    try:
        # Navigate to temp-mail.io
        print("Navigating to temp-mail.io...")
        driver.get("https://temp-mail.io/en")
        
        # Wait for the page to load using proper wait mechanism
        print("Waiting for page to load...")
        wait_for_page_load(driver)
        
        # Additional wait for any dynamic content to initialize
        try:
            # Wait for a key element on the page to confirm it's fully interactive
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="email"]'))
            )
        except:
            print("Warning: Email field not immediately available, but proceeding")
        
        # Wait for user to press Enter to start the process
        wait_for_user_input(driver, "Press Enter to click the random button and generate an email...")
        
        try:
            # Use the exact XPath for the random button
            random_btn_xpath = "/html/body/div[1]/div/header/div[2]/button[2]"
            print(f"Clicking random button with XPath: {random_btn_xpath}")
            
            # Wait for button to be clickable using explicit wait
            random_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, random_btn_xpath))
            )
            random_btn.click()
            print("Clicked random button")
            
            # Use the exact XPath for the email field that the user provided
            email_xpath = '//*[@id="email"]'
            print(f"Checking email from XPath: {email_xpath}")
            
            # Poll the email field until a non-empty value appears
            max_attempts = 30  # Maximum number of attempts to check
            polling_interval = 0.5  # Time between checks in seconds
            email = ""
            
            print("Waiting for email to appear...")
            for attempt in range(max_attempts):
                try:
                    email_element = driver.find_element(By.XPATH, email_xpath)
                    email = email_element.get_attribute("value")
                    
                    # Check if we have a valid email (non-empty and contains @)
                    if email and '@' in email:
                        print(f"Email found after {attempt + 1} attempts: {email}")
                        break
                    else:
                        print(f"Attempt {attempt + 1}: Email not ready yet, retrying...")
                        time.sleep(polling_interval)  # Still need this small sleep between polls
                except Exception as e:
                    print(f"Attempt {attempt + 1}: Error checking email: {e}")
                    time.sleep(polling_interval)  # Still need this small sleep between polls
            
            if not email or '@' not in email:
                print("Could not obtain email automatically after maximum attempts")
                email = input("Please enter the generated email manually: ")
            
            # Keep browser open for manual inspection
            wait_for_user_input(driver, f"Email: {email}\nPress Enter to continue with Coursehero registration...")
            
            return email, driver
            
        except Exception as e:
            print(f"Error during email generation process: {e}")
            # Fallback to manual entry
            email = input("Please enter the generated email manually: ")
            return email, driver
    
    except Exception as e:
        print(f"Error accessing temp-mail.io: {e}")
        wait_for_user_input(driver, "Press Enter to close the browser...")
        driver.quit()
        return None, None

# Capsolver API integration
def solve_hcaptcha(driver, site_key, page_url):
    print("Solving hCaptcha...")
    
    # Create the task for Capsolver API
    task_payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key
        }
    }
    
    # Submit the task to Capsolver
    response = requests.post("https://api.capsolver.com/createTask", json=task_payload)
    response_data = response.json()
    
    if response_data.get("errorId") > 0:
        print(f"Error creating Capsolver task: {response_data.get('errorDescription')}")
        return None
    
    # Get the task ID
    task_id = response_data.get("taskId")
    print(f"Task created with ID: {task_id}")
    
    # Wait for the solution
    max_attempts = 60  # 30 seconds total (0.5s * 60)
    for attempt in range(max_attempts):
        solution_payload = {
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id
        }
        
        solution_response = requests.post("https://api.capsolver.com/getTaskResult", json=solution_payload)
        solution_data = solution_response.json()
        
        if solution_data.get("status") == "ready":
            captcha_key = solution_data.get("solution", {}).get("gRecaptchaResponse")
            print("hCaptcha solved successfully!")
            return captcha_key
        
        if solution_data.get("status") == "failed":
            print(f"Captcha solving failed: {solution_data.get('errorDescription')}")
            return None
        
        print(f"Waiting for captcha solution, attempt {attempt + 1}...")
        time.sleep(0.5)
    
    print("Captcha solving timed out")
    return None

# Generate a random strong password
def generate_password():
    # Generate a password with 12 characters, including uppercase, lowercase, digits, and special chars
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(12))
    return password

# Enhanced function to handle Imperva hCaptcha specifically
def handle_imperva_hcaptcha(driver):
    print("Detected Imperva security check with hCaptcha...")
    
    # Wait for the hCaptcha iframe to be present
    try:
        print("Waiting for hCaptcha iframe to load...")
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'hcaptcha.com')]"))
        )
        print("Switched to hCaptcha iframe")
        
        # Now we're inside the iframe, look for the checkbox
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "checkbox"))
        )
        print("Found hCaptcha checkbox")
        
        # Click the checkbox
        checkbox.click()
        print("Clicked hCaptcha checkbox")
        
        # Switch back to the main content
        driver.switch_to.default_content()
        
        # Wait for verification to complete
        time.sleep(3)
        
        # Check if we need to solve additional challenges
        if "Please solve the challenge" in driver.page_source or "Select all images" in driver.page_source:
            print("Additional challenge detected, trying to solve with Capsolver API...")
            
            # Extract the site key for hCaptcha
            driver.switch_to.default_content()
            site_key = extract_hcaptcha_site_key(driver)
            
            if site_key:
                captcha_response = solve_hcaptcha(driver, site_key, driver.current_url)
                if captcha_response:
                    # Inject the captcha response
                    driver.execute_script(f'document.querySelector("[name=h-captcha-response]").value = "{captcha_response}";')
                    driver.execute_script('document.querySelector("form").submit();')
                    print("Captcha solution submitted via API")
                    wait_for_page_load(driver)
                else:
                    print("Failed to solve captcha via API, manual intervention required")
                    wait_for_user_input(driver, "Please solve the captcha manually and press Enter when done...")
            else:
                print("Could not extract hCaptcha site key")
                wait_for_user_input(driver, "Please solve the captcha manually and press Enter when done...")
        
        return True
        
    except Exception as e:
        print(f"Error handling Imperva hCaptcha: {e}")
        driver.switch_to.default_content()  # Make sure we're back to main content
        wait_for_user_input(driver, "Please solve the captcha manually and press Enter when done...")
        return False

# Helper function to extract hCaptcha site key
def extract_hcaptcha_site_key(driver):
    try:
        # Method 1: Look for data-sitekey attribute on the hcaptcha div
        try:
            hcaptcha_div = driver.find_element(By.CLASS_NAME, "h-captcha")
            site_key = hcaptcha_div.get_attribute("data-sitekey")
            if site_key:
                print(f"Found hCaptcha site key from div: {site_key}")
                return site_key
        except:
            pass
        
        # Method 2: Extract from iframe src
        try:
            iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'hcaptcha.com')]")
            iframe_src = iframe.get_attribute("src")
            site_key_match = re.search(r'sitekey=([^&]+)', iframe_src)
            if site_key_match:
                site_key = site_key_match.group(1)
                print(f"Found hCaptcha site key from iframe: {site_key}")
                return site_key
        except:
            pass
        
        # Method 3: Search in page source
        page_source = driver.page_source
        site_key_match = re.search(r'data-sitekey="([^"]+)"', page_source)
        if site_key_match:
            site_key = site_key_match.group(1)
            print(f"Found hCaptcha site key from page source: {site_key}")
            return site_key
            
        return None
    except Exception as e:
        print(f"Error extracting site key: {e}")
        return None

# Function to register on CourseHero
def register_on_coursehero(driver, email):
    try:
        print("Navigating to CourseHero registration page...")
        driver.get("https://www.coursehero.com/register/")
        
        # Wait for page to load
        wait_for_page_load(driver)
        
        # Check if we're on a captcha/security check page 
        if "security check" in driver.page_source.lower() or "imperva" in driver.page_source.lower():
            print("Security check/captcha detected before registration page")
            handle_imperva_hcaptcha(driver)
            
            # Wait for redirection to the actual registration page
            wait_for_page_load(driver)
            
            # Double-check if we're still on a security page
            if "security check" in driver.page_source.lower() or "imperva" in driver.page_source.lower():
                print("Still on security check page after captcha attempt")
                wait_for_user_input(driver, "Please complete the security check manually and press Enter...")
        
        # Allow inspection and wait for user confirmation before proceeding
        wait_for_user_input(driver, "We should now be on the registration page. Press Enter to continue with form inspection...")
        
        # Let's wait for user to help identify form elements
        print("Please inspect the page and confirm the following element IDs/selectors:")
        print("1. Email field")
        print("2. Password field")
        print("3. Any other required fields (first name, last name, etc.)")
        print("4. Submit button")
        
        # Use explicit waits to wait for registration form elements
        try:
            print("Attempting to locate registration form elements...")
            
            # First let's try to wait for common registration form elements to be present
            try:
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or @id='email']"))
                )
                print(f"Email field found: {email_field.get_attribute('id') or email_field.get_attribute('name')}")
                
                # Try to find password field
                password_field = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @id='password']")
                print(f"Password field found: {password_field.get_attribute('id') or password_field.get_attribute('name')}")
                
                # Try to find submit button
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
                print(f"Submit button found: {submit_button.get_attribute('id') or submit_button.get_attribute('class')}")
                
                # Ask user to confirm these are correct
                confirmation = input("Are these elements correct? (yes/no): ")
                if confirmation.lower() != "yes":
                    raise Exception("User indicated elements are incorrect")
            except Exception as e:
                print(f"Could not automatically identify form elements: {e}")
                # Ask for user input on the selectors
                email_selector = input("Enter email field selector (xpath or css): ")
                password_selector = input("Enter password field selector (xpath or css): ")
                submit_selector = input("Enter submit button selector (xpath or css): ")
                
                # Determine selector type and find elements
                email_field = locate_element(driver, email_selector)
                password_field = locate_element(driver, password_selector)
                submit_button = locate_element(driver, submit_selector)
            
            # Generate a random password
            password = generate_password()
            print(f"Generated password: {password}")
            
            # Fill out the form
            print("Filling out registration form...")
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            # Check if there are additional required fields
            additional_fields = input("Are there additional required fields? (yes/no): ")
            if additional_fields.lower() == "yes":
                while True:
                    field_selector = input("Enter field selector (or 'done' to finish): ")
                    if field_selector.lower() == "done":
                        break
                    field_value = input("Enter value for this field: ")
                    field = locate_element(driver, field_selector)
                    field.send_keys(field_value)
            
            # Wait for user confirmation before submitting
            wait_for_user_input(driver, f"Form filled with email: {email} and password: {password}\nPress Enter to submit the form...")
            
            # Submit the form
            submit_button.click()
            
            # Wait for registration to complete
            wait_for_page_load(driver)
            
            # Confirm success and keep window open
            wait_for_user_input(driver, "Registration submitted! Press Enter to continue...")
            
            return {"email": email, "password": password}
            
        except Exception as e:
            print(f"Error during form filling: {e}")
            wait_for_user_input(driver, "Error encountered. Press Enter to continue...")
            return None
    
    except Exception as e:
        print(f"Error accessing CourseHero: {e}")
        wait_for_user_input(driver, "Error accessing CourseHero. Press Enter to continue...")
        return None

# Helper function to locate elements with either XPath or CSS selectors
def locate_element(driver, selector):
    # Check if it's an XPath (contains // or starts with /)
    if selector.startswith('//') or selector.startswith('/'):
        return driver.find_element(By.XPATH, selector)
    else:
        # Assume it's a CSS selector
        return driver.find_element(By.CSS_SELECTOR, selector)

# Main function to generate Coursehero account
def generate_coursehero_account():
    email, driver = get_temp_email()
    
    if email:
        print(f"Successfully obtained temp email: {email}")
        
        # Register on CourseHero
        registration_data = register_on_coursehero(driver, email)
        
        if registration_data:
            print("Account created successfully!")
            print(f"Email: {registration_data['email']}")
            print(f"Password: {registration_data['password']}")
            
            # Save the account info to a file
            with open("coursehero_accounts.txt", "a") as f:
                f.write(f"Email: {registration_data['email']}, Password: {registration_data['password']}\n")
            
            print("Account information saved to coursehero_accounts.txt")
        
        # Keep browser open until user decides to close
        wait_for_user_input(driver, "Press Enter to close the browser...")
        driver.quit()
    else:
        print("Failed to obtain temp email")

if __name__ == "__main__":
    generate_coursehero_account() 