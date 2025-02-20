import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Use dedicated Brainly automation Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    options.add_argument(f"-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

def scrape_brainly(url, wait_time=10):
    driver = setup_driver()
    driver.get(url)
    
    print(f"✅ Opened {url}, waiting {wait_time} seconds for auto-save...")
    time.sleep(wait_time)  # Allow time for the auto-download to trigger
    
    print("✅ Auto-save should have triggered. Waiting for browser to close...")
    
    driver.quit()
    print("✅ Browser closed. Automation complete!")

if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"
    scrape_brainly(test_url)