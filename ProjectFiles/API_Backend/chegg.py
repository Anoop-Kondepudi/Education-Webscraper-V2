import time
import os
import tempfile
from datetime import datetime
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

class HeadersManager:
    """Class to manage different sets of headers for different browsing stages"""
    
    @staticmethod
    def get_common_headers():
        """Common headers used in all requests"""
        return {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "accept-language": "en-US,en;q=0.9",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "priority": "u=0, i"
        }
    
    @staticmethod
    def get_question_page_headers(referrer):
        """Headers specific to viewing a question page"""
        headers = HeadersManager.get_common_headers()
        headers.update({
            "sec-fetch-site": "same-origin",
            "referer": referrer
        })
        return headers

class CheggScraper:
    def __init__(self, proxy_enabled=True):
        # Chrome user data directory (for persistent sessions)
        self.user_data_dir = os.path.join(os.path.expanduser("~"), ".chegg_scraper_profile")
        
        # Proxy details
        self.proxy_host = "144.229.117.13"
        self.proxy_port = "8080"
        self.proxy_user = "lho7SIZFaRh9"
        self.proxy_pass = "1inYc0RRMvYs"
        self.proxy_enabled = proxy_enabled
        self.driver = None
        
        # Download directory
        self.download_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        # Create profile directory if it doesn't exist
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
    
    def apply_headers(self, headers):
        """Apply headers using Chrome DevTools Protocol"""
        try:
            # Remove User-Agent as it's already set via options
            if 'user-agent' in headers:
                del headers['user-agent']
            
            # Convert all header keys to proper case (important for CDP)
            proper_headers = {}
            for key, value in headers.items():
                # Convert header names to Title-Case format expected by CDP
                proper_key = '-'.join(word.capitalize() for word in key.split('-'))
                proper_headers[proper_key] = value
            
            # Use CDP to set extra headers
            self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': proper_headers})
            print("Applied realistic browser headers")
            return True
        except Exception as e:
            print(f"Error applying headers: {e}")
            return False
    
    def disable_javascript(self):
        """Disable JavaScript execution in the browser"""
        try:
            self.driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': True})
            print("JavaScript disabled")
            return True
        except Exception as e:
            print(f"Failed to disable JavaScript: {e}")
            return False
    
    def enable_javascript(self):
        """Enable JavaScript execution in the browser"""
        try:
            self.driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': False})
            print("JavaScript enabled")
            return True
        except Exception as e:
            print(f"Failed to enable JavaScript: {e}")
            return False
    
    def wait_for_page_load(self, timeout=30):
        """Wait for page to load using document.readyState"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            print("⚠️ Page load timed out")
            return False
    
    def wait_for_element_visibility(self, locator, timeout=10):
        """Wait for an element to be visible on the page"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            return None
            
    def is_captcha_page(self):
        """Dynamically detect if we're on a captcha page using multiple methods"""
        # Method 1: Check page title
        if "Access to this page has been denied" in self.driver.title:
            print("🔍 Captcha detected (page title)")
            return True
            
        # Method 2: Check for specific captcha elements
        captcha_indicators = [
            # Class-based detection
            "//div[contains(@class, 'px-captcha-message')]",
            "//div[contains(@class, 'px-captcha-container')]",
            "//div[@id='px-captcha']",
            "//div[@id='px-captcha-wrapper']",
            
            # Text-based detection
            "//div[contains(text(), 'Press & Hold to confirm')]",
            "//p[contains(text(), 'Press & Hold to confirm')]",
            "//button[contains(text(), 'Press & Hold')]",
            
            # The specific path you mentioned
            "/html/body/div/div/div[2]/div[2]/p",
            
            # Reference ID indication
            "//div[contains(@class, 'px-captcha-refid')]",
            "//div[contains(text(), 'Reference ID')]"
        ]
        
        for xpath in captcha_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements and any(el.is_displayed() for el in elements):
                    print(f"🔍 Captcha detected (element: {xpath})")
                    return True
            except:
                pass
        
        # Method 3: Check for keyword in page source
        if "px-captcha" in self.driver.page_source or "Press & Hold" in self.driver.page_source:
            print("🔍 Captcha detected (page source)")
            return True
            
        # Method 4: Check for captcha iframe
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                if "captcha" in iframe.get_attribute("src").lower() or "captcha" in iframe.get_attribute("title").lower():
                    print("🔍 Captcha detected (iframe)")
                    return True
        except:
            pass
            
        return False
    
    def is_question_page(self):
        """Check if we're on an actual Chegg question page"""
        question_indicators = [
            "//div[contains(@class, 'question-body')]",
            "//div[contains(@class, 'answer-body')]",
            "//div[contains(@class, 'solution')]",
            "//div[@id='sendToExpertButton']",
            "//span[contains(text(), 'Question')]",
            "//span[contains(text(), 'Answer')]"
        ]
        
        for xpath in question_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements and any(el.is_displayed() for el in elements):
                    print(f"✅ Question page detected (element: {xpath})")
                    return True
            except:
                pass
                
        return False
    
    def wait_for_captcha_to_load(self, max_wait_time=15):
        """Wait for the captcha to fully load"""
        print(f"⏳ Waiting up to {max_wait_time} seconds for captcha to fully load...")
        
        # First confirm it's a captcha page
        if not self.is_captcha_page():
            print("Not a captcha page")
            return False
            
        start_time = time.time()
        captcha_ready = False
        
        # Try to find the captcha button with different strategies
        button_selectors = [
            (By.XPATH, "//div[contains(@class, 'px-captcha-error-button')]"),
            (By.XPATH, "//button[contains(text(), 'Press & Hold')]"),
            (By.XPATH, "//div[text()='Press & Hold']"),
            (By.XPATH, "/html/body/div/div/div[2]/div[2]/p"),
            (By.CSS_SELECTOR, ".px-captcha-button"),
            (By.CSS_SELECTOR, "#px-captcha div")
        ]
        
        while time.time() - start_time < max_wait_time and not captcha_ready:
            # Take a screenshot to see what's happening
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.download_dir, f"captcha_loading_{timestamp}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Waiting for captcha - screenshot: {screenshot_path}")
            except:
                pass
                
            # Try all button selectors
            for selector in button_selectors:
                try:
                    elements = self.driver.find_elements(*selector)
                    for element in elements:
                        if element.is_displayed():
                            print(f"✅ Captcha appears to be fully loaded (found: {selector})")
                            return True
                except:
                    pass
                    
            # Also check for specific keywords in the buttons or interactive elements
            try:
                interactive_elements = self.driver.find_elements(By.TAG_NAME, "button") + \
                                       self.driver.find_elements(By.TAG_NAME, "div")
                                       
                for element in interactive_elements:
                    try:
                        if "Press & Hold" in element.text and element.is_displayed():
                            print(f"✅ Found captcha button with text: 'Press & Hold'")
                            return True
                    except:
                        pass
            except:
                pass
                
            # Check if scripts have finished loading
            try:
                script_loaded = self.driver.execute_script(
                    "return document.readyState === 'complete' && !!document.querySelector('#px-captcha') && window._pxVid"
                )
                if script_loaded:
                    print("✅ Captcha scripts appear to be fully loaded")
                    return True
            except:
                pass
                
            # Small delay before next check
            time.sleep(0.5)
            
        print("⚠️ Timed out waiting for captcha to fully load")
        return False
    
    def find_captcha_button(self):
        """Find the Press & Hold captcha button using multiple selectors"""
        captcha_button_selectors = [
            # Main button element
            "//button[contains(@class, 'px-captcha-button')]",
            "//button[contains(text(), 'Press & Hold')]",
            "//div[@class='px-captcha-error-button']",
            "//div[contains(@class, 'px-captcha-error-button')]",
            "//div[text()='Press & Hold']",
            
            # The container element
            "//div[@id='px-captcha']//button",
            "//div[@id='px-captcha']/div",
            
            # Generic based on the iframe's container
            "//iframe[@title='Human verification challenge']/parent::div",
            
            # Very specific path from HTML
            "/html/body/div/div/div[2]/div[2]/p",
            
            # Parent of the path you provided
            "/html/body/div/div/div[2]/div[2]"
        ]
        
        for selector in captcha_button_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for el in elements:
                    if el.is_displayed():
                        print(f"✅ Found captcha button using selector: {selector}")
                        return el
            except:
                continue
                
        # If we can't find with XPath, try CSS selectors
        css_selectors = [
            ".px-captcha-button", 
            "button.press-hold", 
            "[aria-label*='hold']",
            ".px-captcha-error-button",
            "#px-captcha div",
            "#px-captcha button"
        ]
        
        for selector in css_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed():
                        print(f"✅ Found captcha button using CSS: {selector}")
                        return el
            except:
                continue
                
        # Last resort: try to find a clickable div or button that might be the captcha
        try:
            # Search for elements containing the text
            elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Press & Hold')]")
            for el in elements:
                if el.is_displayed() and (el.tag_name == 'button' or el.tag_name == 'div'):
                    print(f"✅ Found captcha button by text content")
                    return el
                
                # If the element itself isn't clickable, try its parent
                parent = el.find_element(By.XPATH, "./..")
                if parent and (parent.tag_name == 'button' or parent.tag_name == 'div'):
                    print(f"✅ Found captcha button parent")
                    return parent
        except:
            pass
        
        # If we still can't find anything specific, try to click where the button should be
        try:
            # Try to find by text content, even if it's not a button
            el = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Press & Hold')]")
            if el.is_displayed():
                print("⚠️ Found text element for captcha, will try to click")
                return el
        except:
            pass
                
        return None
    
    def solve_press_and_hold_captcha(self, max_attempts=3, retry_delay=1):
        """Solve the 'Press & Hold' captcha by pressing and holding the button"""
        print("🔎 Attempting to solve captcha...")
        
        # First, ensure captcha is fully loaded
        captcha_loaded = self.wait_for_captcha_to_load(max_wait_time=10)
        if not captcha_loaded:
            print("⚠️ Captcha never fully loaded")
            return False
        
        for attempt in range(max_attempts):
            try:
                print(f"Attempt {attempt+1}/{max_attempts}...")
                
                # Find the captcha button
                captcha_button = self.find_captcha_button()
                
                if not captcha_button:
                    print("⚠️ Could not find captcha button, will retry")
                    # If we can't find the button, take a screenshot for debugging
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = os.path.join(self.download_dir, f"captcha_debug_{timestamp}.png")
                        self.driver.save_screenshot(screenshot_path)
                        print(f"📸 Saved debug screenshot to: {screenshot_path}")
                        
                        # Also save the HTML
                        html_path = os.path.join(self.download_dir, f"captcha_debug_{timestamp}.html")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                        print(f"💾 Saved debug HTML to: {html_path}")
                    except:
                        pass
                        
                    time.sleep(2)  # Wait a bit longer before retrying
                    continue
                
                # Create action chain for pressing and holding
                print(f"📌 Clicking and holding captcha button...")
                actions = ActionChains(self.driver)
                
                # Move to the element and position near its center
                actions.move_to_element(captcha_button)
                
                # Click and hold
                actions.click_and_hold()
                actions.perform()
                
                # Hold for a few seconds (4-5 seconds is typically enough)
                hold_time = 5  # seconds
                print(f"⏳ Holding for {hold_time} seconds...")
                time.sleep(hold_time)
                
                # Release
                actions.release()
                actions.perform()
                
                # Wait a moment to see the result
                print("🔍 Checking if captcha was solved...")
                time.sleep(2)
                
                # Check if we're still on a captcha page
                if not self.is_captcha_page():
                    print("✅ Captcha solved successfully!")
                    return True
                    
                # Fallback: check if we're now on the question page
                if self.is_question_page():
                    print("✅ Captcha solved successfully (detected question page)!")
                    return True
                
                print(f"❌ Captcha not solved on attempt {attempt+1}, trying again...")
                time.sleep(retry_delay)
                
            except Exception as e:
                print(f"⚠️ Error solving captcha: {e}")
                time.sleep(retry_delay)
        
        print("❌ Failed to solve captcha after multiple attempts")
        return False
    
    def check_for_button(self):
        """Check if the 'Send to Expert' button exists"""
        try:
            button = self.driver.find_element(By.XPATH, '//*[@id="sendToExpertButton"]')
            return button.is_displayed()
        except:
            return False
    
    def poll_for_button(self, max_attempts=60, interval=0.5):
        """Poll for the button existence with a timeout"""
        print("🔍 Polling for 'Send to Expert' button...")
        
        for attempt in range(max_attempts):
            # First check if we're on a captcha page
            if self.is_captcha_page():
                print("🔒 Captcha detected during polling, attempting to solve...")
                if self.solve_press_and_hold_captcha():
                    print("✅ Captcha solved, continuing to look for button")
                else:
                    print("⚠️ Failed to solve captcha, but continuing to look for button")
            
            # Check for the target button
            if self.check_for_button():
                print("✅ Found 'Send to Expert' button!")
                return True
                
            time.sleep(interval)
        
        print("⚠️ 'Send to Expert' button not found after polling")
        return False
    
    def save_html(self, url, success=True):
        """Save the current page HTML to a file"""
        # Disable JavaScript and get static HTML
        print("📥 Capturing static HTML...")
        self.disable_javascript()
        time.sleep(0.5)  # Brief pause to let JS disable take effect
        
        # Get the raw page source
        html_content = self.driver.page_source
        
        # Generate a filename with the question ID if available
        question_id = "unknown"
        if "q" in url.split("-")[-1]:
            question_id = url.split("-")[-1]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "success" if success else "failed"
        filename = f"chegg_question_{question_id}_{timestamp}_{status}_static.html"
        filepath = os.path.join(self.download_dir, filename)
        
        # Save the raw HTML to a file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"💾 Static HTML saved to: {filepath}")
        
        # Re-enable JavaScript so user can interact with the page
        self.enable_javascript()
        
        return filepath
    
    def download_html(self, url):
        """Download the static HTML content of a Chegg question page with button detection"""
        try:
            # Initialize Chrome with undetected-chromedriver
            print("🌐 Setting up undetected Chrome...")
            options = uc.ChromeOptions()
            
            # Basic browser setup
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            
            # Set up proxy if enabled
            if self.proxy_enabled:
                print(f"🔒 Setting up proxy: {self.proxy_host}:{self.proxy_port}")
                options.add_argument(f'--proxy-server=http://{self.proxy_host}:{self.proxy_port}')
            
            # Get common headers to use for User-Agent
            headers = HeadersManager.get_common_headers()
            options.add_argument(f"--user-agent={headers['user-agent']}")
            
            # Fix SSL issues
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Initialize the driver
            print("🚀 Starting browser...")
            self.driver = uc.Chrome(
                options=options,
                user_data_dir=self.user_data_dir,
                use_subprocess=True
            )
            
            # Apply headers using CDP
            print("📝 Applying headers...")
            question_headers = HeadersManager.get_question_page_headers(url)
            self.apply_headers(question_headers)
            
            # Navigate to the URL
            print(f"🌍 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            self.wait_for_page_load()
            
            # Check for captcha after initial page load - if found, solve without refreshing
            if self.is_captcha_page():
                print("🔒 Captcha detected after initial page load")
                if self.solve_press_and_hold_captcha():
                    print("✅ Successfully solved captcha!")
                else:
                    print("⚠️ Failed to solve captcha initially")
                    
                    # Try a refresh if initial attempt failed
                    print("🔄 Refreshing page to try again...")
                    self.driver.refresh()
                    self.wait_for_page_load()
                    
                    # Check for captcha again after refresh
                    if self.is_captcha_page():
                        print("🔒 Captcha detected after page refresh")
                        if not self.solve_press_and_hold_captcha():
                            print("⚠️ Failed to solve captcha after refresh too")
            else:
                # If no captcha initially, it might come after a refresh
                print("🔄 No captcha initially, refreshing page...")
                self.driver.refresh()
                self.wait_for_page_load()
                
                if self.is_captcha_page():
                    print("🔒 Captcha detected after refresh")
                    if not self.solve_press_and_hold_captcha():
                        print("⚠️ Failed to solve captcha")
            
            # Check if we're on the question page
            is_question = self.is_question_page()
            
            # Poll for the button
            button_found = False
            if is_question:
                button_found = self.poll_for_button()
            else:
                # One more check for captcha
                if self.is_captcha_page():
                    print("🔒 Captcha detected during final check")
                    if self.solve_press_and_hold_captcha():
                        # Try polling again after solving
                        button_found = self.poll_for_button()
            
            # Save HTML based on whether button was found
            filepath = self.save_html(url, success=button_found)
            
            # Wait for user to press Enter before closing the browser
            input("\nPress Enter to close the browser...")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            # Close the browser, but only if the try block didn't complete successfully
            if self.driver and sys.exc_info()[0]:
                print("🛑 Closing browser due to error...")
                self.driver.quit()


if __name__ == "__main__":
    # Ask user if they want to use proxy
    use_proxy = input("Use proxy? (y/n): ").lower().strip() == 'y'
    
    # Create scraper with proxy setting
    scraper = CheggScraper(proxy_enabled=use_proxy)
    
    # Get the URL to scrape
    url = input("Enter Chegg question URL: ").strip()
    
    if url:
        # Download static HTML
        scraper.download_html(url)
    else:
        print("No URL provided. Exiting.")