import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import os
import re

# Path to cookies file
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/studocu_cookies.json")

# Path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

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
    # Create a more descriptive filename based on URL
    # Extract document ID or name from URL if possible
    match = re.search(r'\/document\/([^\/]+)', url)
    if match:
        file_id = match.group(1)
    else:
        file_id = str(int(time.time()))  # Use timestamp as fallback
    
    filename = f"studocu_{file_id}.html"
    filepath = os.path.join(DOWNLOADS_PATH, filename)
    
    # Ensure the Downloads directory exists
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)
    
    driver.get(url)
    time.sleep(5)  # Allow page to fully load

    html_content = driver.page_source  # Get full HTML of the page

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"✅ Webpage saved as {filename} in {DOWNLOADS_PATH}")
    return filepath  # Return the file path

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

if __name__ == "__main__":
    # Test URL - you can change this for testing different Studocu pages
    test_url = "https://www.studocu.com/en-us/document/santa-ana-high-school/integrated-math/calculus-cheat-sheet/64871935"
    print(f"🚀 Testing Studocu scraper with URL: {test_url}")
    
    # Run the scraper
    output_file = scrape_studocu(test_url)
    
    print(f"\n✅ Studocu scraping complete!")
    print(f"✅ Output saved as: {output_file}")