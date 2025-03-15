import time
import os
import re
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Path to Firefox profile for Coursehero
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/43gkv1wz.coursehero"

# Path to Downloaded Files folder
DOWNLOADS_PATH = "/Users/anoopkondepudi/Desktop/Education Webscraper V2/Education-Webscraper-V2/ProjectFiles/Downloaded Files"

# Maximum number of refresh attempts
MAX_REFRESH_ATTEMPTS = 3

def setup_driver():
    """Set up Firefox WebDriver with appropriate configurations."""
    options = webdriver.FirefoxOptions()
    
    # Use existing profile if available
    if os.path.exists(FIREFOX_PROFILE_PATH):
        print(f"Using Firefox profile: {FIREFOX_PROFILE_PATH}")
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
    else:
        print("Warning: Firefox profile path not found, using default profile")
    
    # Configure download preferences
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", DOWNLOADS_PATH)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.manager.closeWhenDone", True)
    
    # Create and return the driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

def extract_document_id(url):
    """Extract document ID from a Coursehero URL."""
    pattern = r"\/file\/([^\/]+)\/"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def list_files():
    """Get a list of all files in the download directory."""
    try:
        files = os.listdir(DOWNLOADS_PATH)
        print(f"Files in directory ({len(files)} total):")
        for i, file in enumerate(files):
            print(f"  {i+1}. {file}")
        return set(files)
    except Exception as e:
        print(f"Error listing files: {e}")
        return set()

def is_temporary_file(filename):
    """Check if a file is a temporary download file."""
    temp_patterns = ['.part', '.crdownload', '.download']
    return any(pattern in filename for pattern in temp_patterns)

def is_access_denied(driver):
    """Check if the page shows an access denied error."""
    try:
        # Try the provided XPath
        access_denied_element = driver.find_elements(By.XPATH, "/html/body/div/div[1]/div[1]/div/div[1]")
        if access_denied_element:
            text = access_denied_element[0].text
            if "Access denied" in text:
                print(f"⚠️ Access denied detected: '{text}'")
                return True
                
        # Also check for error text anywhere on the page
        page_source = driver.page_source.lower()
        if "access denied" in page_source or "error 15" in page_source:
            print("⚠️ Access denied text found on page")
            return True
            
        return False
    except Exception as e:
        print(f"Error checking for access denied: {e}")
        return False

def monitor_downloads(initial_files, timeout=60):  # Extended timeout for complete downloads
    """Monitor for new files and return the first completed download."""
    start_time = time.time()
    print(f"Starting file monitoring (timeout: {timeout} seconds)...")
    
    temp_files_detected = set()
    
    while time.time() - start_time < timeout:
        try:
            current_files = set(os.listdir(DOWNLOADS_PATH))
            
            # Check for new temporary files (downloads in progress)
            new_temp_files = {f for f in current_files - initial_files if is_temporary_file(f)}
            for temp_file in new_temp_files - temp_files_detected:
                print(f"🔄 Download in progress: {temp_file}")
                temp_files_detected.add(temp_file)
            
            # Check for new completed files (not temporary and not in initial set)
            new_completed_files = {f for f in current_files - initial_files if not is_temporary_file(f)}
            
            if new_completed_files:
                # Sort by modification time to get the most recent file
                completed_files_with_mtime = []
                for file in new_completed_files:
                    file_path = os.path.join(DOWNLOADS_PATH, file)
                    mtime = os.path.getmtime(file_path)
                    completed_files_with_mtime.append((file, mtime))
                
                # Sort by modification time (newest first)
                completed_files_with_mtime.sort(key=lambda x: x[1], reverse=True)
                newest_file = completed_files_with_mtime[0][0]
                
                print(f"✅ Download completed: {newest_file}")
                return os.path.join(DOWNLOADS_PATH, newest_file)
        except Exception as e:
            print(f"Error during monitoring: {e}")
        
        time.sleep(0.25)
    
    print("⏱️ Monitoring timeout reached. No completed downloads detected.")
    return None

def send_request_with_refresh(driver, url, download_event):
    """Send request with automatic refresh if access denied."""
    try:
        attempts = 0
        while attempts < MAX_REFRESH_ATTEMPTS and not download_event.is_set():
            attempts += 1
            print(f"Thread: Sending request to {url} (attempt {attempts}/{MAX_REFRESH_ATTEMPTS})")
            
            driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            if is_access_denied(driver):
                print(f"🔄 Access denied detected. Refreshing page (attempt {attempts}/{MAX_REFRESH_ATTEMPTS})")
                time.sleep(1)
                continue
            else:
                print("Thread: Request sent successfully (no access denied detected)")
                break
                
        if attempts >= MAX_REFRESH_ATTEMPTS:
            print("❌ Max refresh attempts reached. Still getting access denied.")
    except Exception as e:
        print(f"Thread: Error sending request: {e}")

def scrape_coursehero(url):
    """Access Coursehero content directly and monitor for downloads."""
    print(f"🚀 Starting Coursehero scraper for URL: {url}")
    
    # Extract document ID from URL
    document_id = extract_document_id(url)
    if not document_id:
        print(f"❌ Could not extract document ID from URL: {url}")
        return None, None
    
    print(f"📄 Extracted document ID: {document_id}")
    
    # Ensure download directory exists
    if not os.path.exists(DOWNLOADS_PATH):
        os.makedirs(DOWNLOADS_PATH)
    
    # Check initial files
    print("\n📋 INITIAL FILES:")
    initial_files = list_files()
    
    # Setup driver
    driver = setup_driver()
    
    try:
        # Build download URL
        download_url = f"https://www.coursehero.com/api/v1/documents/unlock-and-download/{document_id}/"
        print(f"\n⬇️ Will send request to: {download_url}")
        
        # Create an event to signal when download is complete
        download_complete = threading.Event()
        
        # Start a thread to send the request (non-blocking)
        request_thread = threading.Thread(
            target=send_request_with_refresh, 
            args=(driver, download_url, download_complete)
        )
        request_thread.daemon = True
        request_thread.start()
        
        # Wait a moment for the request to start
        time.sleep(1)
        print("Main thread continuing with file monitoring...")
        
        # Monitor for downloads
        downloaded_file = monitor_downloads(initial_files)
        
        # Signal that download is complete (to stop refreshing)
        download_complete.set()
        
        # Check final files
        print("\n📋 FINAL FILES:")
        list_files()
        
        if downloaded_file:
            filename = os.path.basename(downloaded_file)
            print(f"\n✅ SUCCESS: File downloaded to: {filename}")
            return downloaded_file, driver
        else:
            print("\n❌ FAILED: No completed download detected after timeout")
            return None, driver
            
    except Exception as e:
        print(f"❌ Main thread error: {e}")
        return None, driver

if __name__ == "__main__":
    # Test the script with a sample URL
    test_url = "https://www.coursehero.com/file/151322757/Unit-B-Module-3-Lesson-4-Assignmentdocxpdf/"
    result, driver = scrape_coursehero(test_url)
    
    if result:
        print(f"🎉 Document downloaded to: {result}")
    else:
        print("⚠️ No document was downloaded")
    
    # Wait for user input before closing the browser
    input("Press Enter to close the browser...")
    driver.quit()
    print("�� Browser closed") 