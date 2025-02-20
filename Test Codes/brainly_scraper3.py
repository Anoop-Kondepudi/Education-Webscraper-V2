import json
import time
import os
import platform
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI

    # Set download preferences
    download_dir = os.path.join(os.getcwd(), "SavedPages")  # Set download folder
    os.makedirs(download_dir, exist_ok=True)

    options.set_preference("browser.download.folderList", 2)  # Use custom folder
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/html")
    options.set_preference("browser.download.useDownloadDir", True)

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Wait for page to fully render
def wait_for_page_load(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Give extra time for JavaScript rendering
    except Exception as e:
        print(f"⚠️ Page load timeout: {e}")

# Save the page using Selenium Actions
def save_webpage(driver):
    time.sleep(2)  # Wait for the browser to be ready
    actions = ActionChains(driver)

    # Detect macOS and use COMMAND + S instead of CONTROL + S
    if platform.system() == "Darwin":  # macOS
        actions.key_down(Keys.COMMAND).send_keys("s").key_up(Keys.COMMAND).perform()
    else:  # Windows/Linux
        actions.key_down(Keys.CONTROL).send_keys("s").key_up(Keys.CONTROL).perform()

    time.sleep(2)  # Wait for dialog to open
    actions.send_keys(Keys.ENTER).perform()  # Confirm save location
    time.sleep(3)  # Wait for save to complete

# Main function to scrape Brainly page
def scrape_brainly(url):
    driver = setup_driver()
    print("✅ Navigating to Brainly page without login")
    
    driver.get(url)
    wait_for_page_load(driver)
    
    # Save the webpage using Selenium
    save_webpage(driver)
    
    # Close the browser
    driver.quit()
    
    print("✅ Webpage saved successfully")

# Run script
if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"  # Hardcoded Brainly link
    scrape_brainly(test_url)
    print("Webpage saved successfully!")