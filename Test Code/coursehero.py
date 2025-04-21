import asyncio
import os
import re
import json
from rnet import Impersonate, Client
from datetime import datetime

async def get_coursehero_cookies_and_save_html():
    """
    Function to get cookies from the Course Hero login page and save the HTML content.
    """
    # URL for the Course Hero login page
    url = "https://www.coursehero.com/login/?login_user_type=&ref=login"
    
    try:
        # Create a client with Firefox impersonation
        client = Client(impersonate=Impersonate.Firefox136)
        
        # Add debugging info
        print(f"Sending request to {url}")
        
        # Make a GET request to the URL
        response = await client.get(url)
        
        # Debug response information
        print(f"Response received. Status code: {response.status_code}")
        
        # Save the HTML content regardless of status code
        try:
            # Get HTML content
            html_content = await response.text()
            
            # Create a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coursehero_login_{timestamp}.html"
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            
            # Save HTML to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"HTML content saved to: {filepath}")
            
            # Process cookie information
            cookie_dict = {}
            try:
                cookies = response.cookies
                print("\nCookies information:")
                for cookie in cookies:
                    if hasattr(cookie, 'name') and hasattr(cookie, 'value'):
                        print(f"  - {cookie}")
                        cookie_dict[cookie.name] = cookie.value
                
                # Save cookies to a file for future use
                cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coursehero_cookies.json")
                with open(cookies_file, "w") as f:
                    json.dump(cookie_dict, f, indent=2)
                print(f"Cookies saved to: {cookies_file}")
                
            except Exception as cookie_err:
                print(f"Error processing cookies: {cookie_err}")
                import traceback
                traceback.print_exc()
            
            return response, cookie_dict, filepath
            
        except Exception as html_err:
            print(f"Error saving HTML: {html_err}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    except Exception as e:
        print(f"An error occurred during request: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

async def login_to_coursehero(email, password, initial_response=None):
    """
    Function to log into Course Hero using the provided credentials.
    """
    login_url = "https://www.coursehero.com/login/?login_user_type=&ref=login"
    api_login_url = "https://www.coursehero.com/api/v1/login/"
    
    try:
        # Create a client with Firefox impersonation
        client = Client(impersonate=Impersonate.Firefox136)
        
        # If no initial response was provided, get the login page first
        if not initial_response:
            print("Getting initial login page...")
            initial_response = await client.get(login_url)
            if initial_response.status_code != 200:
                print(f"Failed to get login page. Status code: {initial_response.status_code}")
                return None
        
        # Extract the login HTML to look for recaptcha and other needed info
        login_html = await initial_response.text()
        
        # Look for recaptcha site key
        recaptcha_site_key = None
        site_key_match = re.search(r'data-sitekey=["\'](.*?)["\']', login_html)
        if site_key_match:
            recaptcha_site_key = site_key_match.group(1)
            print(f"Found reCAPTCHA site key: {recaptcha_site_key}")
        
        # Look for any CSRF token
        csrf_token = None
        csrf_match = re.search(r'name="csrf_token".*?value=["\'](.*?)["\']', login_html)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"Found CSRF token: {csrf_token}")
            
        # Print a message about recaptcha
        print("\n===== IMPORTANT RECAPTCHA NOTICE =====")
        print("CourseHero likely uses reCAPTCHA for login protection.")
        print("To properly handle this, you would need to:")
        print("1. Use a captcha solving service")
        print("2. Manually solve the captcha in a browser and capture the token")
        print("3. Use browser automation to handle the full login flow")
        print("This simple script cannot automatically bypass the reCAPTCHA.")
        print("=====================================\n")
            
        # Create the login data
        login_data = {
            "email": email,
            "password": password,
            "remember_me": "1",
            "submit": "true"
        }
        
        if csrf_token:
            login_data["csrf_token"] = csrf_token
            
        # You need to manually add a valid recaptcha response token
        # This is just a placeholder - it won't work
        login_data["g-recaptcha-response"] = "REPLACE_WITH_VALID_RECAPTCHA_TOKEN"
        
        # Set up headers for the login request
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": login_url,
            "Origin": "https://www.coursehero.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Connection": "keep-alive"
        }
        
        # Print the prepared login data (excluding password)
        safe_login_data = login_data.copy()
        safe_login_data["password"] = "********"
        print(f"Prepared login data: {safe_login_data}")
        
        print("\nNOTE: This demo won't actually submit the login because:")
        print("1. We need a valid recaptcha token")
        print("2. The password is just a placeholder")
        print("To actually log in, you'd need to:")
        print("- Replace the recaptcha token with a valid one")
        print("- Use your actual email and password")
        print("- Uncomment the client.post call below")
        
        # Uncomment this to actually try the login
        # Note: Will likely fail without a valid recaptcha token
        """
        print("Attempting to log in...")
        login_resp = await client.post(api_login_url, data=login_data, headers=headers)
        
        # Check the response
        print(f"Login response status code: {login_resp.status_code}")
        
        # Save the response content
        login_resp_content = await login_resp.text()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        login_resp_file = f"coursehero_login_response_{timestamp}.json"
        login_resp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), login_resp_file)
        
        with open(login_resp_path, "w", encoding="utf-8") as f:
            f.write(login_resp_content)
        
        print(f"Login response saved to: {login_resp_path}")
        
        # Get cookies after login
        login_cookies = login_resp.cookies
        
        return login_resp
        """
        
        return None  # Return None for now since we're not actually logging in
    
    except Exception as e:
        print(f"Login preparation error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    # Call the function to get the cookies and save HTML
    response, cookies_dict, filepath = await get_coursehero_cookies_and_save_html()
    
    if filepath:
        print(f"\nHTML file was successfully saved to: {filepath}")
    else:
        print("\nFailed to save HTML file.")
    
    if cookies_dict:
        print("\nCookies retrieved and ready for use in subsequent requests.")
        print(f"Found {len(cookies_dict)} cookies.")
        
    # Demo login preparation with placeholder credentials
    # NOTE: This won't actually log in due to recaptcha
    email = "example@email.com"  # Replace with your email
    password = "password123"     # Replace with your password
    await login_to_coursehero(email, password, response)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
