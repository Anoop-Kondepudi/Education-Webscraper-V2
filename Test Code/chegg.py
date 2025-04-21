import asyncio
from rnet import Client, Impersonate
import json
import re
import time

async def login_to_chegg(email, password):
    # Create a client with Firefox browser fingerprint
    client = Client(
        impersonate=Impersonate.Firefox136,  # Use Firefox 136 fingerprint
        cookie_store=True,  # Enable cookie storage
        follow_redirects=True,  # Automatically follow redirects
        timeout=30000  # 30 second timeout
    )
    
    print("Step 1: Visiting Chegg homepage to get initial cookies...")
    # First visit the homepage to get initial cookies
    resp = await client.get("https://www.chegg.com/")
    print(f"Homepage status: {resp.status_code}")
    
    print("Step 2: Visiting login page directly...")
    # Visit the login page directly
    login_url = "https://www.chegg.com/auth?action=login"
    login_resp = await client.get(login_url)
    print(f"Login page status: {login_resp.status_code}")
    
    # Get the redirect URL from the response
    redirect_url = login_resp.url
    print(f"Redirected to: {redirect_url}")
    
    # If we're already at the Auth0 identifier page, we can proceed
    if "auth0.identity1.chegg.com/u/login/identifier" in redirect_url:
        print("Successfully redirected to Auth0 identifier page")
        
        # Extract the state parameter from the URL
        state_match = re.search(r'state=([^&]+)', redirect_url)
        if state_match:
            state = state_match.group(1)
            print(f"Found state parameter: {state[:20]}...")
        else:
            print("Could not find state parameter in redirect URL")
            return False, None
    else:
        # If we're not redirected to Auth0, try the direct Auth0 URL
        print("Not redirected to Auth0, trying direct Auth0 URL...")
        
        # Use a direct Auth0 URL with a new state parameter
        # Note: In a real scenario, you'd need to get a valid state parameter
        auth0_url = "https://auth0.identity1.chegg.com/u/login/identifier?state=hKFo2SBSMlVwUTVMd25hUUxkb28wM3doR1RTZ29LM195RW5FOaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIF94Q2NkR2J3a0dGR20yZHk3WE9GMHUwcExmRG1scHo3o2NpZNkgSzZvdXQ3UmFsRW9rSFFDdVJNc0xDMEJud25YN1ZiYzI&ui_locales=en-US"
        
        auth0_resp = await client.get(auth0_url)
        print(f"Direct Auth0 URL status: {auth0_resp.status_code}")
        
        # Extract the state parameter from the URL
        state_match = re.search(r'state=([^&]+)', auth0_url)
        if state_match:
            state = state_match.group(1)
            print(f"Using state parameter from direct URL: {state[:20]}...")
        else:
            print("Could not find state parameter in direct Auth0 URL")
            return False, None
    
    print("Step 3: Submitting username/email...")
    # Submit the username/email
    identifier_url = f"https://auth0.identity1.chegg.com/u/login/identifier?state={state}&ui_locales=en-US"
    identifier_data = {
        "state": state,
        "username": email,
        "action": "default"
    }
    
    identifier_resp = await client.post(
        identifier_url,
        form=[(k, v) for k, v in identifier_data.items()],
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://auth0.identity1.chegg.com",
            "Referer": identifier_url
        }
    )
    
    print(f"Identifier submission status: {identifier_resp.status_code}")
    print(f"Current URL after identifier submission: {identifier_resp.url}")
    
    # Check if we're redirected to the password page
    if "login/password" not in identifier_resp.url:
        print("Not redirected to password page. Identifier submission might have failed.")
        print("Trying direct password URL...")
        
        # Try to construct the password URL directly
        password_url = f"https://auth0.identity1.chegg.com/u/login/password?state={state}&ui_locales=en-US"
    else:
        password_url = identifier_resp.url
        print(f"Successfully redirected to password page: {password_url}")
    
    # Add a small delay to mimic human behavior
    await asyncio.sleep(1)
    
    print("Step 4: Submitting password...")
    # Submit the password
    password_data = {
        "state": state,
        "username": email,
        "password": password,
        "action": "default"
    }
    
    password_resp = await client.post(
        password_url,
        form=[(k, v) for k, v in password_data.items()],
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://auth0.identity1.chegg.com",
            "Referer": password_url
        }
    )
    
    print(f"Password submission status: {password_resp.status_code}")
    print(f"Current URL after password submission: {password_resp.url}")
    
    # Check if we're being redirected to the authorization endpoint
    if "/authorize/resume" in password_resp.url or "auth-gate.chegg.com" in password_resp.url:
        print("Successfully redirected to authorization endpoint")
        
        # Follow the redirect chain to complete login
        # Add a small delay to allow all redirects to complete
        await asyncio.sleep(2)
        
        home_resp = await client.get("https://www.chegg.com/")
        print(f"Home page status after login: {home_resp.status_code}")
        
        # Check if login was successful
        home_html = await home_resp.text()
        
        # Save the HTML for debugging
        with open('chegg_home.html', 'w', encoding='utf-8') as f:
            f.write(home_html)
        print("Saved home page HTML to chegg_home.html")
        
        # Look for indicators of successful login
        login_indicators = ["account", "logout", "my library", "my account"]
        login_successful = any(indicator in home_html.lower() for indicator in login_indicators)
        
        if login_successful:
            print("Login successful!")
            
            # Save cookies to a file
            cookies = []
            for url in ["https://www.chegg.com/", "https://auth0.identity1.chegg.com/"]:
                site_cookies = client.get_cookies(url)
                if site_cookies:
                    cookies.extend(site_cookies)
            
            with open('chegg_cookies.json', 'w') as f:
                json.dump([{
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain,
                    "path": c.path,
                    "expires": c.expires,
                    "secure": c.secure,
                    "http_only": c.http_only
                } for c in cookies], f)
            print("Cookies saved to chegg_cookies.json")
            
            return True, client
        else:
            print("Login might have failed. Could not find account/logout indicators.")
            print("Please check chegg_home.html for details.")
            return False, None
    else:
        print("Login failed. Did not redirect to authorization endpoint.")
        print(f"Current URL: {password_resp.url}")
        
        # Try to get the content to see what went wrong
        content = await password_resp.text()
        with open('login_failure.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Saved failure page to login_failure.html")
        
        return False, None

async def main():
    email = "3suk300x5j@jxpomup.com"  # Replace with your Chegg email
    password = "3suk300x5j@jxpomup.com"  # Replace with your Chegg password
    
    success, client = await login_to_chegg(email, password)
    
    if success and client:
        # Example: Access a page that requires login
        print("\nAccessing a page that requires login...")
        response = await client.get("https://www.chegg.com/study")
        print(f"Study page status code: {response.status_code}")
        
        # Save the study page HTML for verification
        study_html = await response.text()
        with open('chegg_study.html', 'w', encoding='utf-8') as f:
            f.write(study_html)
        print("Saved study page HTML to chegg_study.html")

if __name__ == "__main__":
    asyncio.run(main())