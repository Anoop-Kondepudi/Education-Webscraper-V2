import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Use existing Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/6sbklhar.default-release"

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    options.add_argument(f"-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Simulate typing in a new tab
def test_keyboard_input(driver):
    driver.execute_script("window.open('');")  # Open a new tab
    driver.switch_to.window(driver.window_handles[-1])  # Switch to new tab
    
    time.sleep(2)
    
    actions = ActionChains(driver)
    actions.send_keys("Hello this is a test").perform()
    print("✅ Typed 'Hello this is a test' in the new tab!")

    time.sleep(3)  # Pause to see the result

def scrape_brainly(url):
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)  # Allow page to load fully

    # Test keyboard input
    test_keyboard_input(driver)
    
    driver.quit()
    print("✅ Webpage test completed!")

if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"
    scrape_brainly(test_url)
