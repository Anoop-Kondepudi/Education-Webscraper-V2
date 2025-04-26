import time
import os
import glob
import atexit
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Use dedicated Brainly automation Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Desktop/Education Webscraper V2/Education-Webscraper-V2/ProjectFiles/API_Backend/firefox-profiles/8wofgziv.brainly-expert"

# Correct path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

# Keep track of active browser instances
active_driver = None

def close_active_driver():
    """Close any active driver when the module exits"""
    global active_driver
    if active_driver:
        try:
            active_driver.quit()
            print("✅ Cleaned up expert browser instance on exit")
        except Exception as e:
            print(f"Warning: Error closing browser: {e}")
        active_driver = None

# Register the cleanup function
atexit.register(close_active_driver)

def setup_driver():
    """Set up and return Firefox WebDriver."""
    global active_driver
    
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run in headless mode
    options.add_argument("--headless")
    
    # Set specific window size
    options.add_argument("--width=1280")
    options.add_argument("--height=800")
    
    if os.path.exists(FIREFOX_PROFILE_PATH):
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
    else:
        print("Warning: Firefox profile path not found, using default profile")
    
    # Configure download preferences
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", DOWNLOADS_PATH)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/html")
    
    # Prevent ALL download-related dialogs and prompts
    options.set_preference("browser.download.panel.shown", False)
    options.set_preference("browser.download.manager.showAlertOnComplete", False)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.manager.useWindow", False)
    options.set_preference("browser.download.manager.closeWhenDone", True)
    options.set_preference("browser.download.always_ask_before_handling_new_types", False)
    options.set_preference("browser.download.manager.quitBehavior", 2)
    
    active_driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return active_driver

def check_download_success(driver, timeout=30):
    """Check if download was successful by monitoring the Downloads folder."""
    print(f"Checking for downloads in: {DOWNLOADS_PATH}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Look for newest HTML file in Downloads
        html_files = glob.glob(os.path.join(DOWNLOADS_PATH, "*.html"))
        if html_files:
            newest_file = max(html_files, key=os.path.getctime)
            file_name = os.path.basename(newest_file)
            
            # Check if file was just created (within last few seconds)
            file_creation_time = os.path.getctime(newest_file)
            if time.time() - file_creation_time < 10:  # File created in last 10 seconds
                if file_name.startswith("brainly.com"):
                    print("❌ Download failed: Captcha detected or page not loaded properly")
                    return False
                else:
                    print(f"✅ Download successful! File saved as: {file_name}")
                    return True
                
        time.sleep(0.5)  # Check every half second
    
    print("❌ Timeout: No download detected")
    return False

def scrape_brainly(url):
    """Main scraping function - simply open URL and wait for download."""
    global active_driver
    driver = setup_driver()
    download_success = False
    
    try:
        # Navigate to Brainly URL
        print(f"Opening {url}...")
        driver.get(url)
        
        # Wait for download
        download_success = check_download_success(driver)
        
        if download_success:
            print("✅ Download verified.")
        else:
            print("❌ Download verification failed.")
        
        driver.quit()
        active_driver = None
        print("✅ Browser closed. Expert answer automation complete!")
        return download_success
        
    except Exception as e:
        print(f"Error in scraping process: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        active_driver = None
        return False

if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"
    success = scrape_brainly(test_url)
    print(f"Download success: {success}")