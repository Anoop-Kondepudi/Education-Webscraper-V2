import requests
import capsolver
import urllib3
import random
from datetime import datetime
from collections import OrderedDict
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy Configuration
PROXY_HOST = "144.229.117.13"
PROXY_PORT = "1337"
PROXY_USER = "lho7SIZFaRh9"
PROXY_PASS = "1inYc0RRMvYs"

# Chrome 120 Browser Headers (in correct order)
ORDERED_HEADERS = OrderedDict([
    ('sec-ch-ua', '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'),
    ('sec-ch-ua-mobile', '?0'),
    ('sec-ch-ua-platform', '"Windows"'),
    ('upgrade-insecure-requests', '1'),
    ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    ('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'),
    ('sec-fetch-site', 'none'),
    ('sec-fetch-mode', 'navigate'),
    ('sec-fetch-user', '?1'),
    ('sec-fetch-dest', 'document'),
    ('accept-encoding', 'gzip, deflate, br'),
    ('accept-language', 'en-US,en;q=0.9'),
])

def get_random_device_memory():
    return random.choice([2, 4, 8, 16])

def get_random_hardware_concurrency():
    return random.choice([4, 6, 8, 12, 16])

def solve_recaptcha():
    try:
        capsolver.api_key = "CAP-BF3A913B93C1406DB8D4772118D2E44694DF0EB9DD657FF38C5A5C30712159C7"
        solution = capsolver.solve({
            "type": "ReCaptchaV2EnterpriseTaskProxyLess",
            "websiteURL": "https://www.coursehero.com",
            "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
            "apiDomain": "www.recaptcha.net",
            "pageAction": "login"
        })

        return solution['gRecaptchaResponse']
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return None

def create_browser_fingerprint():
    return {
        'deviceMemory': get_random_device_memory(),
        'hardwareConcurrency': get_random_hardware_concurrency(),
        'platform': 'Win32',
        'webdriver': 'false',
        'language': 'en-US',
        'colorDepth': 24,
        'pixelRatio': 1,
        'screenResolution': f"{random.choice([1920, 2560])}x{random.choice([1080, 1440])}",
        'timezoneOffset': random.choice([-480, -420, -360, -300, -240]),
        'timezone': 'America/New_York'
    }

def login_to_coursehero():
    session = requests.Session()
    
    proxies = {
        'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
        'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
    }
    
    # Generate browser fingerprint
    fingerprint = create_browser_fingerprint()
    
    # Initial page load with browser-like headers
    print(f"[{datetime.now()}] Initial page visit...")
    try:
        headers = dict(ORDERED_HEADERS)
        headers['sec-fetch-site'] = 'none'
        headers['sec-fetch-mode'] = 'navigate'
        headers['sec-fetch-dest'] = 'document'
        
        # Visit homepage first
        response = session.get(
            'https://www.coursehero.com/',
            headers=headers,
            proxies=proxies,
            verify=False
        )
        print(f"Homepage response status: {response.status_code}")
        time.sleep(3)  # Add delay between requests
        
        # Then visit login page
        response = session.get(
            'https://www.coursehero.com/login/',
            headers=headers,
            proxies=proxies,
            verify=False
        )
        print(f"Login page response status: {response.status_code}")
        time.sleep(2)
        
        # Extract any security tokens or cookies
        for cookie in response.cookies:
            print(f"Received cookie: {cookie}")
            
    except Exception as e:
        return False, f"Initial page load failed: {e}"

    # Get Reese84 token
    print(f"[{datetime.now()}] Getting Reese84 token...")
    try:
        # Read post data from file
        with open('postdata.txt') as f:
            post_data = f.read()
        
        # Make request to get Reese84 token
        response = session.post(
            'https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad?d=www.coursehero.com',
            headers=headers,
            data=post_data,
            proxies=proxies,
            verify=False
        )
        
        response_json = response.json()
        reese84_token = response_json["token"]
        
        print(f"Reese84 token: {reese84_token}")
        print(f"Response JSON: {response_json}")
        
        # Set the token as a cookie
        session.cookies.set("reese84", reese84_token, domain='www.coursehero.com', path='/', secure=True)
        
        # Update headers for subsequent requests - storing these for later use
        reese84_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Dnt': '1',
            'Referer': 'https://www.coursehero.com/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': ORDERED_HEADERS['user-agent']
        }
        
        # Visit login page with updated headers
        response = session.get(
            'https://www.coursehero.com/login/?login_user_type=&ref=login',
            headers=reese84_headers,
            proxies=proxies,
            verify=False
        )
        print(f"Login page response with Reese84 token: {response}")
        
    except Exception as e:
        return False, f"Failed to get Reese84 token: {e}"

    # Solve reCAPTCHA
    print(f"[{datetime.now()}] Solving reCAPTCHA...")
    recaptcha_token = solve_recaptcha()
    if not recaptcha_token:
        return False, "Failed to solve captcha"
    
    time.sleep(2)  # Add delay after captcha

    # Use the same headers from Reese84 token request for consistency
    login_headers = reese84_headers.copy()
    login_headers.update({
        'origin': 'https://www.coursehero.com',
        'referer': 'https://www.coursehero.com/login/',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'x-requested-with': 'XMLHttpRequest'
    })

    # No need to add fingerprint data since we're maintaining the security context
    # from the successful Reese84 token request

    login_data = {
        'email': 'pzkudvqxdt@ibolinva.com',
        'password': 'pzkudvqxdt@ibolinva.com',
        'submit': 'true',
        'remember_me': '1',
        'g-recaptcha-response': recaptcha_token,
        'login_type': 'Email',
        'device_type': 'desktop'
    }
    
    print(f"[{datetime.now()}] Attempting login...")
    try:
        # Add a short delay before login attempt
        time.sleep(1)
        
        response = session.post(
            'https://www.coursehero.com/ajax/login.php',
            headers=login_headers,
            data=login_data,
            proxies=proxies,
            verify=False,
            timeout=30
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response headers: {dict(response.headers)}")
        print(f"Login response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            if '"success":true' in response.text:
                return True, session
            else:
                return False, "Invalid credentials or login failed"
        else:
            return False, f"Login failed with status code: {response.status_code}"
            
    except Exception as e:
        return False, f"Login error: {e}"

def main():
    success, result = login_to_coursehero()
    if success:
        print(f"[{datetime.now()}] Successfully logged in!")
        session = result
    else:
        print(f"[{datetime.now()}] Login failed: {result}")

if __name__ == "__main__":
    main()