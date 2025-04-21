import requests

# Define the user agent
useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'

# Define the data payload
data = {
    'api-key': '0485',
    'useragent': useragent
}

try:
    # Make the POST request
    response = requests.post('https://hwclutch.com/incap', json=data)

    # Try to print the JSON response if possible
    try:
        print(response.json())
    except ValueError:
        print("[!] Response is not JSON. Raw response:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print("[!] Request failed:", e)
