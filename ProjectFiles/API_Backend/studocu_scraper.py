import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import os

# Path to cookies file
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/studocu_cookies.json")

# Function to initialize Selenium WebDriver
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run headless (no browser pop-up)
    options.add_argument("--headless")

    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = FirefoxService(GeckoDriverManager().install(), log_output=None)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

# Function to load saved cookies into the browser
def load_cookies(driver):
    try:
        with open(COOKIES_PATH, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Cookies loaded successfully!")
    except Exception as e:
        print(f"⚠️ Failed to load cookies: {e}")

# Function to download Studocu page as HTML
def save_page_html(driver, url):
    filename = os.path.join(os.path.dirname(__file__), f"studocu_page_{int(time.time())}.html")
    driver.get(url)
    time.sleep(5)  # Allow page to fully load

    html_content = driver.page_source  # Get full HTML of the page

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"✅ Webpage saved as {filename}")
    return filename  # Return the file name

# Main function to scrape Studocu page
def scrape_studocu(url):
    driver = setup_driver()
    driver.get("https://www.studocu.com/en-us/")  # Load Studocu home page first

    # Load cookies for premium access
    load_cookies(driver)
    driver.refresh()
    time.sleep(3)

    print("✅ Logged in using saved cookies!")

    # Download webpage
    html_file = save_page_html(driver, url)

    # Close the browser
    driver.quit()

    return html_file  # Return the saved file path