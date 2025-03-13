# To grab the cookies for Quizlet, you need to log in manually on your browser. (Not selenium browser)
# Then download the extension: EditThisCookie
# Go to Quizlet.com and log in again.
# Click the EditThisCookie extension and export the cookies.
# Create a new file in Cookies folder called quizlet_cookies.json
# Paste the cookies into the file.
# Run the script. (quizlet_scraper.py)

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from capsolver_extension_python import Capsolver  # Correct CapSolver import

# Load your CapSolver API Key
CAPSOLVER_API_KEY = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"

# Path to save cookies
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/quizlet_cookies.json")

# Set up Selenium WebDriver with CapSolver extension
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Must be visible to pass Cloudflare verification

    # Load CapSolver extension
    options.add_argument(Capsolver(api_key=CAPSOLVER_API_KEY).load())

    # Start the browser
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Save cookies after login
def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIES_PATH, "w") as file:
        json.dump(cookies, file)
    print(f"✅ Cookies saved to {COOKIES_PATH}")

# Login to Quizlet & Save Cookies
def login_and_save_cookies():
    driver = setup_driver()
    driver.get("https://quizlet.com/login")

    input("🔷 Log in manually, then press ENTER to save cookies...")

    save_cookies(driver)
    driver.quit()

# Run the script
if __name__ == "__main__":
    login_and_save_cookies()