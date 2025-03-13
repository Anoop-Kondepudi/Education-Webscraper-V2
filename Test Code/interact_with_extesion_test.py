import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Use your Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    options.add_argument("-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Start Firefox with your profile
driver = setup_driver()

# Open a test webpage
driver.get("https://www.google.com")

# Simulate pressing Ctrl + Shift + S (or your assigned shortcut)
actions = ActionChains(driver)
actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys("S").key_up(Keys.CONTROL).key_up(Keys.SHIFT).perform()

# Wait to see if the extension activates
time.sleep(5)

# Close the browser
driver.quit()