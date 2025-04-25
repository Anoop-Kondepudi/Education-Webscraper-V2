import time
import os
import glob
import atexit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Use dedicated Brainly automation Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

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
            print("✅ Cleaned up community browser instance on exit")
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
    
    active_driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return active_driver

def check_for_expert_answer(driver):
    """Check if the page has an expert answer section"""
    expert_answer_exists = False
    page_html = driver.page_source
    
    try:
        # Check for specific data-testid attributes from the new UI
        data_testid_indicators = [
            'data-testid="multi_answer_tab_expert"',
            'multi_answer_tab_expert'
        ]
        
        for indicator in data_testid_indicators:
            if indicator in page_html:
                expert_answer_exists = True
                print(f"✅ Expert answer detected via data-testid: '{indicator}'")
                return expert_answer_exists
        
        # Check for class patterns that indicate the expert UI components
        class_indicators = [
            'sg-icon--icon-green-60',  # The green checkmark icon next to Brainly
            'sg-button--transparent'   # The tab button styling
        ]
        
        for indicator in class_indicators:
            if indicator in page_html:
                # If we find these classes and also find "Experts" text nearby
                if "by Experts" in page_html or ">by Experts<" in page_html:
                    expert_answer_exists = True
                    print(f"✅ Expert answer detected via class pattern: '{indicator}' with 'by Experts' text")
                    return expert_answer_exists
        
        # Try to find the expert tabs using XPath based on the HTML structure shown
        try:
            # Look for button with multi_answer_tab_expert data-testid
            expert_tab_xpath = '//button[@data-testid="multi_answer_tab_expert"]'
            if driver.find_elements(By.XPATH, expert_tab_xpath):
                expert_answer_exists = True
                print("✅ Expert answer detected via XPath for multi_answer_tab_expert")
                return expert_answer_exists
                
            # Look for the specific div structure shown in the screenshots
            expert_text_xpath = '//div[contains(@class, "sg-text") and contains(text(), "by") and contains(following-sibling::text(), "Experts")]'
            if driver.find_elements(By.XPATH, expert_text_xpath):
                expert_answer_exists = True
                print("✅ Expert answer detected via XPath for 'by Experts' text structure")
                return expert_answer_exists
            
            # Look for the green checkmark icon
            green_icon_xpath = '//div[contains(@class, "sg-icon--icon-green-60")]'
            if driver.find_elements(By.XPATH, green_icon_xpath):
                expert_answer_exists = True
                print("✅ Expert answer detected via XPath for green checkmark icon")
                return expert_answer_exists
        except Exception as selector_error:
            print(f"Warning: Error in selector detection: {selector_error}")
        
        # If we still haven't found anything, look for fragments that might indicate expert answers
        text_fragments = [
            '>Brainly<',
            '>by Experts<',
            'Community</button>',
            'Experts</button>'
        ]
        
        # Check if multiple fragments exist together
        fragments_found = sum(1 for fragment in text_fragments if fragment in page_html)
        if fragments_found >= 2:  # If we find at least 2 fragments
            expert_answer_exists = True
            print(f"✅ Expert answer detected via multiple text fragments ({fragments_found} found)")
            return expert_answer_exists
        
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
    global active_driver
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
        active_driver = None
        print("✅ Browser closed. Community answer automation complete!")
        
        return (download_success, expert_answer_exists)
        
    except Exception as e:
        print(f"Error in scraping process: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        active_driver = None
        return (False, False)

if __name__ == "__main__":
    # When running directly, use this test URL
    test_url = "https://brainly.com/question/48003838"
    success, has_expert = scrape_brainly(test_url)
    print(f"Download success: {success}, Has expert answer: {has_expert}")