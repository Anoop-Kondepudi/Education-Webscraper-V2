import requests
import time
import json

# Proxy configuration from the original script
PROXIES = {
    'http': 'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337',
    'https': 'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337'
}

# Test URLs - starting with simple ones, then the target
TEST_URLS = [
    "http://httpbin.org/ip",           # Returns IP address, good for validating proxy works
    "https://httpbin.org/ip",          # Same but over HTTPS
    "https://api.ipify.org?format=json", # Alternative IP check
    "https://www.google.com",          # Simple connectivity test
    "https://www.coursehero.com",      # The target site
    "https://hwclutch.com"             # The problematic service
]

def test_connection(url, use_proxy=False, timeout=10):
    """Test connection to a URL with and without proxy"""
    method = "with proxy" if use_proxy else "without proxy"
    print(f"\nTesting {url} {method}")
    
    try:
        if use_proxy:
            start_time = time.time()
            response = requests.get(url, proxies=PROXIES, timeout=timeout)
            elapsed = time.time() - start_time
        else:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            elapsed = time.time() - start_time
            
        print(f"Status code: {response.status_code}")
        print(f"Response time: {elapsed:.2f} seconds")
        
        if "ip" in url:
            # For IP check services, show the IP we're connecting from
            try:
                response_json = response.json()
                if "ip" in response_json:
                    print(f"IP address: {response_json['ip']}")
                elif "origin" in response_json:
                    print(f"IP address: {response_json['origin']}")
                else:
                    print("IP information not found in response")
                    print(f"Response: {json.dumps(response_json, indent=2)}")
            except Exception as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Response text: {response.text[:200]}")
        
        return True
    except requests.exceptions.ConnectTimeout:
        print(f"Connection timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return False

def main():
    print("====== Proxy Testing Tool ======")
    print(f"Testing proxy: {PROXIES['https']}")
    
    # First validate the proxy itself works
    print("\n--- PROXY VALIDATION ---")
    proxy_works = False
    for url in TEST_URLS[:3]:  # Just use the IP-checking URLs for validation
        if test_connection(url, use_proxy=True):
            proxy_works = True
            break
    
    if not proxy_works:
        print("\n❌ PROXY VALIDATION FAILED")
        print("The configured proxy doesn't appear to be working.")
        choice = input("Continue with further tests? (y/n): ")
        if choice.lower() != 'y':
            return
    else:
        print("\n✅ PROXY VALIDATION SUCCESSFUL")
    
    # Test all URLs with and without proxy
    results = []
    
    print("\n--- DETAILED CONNECTION TESTS ---")
    for url in TEST_URLS:
        direct_result = test_connection(url, use_proxy=False)
        proxy_result = test_connection(url, use_proxy=True)
        
        results.append({
            "url": url,
            "direct_connection": "✅ Success" if direct_result else "❌ Failed",
            "proxy_connection": "✅ Success" if proxy_result else "❌ Failed"
        })
    
    # Print summary
    print("\n====== TEST RESULTS SUMMARY ======")
    print(f"{'URL':<30} | {'Direct Connection':<20} | {'Proxy Connection':<20}")
    print("-" * 75)
    
    for result in results:
        print(f"{result['url']:<30} | {result['direct_connection']:<20} | {result['proxy_connection']:<20}")
    
    # Recommendations
    print("\n====== RECOMMENDATIONS ======")
    if not proxy_works:
        print("1. The proxy appears to be invalid or expired. You should update the proxy configuration.")
    
    hwclutch_direct = next((r for r in results if r['url'] == 'https://hwclutch.com'), None)
    hwclutch_proxy = next((r for r in results if r['url'] == 'https://hwclutch.com'), None)
    
    if hwclutch_direct and 'Failed' in hwclutch_direct['direct_connection'] and hwclutch_proxy and 'Failed' in hwclutch_proxy['proxy_connection']:
        print("2. The hwclutch.com service appears to be down or has changed. The script needs to be updated.")
    
    if all('Failed' in r['proxy_connection'] for r in results) and any('Success' in r['direct_connection'] for r in results):
        print("3. The proxy is consistently failing. Try using direct connections if possible.")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main() 