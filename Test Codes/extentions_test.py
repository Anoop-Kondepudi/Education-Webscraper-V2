import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Path to manually downloaded Save Page WE extension
EXTENSION_PATH = "/Users/anoopkondepudi/Desktop/Education Webscraper V2/Education-Webscraper-V2/ProjectFiles/Extensions/save_page_we-28.11.xpi"  # Update with correct path

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI

    # Install Save Page WE extension manually
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    driver.install_addon(EXTENSION_PATH, temporary=True)  # Load the extension

    return driver
