# Ended up just using inspect eleement and getting the parameters manually.
# Also downloaded the HTML to get the valid link.
# Now using this info, we can properly form the payload/parameters/headers to send to Capsolver API to get the token.
# Thus, this code is now scraped.

import time
import os
import requests
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

def wait_for_vpn_connection(driver, timeout=30):
    """Wait for VPN to connect by detecting network changes."""
    print("Checking for VPN connection...")
    
    # Load Firefox internal page (won't trigger Save Page WE)
    driver.get("chrome://browser/content/browser.xhtml")
    time.sleep(2)  # Give Surfshark time to initialize
    
    # Simpler connection check script
    check_connection_script = """
        var callback = arguments[arguments.length - 1];
        try {
            var connection = navigator.connection || navigator.mozConnection;
            callback({
                rtt: connection ? connection.rtt : null,
                downlink: connection ? connection.downlink : null,
                timestamp: Date.now()
            });
        } catch(e) {
            callback(null);
        }
    """
    
    try:
        # Get initial state
        initial_state = driver.execute_async_script(check_connection_script)
        print(f"Initial network state detected")
        
        # Wait for connection changes
        print("Waiting for VPN connection...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_state = driver.execute_async_script(check_connection_script)
            
            if current_state and initial_state:
                if (current_state['rtt'] != initial_state['rtt'] or 
                    current_state['downlink'] != initial_state['downlink']):
                    print("Network change detected - VPN connected!")
                    return True
            
            time.sleep(0.5)  # Check every half second
        
        print("Warning: VPN connection not detected within timeout period")
        return False
        
    except Exception as e:
        print(f"Error in VPN detection: {e}")
        return False

def scrape_brainly(url, wait_time=10):
    driver = setup_driver()
    
    # Small initial delay for Firefox to fully initialize
    time.sleep(1)
    
    # Wait for VPN connection
    if wait_for_vpn_connection(driver):
        # Continue with original scraping
        driver.get(url)
        print(f"✅ Opened {url}, waiting {wait_time} seconds for auto-save...")
        time.sleep(wait_time)
        
        print("✅ Auto-save should have triggered. Waiting for browser to close...")
        driver.quit()
        print("✅ Browser closed. Automation complete!")
    else:
        print("❌ Failed to detect VPN connection. Aborting...")
        driver.quit()

if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"
    scrape_brainly(test_url)