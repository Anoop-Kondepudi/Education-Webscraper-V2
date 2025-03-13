import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Use dedicated Brainly automation Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

# Correct path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

def setup_driver():
    """Set up and return Firefox WebDriver."""
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run in headless mode
    options.add_argument("--headless")
    
    # Create Firefox profile first
    profile = webdriver.FirefoxProfile()
    
    if os.path.exists(FIREFOX_PROFILE_PATH):
        # Use existing profile path
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
    else:
        print("Warning: Firefox profile path not found, using default profile")
        options.profile = profile
    
    # Disable JavaScript
    profile.set_preference("javascript.enabled", False)
    print("✅ JavaScript disabled")
    
    # Prevent download cancel confirmation dialog
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("browser.tabs.warnOnClose", False)
    profile.set_preference("browser.tabs.warnOnCloseOtherTabs", False)
    profile.set_preference("dom.disable_beforeunload", True)
    
    # Additional preferences for headless downloads
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", DOWNLOADS_PATH)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/html")
    print("✅ Download dialogs disabled")
    
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

def check_for_expert_answer(driver):
    """Check if the page has an expert answer section"""
    expert_answer_exists = False
    page_html = driver.page_source
    
    try:
        # Check for the specific element structure first (fastest)
        if '>Community<' in page_html and '>Expert<' in page_html:
            expert_answer_exists = True
            print("✅ Expert answer detected via text content inspection")
            return expert_answer_exists
            
        # Then check for answer switch elements
        if "#answer-switch" in page_html or "answer-switch" in page_html:
            expert_answer_exists = True
            print("✅ Expert answer detected via HTML inspection")
            return expert_answer_exists
            
        # If HTML inspection doesn't work, try using direct selectors (though less reliable with JS disabled)
        try:
            # Try a few selectors that might indicate an expert answer
            selectors = [
                "#answer-switch",
                ".answer-switch",
                "[data-testid='answer-switch']",
                "#main-content > div > div:nth-child(2) > section > div > div > div"
            ]
            
            for selector in selectors:
                try:
                    driver.find_element(By.CSS_SELECTOR, selector)
                    expert_answer_exists = True
                    print(f"✅ Expert answer detected via selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
        except:
            # If selenium can't find elements (JS disabled may affect this), 
            # we'll rely on the HTML inspection above
            pass
            
        if not expert_answer_exists:
            print("ℹ️ No expert answer detected")
            
        return expert_answer_exists
        
    except Exception as e:
        print(f"Error checking for expert answer: {e}")
        return False

def check_download_success(driver, timeout=30):
    """Check if download was successful by monitoring the correct Downloads folder."""
    # Use the project's Downloaded Files folder
    print(f"Checking for downloads in: {DOWNLOADS_PATH}")
    start_time = time.time()
    
    # Get page title for comparison
    page_title = driver.title.strip()
    print(f"Page title: {page_title}")
    
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
    """Main scraping function - directly open Brainly URL and check download.
    
    Returns:
        tuple: (download_success, expert_answer_exists)
    """
    driver = setup_driver()
    download_success = False
    expert_answer_exists = False
    
    try:
        # Navigate directly to Brainly URL
        driver.get(url)
        print(f"✅ Opened {url}, waiting for download...")
        
        # Check if download was successful
        download_success = check_download_success(driver)
        
        if download_success:
            print("✅ Download verified.")
            
            # Before closing, check if an expert answer exists
            print("🔍 Checking for expert answer...")
            expert_answer_exists = check_for_expert_answer(driver)
        else:
            print("❌ Download verification failed. Possible captcha or error.")
        
        driver.quit()
        print("✅ Browser closed. Community answer automation complete!")
        
        return (download_success, expert_answer_exists)
        
    except Exception as e:
        print(f"Error in scraping process: {e}")
        driver.quit()
        return (False, False)

if __name__ == "__main__":
    # When running directly, use this test URL
    test_url = "https://brainly.com/question/48003838"
    success, has_expert = scrape_brainly(test_url)
    print(f"Download success: {success}, Has expert answer: {has_expert}")