import requests
from capsolver import Capsolver  # Corrected import

# CapSolver API Key
CAPSOLVER_API_KEY = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"

# Proxy details (Replace with yours)
PROXY = "http://wr37kDWXUGoa:USMuWej9iXz8@12.176.171.19:8080"

# Initialize CapSolver (Corrected class name)
solver = Capsolver(api_key=CAPSOLVER_API_KEY)

# Step 1: Solve DataDome challenge
task = {
    "type": "AntiBotDataDomeTask",
    "websiteURL": "https://brainly.com",
    "proxy": PROXY,
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

solution = solver.solve(task)

if not solution:
    print("Failed to bypass DataDome")
    exit()

# Extract necessary data
cookies = solution["cookies"]
fingerprint = solution.get("fingerprint", {})
local_storage = solution.get("localStorage", {})

# Convert cookies to a request-friendly format
cookie_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])
user_agent = solution["userAgent"]

print(f"Cookies: {cookie_string}")
print(f"User-Agent: {user_agent}")
print(f"Fingerprint: {fingerprint}")
print(f"LocalStorage: {local_storage}")

# Step 2: Use the obtained cookies & fingerprint to make a request

# Setup session with proxy
session = requests.Session()
session.proxies = {
    "http": PROXY,
    "https": PROXY
}

# Headers with fingerprint data
headers = {
    "Cookie": cookie_string,
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://brainly.com/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}

# Brainly URL to scrape
brainly_url = "https://brainly.com"

# Make the request
response = session.get(brainly_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("✅ Successfully accessed Brainly!")
    print(response.text)  # View the response
else:
    print(f"❌ Request failed with status code {response.status_code}")
    print(response.text)  # Check what Brainly is returning