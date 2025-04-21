import requests
import socket
import time
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://hwclutch.com"
TIMEOUT = 10

# Common endpoints to check
ENDPOINTS = [
    "/",
    "/incap",
    "/api",
    "/status",
    "/health",
    "/api/status",
    "/api/v1/incap",
    "/api/v2/incap"
]

def check_domain_dns():
    """Check if the domain resolves to an IP address"""
    print("Checking DNS resolution for hwclutch.com...")
    try:
        ip_address = socket.gethostbyname("hwclutch.com")
        print(f"✅ Domain resolves to: {ip_address}")
        return True
    except socket.gaierror:
        print("❌ Could not resolve domain. The domain may no longer exist.")
        return False

def check_url(url):
    """Check if a URL is accessible with different HTTP methods"""
    print(f"\nChecking URL: {url}")
    
    methods = ["GET", "HEAD", "OPTIONS"]
    
    for method in methods:
        try:
            print(f"  Trying {method} request...")
            if method == "GET":
                response = requests.request(method, url, timeout=TIMEOUT)
            else:
                response = requests.request(method, url, timeout=TIMEOUT)
                
            print(f"  Status code: {response.status_code}")
            
            if response.status_code < 400:
                print(f"  ✅ {method} request successful")
                
                # If it's a GET request and we got a successful response, check the content
                if method == "GET":
                    content_type = response.headers.get('Content-Type', '')
                    print(f"  Content-Type: {content_type}")
                    
                    try:
                        if 'application/json' in content_type:
                            json_response = response.json()
                            print(f"  Response contains valid JSON with keys: {list(json_response.keys())}")
                        else:
                            # Just show the first 200 chars of the response
                            preview = response.text[:200]
                            if len(response.text) > 200:
                                preview += "..."
                            print(f"  Response preview: {preview}")
                    except Exception as e:
                        print(f"  Error parsing response: {e}")
                
                return True
            else:
                print(f"  ❌ Received error status code")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ {method} request timed out")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {method} connection error")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {method} request failed: {e}")
        
        # Add a small delay between requests
        time.sleep(1)
    
    return False

def main():
    print("=== hwclutch.com Domain & Endpoint Discovery ===\n")
    
    # First check if the domain resolves
    if not check_domain_dns():
        print("\nDomain doesn't resolve. Further checks are unlikely to succeed.")
        choice = input("Continue with endpoint checks anyway? (y/n): ")
        if choice.lower() != 'y':
            return
    
    # Check each endpoint
    working_endpoints = []
    
    for endpoint in ENDPOINTS:
        url = urljoin(BASE_URL, endpoint)
        if check_url(url):
            working_endpoints.append(endpoint)
    
    # Summary
    print("\n=== Summary ===")
    if working_endpoints:
        print(f"Found {len(working_endpoints)} working endpoints:")
        for endpoint in working_endpoints:
            print(f"  - {urljoin(BASE_URL, endpoint)}")
    else:
        print("No working endpoints found. The service may be down or significantly changed.")
    
    # Custom endpoint check
    print("\n=== Custom Endpoint Check ===")
    while True:
        custom = input("\nEnter a custom endpoint to check (or 'q' to quit): ")
        if custom.lower() == 'q':
            break
            
        if not custom.startswith('/'):
            custom = '/' + custom
            
        check_url(urljoin(BASE_URL, custom))

if __name__ == "__main__":
    main() 