import requests
import json
import time

# Configuration
ENDPOINT = "https://hwclutch.com/incap"
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'

# Possible API keys to try - the first is the original, others are variations to test
api_keys = [
    'zelly',
    'Zelly',
    'zellyunlock',
    'zellyv2',
    'zelly-api',
    'zellyapi'
]

# For proxies if needed
proxies = {
    'http': f'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337',
    'https': f'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337'
}

def make_request(api_key, use_proxies=False):
    """Make a request to the hwclutch endpoint with the given API key"""
    data = {
        'api-key': api_key,
        'useragent': USER_AGENT
    }
    
    # Try different parameter formats
    alt_data = {
        'apikey': api_key,
        'user-agent': USER_AGENT
    }
    
    print(f"\n--- Testing API key: '{api_key}' {'(with proxies)' if use_proxies else ''} ---")
    
    request_variants = [
        {"name": "Original format", "data": data},
        {"name": "Alternative format", "data": alt_data}
    ]
    
    for variant in request_variants:
        print(f"\nTrying {variant['name']}: {json.dumps(variant['data'], indent=2)}")
        
        try:
            if use_proxies:
                response = requests.post(ENDPOINT, json=variant['data'], proxies=proxies, timeout=15)
            else:
                response = requests.post(ENDPOINT, json=variant['data'], timeout=15)
            
            print(f"Status code: {response.status_code}")
            
            try:
                # Try to parse as JSON
                response_json = response.json()
                print(f"Response (JSON):")
                print(json.dumps(response_json, indent=2))
                
                # Check for the expected 'postdata' key
                if 'postdata' in response_json:
                    print("\n✅ SUCCESS: 'postdata' key found in response")
                    print(f"This configuration works: API key '{api_key}', format: {variant['name']}, proxies: {use_proxies}")
                    return True, api_key, variant['data'], use_proxies
                else:
                    print("\n❌ 'postdata' key NOT found in response")
                    if len(response_json) > 0:
                        print("Available keys:", list(response_json.keys()))
            except json.JSONDecodeError:
                print("Response is not valid JSON:")
                print(response.text[:500])  # Show first 500 chars
                
            # Add a small delay between requests to not overload the server
            time.sleep(1)
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    return False, None, None, None

def main():
    print("Starting hwclutch.com API test...")
    
    # Test without proxies first for all API keys
    for api_key in api_keys:
        success, working_key, working_data, with_proxies = make_request(api_key, use_proxies=False)
        if success:
            print("\n===== FOUND WORKING CONFIGURATION =====")
            print(f"API key: {working_key}")
            print(f"Request format: {json.dumps(working_data, indent=2)}")
            print(f"Proxies: {with_proxies}")
            return
    
    # If no success, try with proxies
    for api_key in api_keys:
        success, working_key, working_data, with_proxies = make_request(api_key, use_proxies=True)
        if success:
            print("\n===== FOUND WORKING CONFIGURATION =====")
            print(f"API key: {working_key}")
            print(f"Request format: {json.dumps(working_data, indent=2)}")
            print(f"Proxies: {with_proxies}")
            return
    
    print("\n❌ No working configuration found. The service may be down or the API may have changed significantly.")
    
if __name__ == "__main__":
    main() 