import json
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

def save_auth_data(driver, filename):
    """Save authentication data including JWT token"""
    auth_data = {}
    
    # Get cookies
    cookies = driver.get_cookies()
    auth_data['cookies'] = cookies
    
    # Get localStorage
    local_storage = driver.execute_script(
        "var ls = {}; for (var i = 0; i < localStorage.length; i++) { "
        "var key = localStorage.key(i); ls[key] = localStorage.getItem(key); } return ls;")
    auth_data['localStorage'] = local_storage
    
    # Get sessionStorage
    session_storage = driver.execute_script(
        "var ss = {}; for (var i = 0; i < sessionStorage.length; i++) { "
        "var key = sessionStorage.key(i); ss[key] = sessionStorage.getItem(key); } return ss;")
    auth_data['sessionStorage'] = session_storage
    
    # Extract JWT token from page
    jwt_token = driver.execute_script("""
    // Look for JWT tokens in various places
    function findJwtToken() {
      // Pattern to match JWT tokens
      const jwtPattern = /eyJ[a-zA-Z0-9_-]+\\.[a-zA-Z0-9_-]+\\.[a-zA-Z0-9_-]+/;
      
      // Check localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        const match = value.match(jwtPattern);
        if (match) return match[0];
      }
      
      // Check sessionStorage
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        const value = sessionStorage.getItem(key);
        const match = value.match(jwtPattern);
        if (match) return match[0];
      }
      
      return null;
    }
    
    return findJwtToken();
    """)
    
    if jwt_token:
        auth_data['jwt_token'] = jwt_token
        print(f"Found JWT token: {jwt_token}")
        print("\nFULL TOKEN (copy this for hardcoding if needed):")
        print("="*80)
        print(jwt_token)
        print("="*80)
    
    # Save to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save data with pretty printing
    with open(filename, 'w') as f:
        json.dump(auth_data, f, indent=4)
    
    # Verify file was saved properly
    try:
        with open(filename, 'r') as f:
            saved_data = json.load(f)
        
        if saved_data.get('jwt_token') == jwt_token:
            print(f"Authentication data successfully saved to {filename}")
        else:
            print(f"WARNING: JWT token may not have been saved correctly to {filename}")
            print(f"Writing token to separate file for backup")
            
            # Save token to a separate text file as backup
            token_file = os.path.join(os.path.dirname(filename), "jwt_token.txt")
            with open(token_file, 'w') as tf:
                tf.write(jwt_token)
            print(f"Token backed up to {token_file}")
    except Exception as e:
        print(f"Error verifying saved file: {e}")
    
    return auth_data

def load_auth_data(filename):
    """Load authentication data from file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}. File may be empty or corrupted.")
        return None

def apply_auth_data(driver, auth_data):
    """Apply saved authentication data to browser session"""
    # Apply cookies
    for cookie in auth_data.get('cookies', []):
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Error adding cookie: {e}")
    
    # Apply localStorage
    for key, value in auth_data.get('localStorage', {}).items():
        try:
            driver.execute_script(f"localStorage.setItem('{key}', arguments[0]);", value)
        except Exception as e:
            print(f"Error setting localStorage item {key}: {e}")
    
    # Apply sessionStorage
    for key, value in auth_data.get('sessionStorage', {}).items():
        try:
            driver.execute_script(f"sessionStorage.setItem('{key}', arguments[0]);", value)
        except Exception as e:
            print(f"Error setting sessionStorage item {key}: {e}")
    
    # Set up token injection if we have a JWT token
    jwt_token = auth_data.get('jwt_token')
    if jwt_token:
        try:
            # Simple script to ensure token is available for XHR requests
            script = """
            // Store token in a variable
            var token = arguments[0];
            
            // Store token in window object
            window.turnitinJWTToken = token;
            
            // Create a function to add token to all API requests
            function addTokenToApiRequests() {
              // Override fetch
              var originalFetch = window.fetch;
              window.fetch = function(url, options) {
                options = options || {};
                options.headers = options.headers || {};
                
                if (url.includes('api.turnitindetect.com')) {
                  options.headers['x-access-token'] = window.turnitinJWTToken;
                }
                
                return originalFetch.call(this, url, options);
              };
              
              // Override XMLHttpRequest
              var originalOpen = XMLHttpRequest.prototype.open;
              XMLHttpRequest.prototype.open = function() {
                this._url = arguments[1];
                originalOpen.apply(this, arguments);
              };
              
              var originalSend = XMLHttpRequest.prototype.send;
              XMLHttpRequest.prototype.send = function() {
                if (this._url && this._url.includes('api.turnitindetect.com')) {
                  this.setRequestHeader('x-access-token', window.turnitinJWTToken);
                }
                originalSend.apply(this, arguments);
              };
              
              console.log('Token injection for API requests is active');
            }
            
            // Run the function
            addTokenToApiRequests();
            """
            driver.execute_script(script, jwt_token)
            print("Successfully injected JWT token into page")
        except Exception as e:
            print(f"Error injecting JWT token: {e}")
    
    # Refresh the page to apply changes
    driver.refresh()

def auto_login_with_token():
    # Your JWT token (expires 1742239512 - about a year from now)
    JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTY5MThmZWUtOWQ0NC00NGE2LTlkM2QtZGViOTUyOGUxODdjIiwiZXhwIjoxNzQyMjM5NTEyfQ.a2icuz4Tbzq-gGlL70Cw9EK-KtIgiuDikQ10qpCtJlY"
    
    # Setup Firefox with profile
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/q4q811t1.turnitin"
    options = Options()
    options.profile = firefox_profile_path
    
    # Initialize the driver
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )
    
    try:
        # First navigate to the site's domain to set up JavaScript environment
        print("Navigating to turnitindetect.com...")
        driver.get("https://turnitindetect.com")
        
        # Wait for page to load
        time.sleep(2)
        
        # Inject the JWT token and set up request interceptors
        print("Injecting authentication token...")
        token_injection_script = """
        // Store the JWT token
        window.turnitinJWTToken = arguments[0];
        console.log("Token stored:", window.turnitinJWTToken);
        
        // Store token in localStorage (may help with persistence)
        localStorage.setItem('turnitinToken', window.turnitinJWTToken);
        
        // Override fetch to include token in API requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            options = options || {};
            options.headers = options.headers || {};
            
            if (url && url.includes('api.turnitindetect.com')) {
                console.log("Adding token to fetch request:", url);
                options.headers['x-access-token'] = window.turnitinJWTToken;
            }
            
            return originalFetch.call(this, url, options);
        };
        
        // Override XMLHttpRequest to include token
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function() {
            this._url = arguments[1];
            originalOpen.apply(this, arguments);
        };
        
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            if (this._url && this._url.includes('api.turnitindetect.com')) {
                console.log("Adding token to XHR request:", this._url);
                this.setRequestHeader('x-access-token', window.turnitinJWTToken);
            }
            originalSend.apply(this, arguments);
        };
        
        console.log("Request interceptors installed successfully");
        
        // Return true to confirm script execution
        return true;
        """
        result = driver.execute_script(token_injection_script, JWT_TOKEN)
        print(f"Token injection result: {result}")
        
        # Directly navigate to dashboard after token injection
        print("Navigating to dashboard...")
        driver.get("https://turnitindetect.com/dashboard")
        
        # Wait for the dashboard to load (looking for typical elements)
        print("Waiting for dashboard to load...")
        wait = WebDriverWait(driver, 10)
        
        try:
            # Wait for a dashboard indicator (adjust selector as needed)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dashboard, .dashboard-container, h1")))
            page_title = driver.title
            page_text = driver.execute_script("return document.body.textContent")
            
            # Check if we're successfully logged in
            if "dashboard" in page_text.lower() or "welcome" in page_text.lower():
                print("Successfully logged in! Dashboard loaded.")
            else:
                print("Page loaded, but might not be logged in. Current page:", page_title)
                # Try direct API call to validate token
                validate_script = """
                // Check if token is valid via API call
                async function validateToken() {
                    try {
                        const response = await fetch('https://api.turnitindetect.com/validate-token', {
                            method: 'GET',
                            headers: {
                                'x-access-token': window.turnitinJWTToken
                            }
                        });
                        const data = await response.json();
                        return data;
                    } catch (error) {
                        return {error: error.message};
                    }
                }
                return validateToken();
                """
                validation = driver.execute_script(validate_script)
                print(f"Token validation result: {validation}")
        except Exception as e:
            print(f"Error waiting for dashboard: {e}")
            print("Might not be logged in. Check the browser window.")
        
        # Keep browser open until user closes it
        print("\nAuto-login process complete.")
        print("Browser will remain open - you can continue using it.")
        print("Press Ctrl+C in the terminal to close the script when you're done.")
        
        # Wait indefinitely (until user interrupts)
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nUser interrupted. Closing browser...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up if needed
        driver.quit()

if __name__ == "__main__":
    auto_login_with_token()