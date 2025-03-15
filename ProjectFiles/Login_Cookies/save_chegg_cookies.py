import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
import os

# Path to save cookies
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/chegg_cookies.json")

# Chrome profile path
CHROME_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Google/Chrome/Profile 1"

# Set up WebDriver with anti-detection measures
def setup_driver():
    print(f"Opening Chrome with profile: {CHROME_PROFILE_PATH}")
    
    options = ChromeOptions()
    options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Random window size to appear more human
    width = random.randint(1050, 1200)
    height = random.randint(800, 950)
    options.add_argument(f"--window-size={width},{height}")
    
    # Common user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=options)
    
    # Additional techniques to evade detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("window.navigator.chrome = { runtime: {} }")
    
    return driver

# Save cookies after login
def save_cookies(driver):
    print("Attempting to save cookies...")
    # Simulate human behavior - wait a bit
    time.sleep(random.uniform(1.5, 3.0))
    
    cookies = driver.get_cookies()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)
    
    with open(COOKIES_PATH, "w") as file:
        json.dump(cookies, file)
    print(f"✅ Cookies saved to {COOKIES_PATH}")
    print(f"Total cookies saved: {len(cookies)}")

# Run login process
def login_and_save_cookies():
    print("Starting Chrome and opening Chegg...")
    driver = setup_driver()
    
    # Add random delay before navigating to appear more human-like
    time.sleep(random.uniform(1.0, 2.5))
    
    # Load Chegg
    driver.get("https://www.chegg.com")
    
    # Wait a bit before clicking login - simulate human behavior
    time.sleep(random.uniform(2.0, 4.0))
    
    # Now navigate to login page
    driver.get("https://www.chegg.com/auth")
    
    print("\n📢 IMPORTANT: Please sign in to your Chegg account manually.")
    print("📢 Make sure you're completely logged in before continuing.")
    input("🔷 After logging in, press ENTER to save cookies...")
    
    # Check if we're logged in by looking for session indicators
    if "auth0.identity" in driver.current_url or "Log in" in driver.title:
        print("⚠️ WARNING: It appears you may not be fully logged in yet.")
        input("🔷 Please confirm you are logged in, then press ENTER again...")
    
    save_cookies(driver)
    print("Closing browser...")
    driver.quit()

# Run script
if __name__ == "__main__":
    print("=== Chegg Cookie Saver ===")
    try:
        login_and_save_cookies()
        print("=== Process Complete ===")
    except Exception as e:
        print(f"Error: {e}") 