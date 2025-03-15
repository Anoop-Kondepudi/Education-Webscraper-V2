import time
import os
import tempfile
from selenium import webdriver
import zipfile
import shutil

class CheggScraper:
    def __init__(self):
        # Brave profile path
        self.brave_profile_path = "/Users/anoopkondepudi/Library/Application Support/BraveSoftware/Brave-Browser/Default"
        # Path to Brave browser on macOS
        self.brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        # Proxy details
        self.proxy_host = "144.229.117.13"
        self.proxy_port = "8080"  # Try HTTP port instead of SOCKS5
        self.proxy_user = "lho7SIZFaRh9"
        self.proxy_pass = "1inYc0RRMvYs"
        self.driver = None
    
    def create_proxy_extension(self):
        """Create a Chrome extension to handle proxy authentication"""
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "webRequest",
                "webRequestBlocking",
                "<all_urls>"
            ],
            "background": {"scripts": ["background.js"]},
            "minimum_chrome_version": "76.0.0"
        }
        """
        
        # Configure as HTTP proxy (instead of SOCKS5)
        background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: %s
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """ % (self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass)
        
        # Create a temporary directory for the extension
        temp_dir = tempfile.mkdtemp()
        
        # Write the extension files
        with open(os.path.join(temp_dir, "manifest.json"), "w") as f:
            f.write(manifest_json)
            
        with open(os.path.join(temp_dir, "background.js"), "w") as f:
            f.write(background_js)
            
        # Create a zip file of the extension
        zip_path = os.path.join(tempfile.gettempdir(), "proxy_ext.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write(os.path.join(temp_dir, "manifest.json"), "manifest.json")
            zf.write(os.path.join(temp_dir, "background.js"), "background.js")
        
        return zip_path
    
    def access_question(self, url):
        """Access a Chegg question using Brave browser with HTTP proxy"""
        try:
            print("Setting up Brave with HTTP proxy...")
            options = webdriver.ChromeOptions()
            
            # Use Brave browser
            options.binary_location = self.brave_path
            
            # Use Brave profile
            options.add_argument(f"--user-data-dir={self.brave_profile_path}")
            
            # Anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Add proxy extension
            proxy_extension_path = self.create_proxy_extension()
            print(f"Using proxy extension: {proxy_extension_path}")
            options.add_extension(proxy_extension_path)
            
            # Additional helpful options
            options.add_argument("--no-sandbox")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            
            # Initialize the driver
            print("Starting browser...")
            self.driver = webdriver.Chrome(options=options)
            print("Browser started successfully")
            
            # Apply anti-detection script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Test the connection and proxy
            print("Testing connection with proxy...")
            self.driver.get("http://httpbin.org/ip")
            time.sleep(3)
            print(f"Current IP: {self.driver.page_source}")
            
            # Go directly to the question URL
            print(f"Going to: {url}")
            self.driver.get(url)
            
            # Keep browser open
            input("Press Enter to close the browser...")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    # Test URL
    test_url = "https://www.chegg.com/homework-help/questions-and-answers/question-1-10-points-let-f-x-x2-x-12-x-4-x-3-answer-following-questions-a-find-zeros-f-x--q60268666"
    
    # Create scraper and access question
    scraper = CheggScraper()
    scraper.access_question(test_url)
