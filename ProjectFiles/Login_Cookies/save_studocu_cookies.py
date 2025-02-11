import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import os

# Path to save cookies
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/studocu_cookies.json")

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Disable headless so you can log in manually
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Save cookies after login
def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIES_PATH, "w") as file:
        json.dump(cookies, file)
    print(f"✅ Cookies saved to {COOKIES_PATH}")

# Run login process
def login_and_save_cookies():
    driver = setup_driver()
    driver.get("https://www.studocu.com/en-us/login")
    
    input("🔷 Log in manually, then press ENTER to save cookies...")
    
    save_cookies(driver)
    driver.quit()

# Run script
if __name__ == "__main__":
    login_and_save_cookies()