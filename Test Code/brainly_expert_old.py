import time
import os
import glob
import threading
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Use dedicated Brainly automation Firefox profile
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/8wofgziv.brainly-expert"

# Correct path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

def setup_driver():
    """Set up and return Firefox WebDriver."""
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    
    if os.path.exists(FIREFOX_PROFILE_PATH):
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
    else:
        print("Warning: Firefox profile path not found, using default profile")
    
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

def check_download_success(driver, timeout=30):
    """Check if download was successful by monitoring the correct Downloads folder."""
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

def disable_javascript(driver):
    """Disable JavaScript in the browser."""
    try:
        # Execute script to disable all JavaScript functionality
        driver.execute_script("""
            // Disable all event listeners
            var old = Element.prototype.addEventListener;
            Element.prototype.addEventListener = function() {};
            
            // Disable timers
            window.setTimeout = function() {};
            window.setInterval = function() {};
            
            // Disable further script execution
            window.eval = function() {};
            
            // Disable AJAX requests
            XMLHttpRequest.prototype.open = function() {}; 
            XMLHttpRequest.prototype.send = function() {};
            
            // Disable fetch
            window.fetch = function() { return new Promise((resolve, reject) => {}); };
            
            // Prevent further script tags from executing
            document.createElement = function(tag) {
                var element = Object.create(HTMLElement.prototype);
                if (tag.toLowerCase() === 'script') {
                    // Return a dummy script element that does nothing
                    element.src = '';
                    element.type = 'text/plain';
                }
                return element;
            };
            
            console.log('JavaScript functionality disabled via script injection');
        """)
        print("✅ JavaScript functionality disabled via script injection")
        return True
    except Exception as e:
        print(f"Error disabling JavaScript: {e}")
        return False

def answer_switch_monitor(driver, stop_event):
    """Constantly monitor and click the answer-switch when it appears."""
    selectors_to_try = [
        "#answer-switch",       # Primary selector
        ".answer-switch",       # Class variant
        "[data-testid='answer-switch']",  # Test ID variant
        "[id*='answer-switch']",  # Partial ID match
        "[class*='answer-switch']",  # Partial class match
        "#main-content > div > div:nth-child(2) > section > div > div > div"  # From user's description
    ]
    
    for selector in selectors_to_try:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            print(f"✅ Clicked element with selector: {selector}")
            
            # Immediately disable JavaScript after clicking
            disable_javascript(driver)
            
            # Signal that we've performed the operation
            stop_event.set()
            return
        except NoSuchElementException:
            continue  # Try next selector
        except Exception as e:
            print(f"Error while trying to click {selector}: {e}")
            continue
    
    # If we get here, we didn't find any of the selectors this time
    time.sleep(0.05)  # Very small sleep to prevent CPU hammering

def scrape_brainly(url):
    """Main scraping function with constant checking for answer-switch."""
    driver = setup_driver()
    
    try:
        # Navigate directly to Brainly URL
        driver.get(url)
        print(f"✅ Opened {url}, searching for answer switch...")
        
        # Start a thread to constantly check for the element
        stop_event = threading.Event()
        
        # Set up a loop to keep checking until either:
        # 1. We find and click the element
        # 2. A download happens
        # 3. We hit a timeout
        timeout = 30  # seconds
        start_time = time.time()
        
        while not stop_event.is_set() and time.time() - start_time < timeout:
            # Run the monitor function directly in main thread since we need to navigate away
            answer_switch_monitor(driver, stop_event)
            if stop_event.is_set():
                print("✅ Found and clicked element, disabled JavaScript")
                break
        
        # Check if download was successful
        download_success = check_download_success(driver)
        
        if download_success:
            print("✅ Download verified. Closing browser...")
        else:
            print("❌ Download verification failed. Possible captcha or error.")
        
        driver.quit()
        print("✅ Browser closed. Expert answer automation complete!")
        
    except Exception as e:
        print(f"Error in scraping process: {e}")
        driver.quit()

if __name__ == "__main__":
    # When running directly, use this test URL
    test_url = "https://brainly.com/question/48003838"
    scrape_brainly(test_url)