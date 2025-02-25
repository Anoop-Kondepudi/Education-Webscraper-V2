import requests
import json
import time

# Capsolver API Key
CAPSOLVER_API_KEY = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"

# Target website URL
TARGET_URL = "https://www.allopneus.com/liste/pneu-auto?saison%5B%5D=4seasons&saison%5B%5D=ete&saison%5B%5D=hiver&page=1"

# Proxy Information
proxy_host = "12.176.171.19"  # Proxy IP
proxy_port = 8080  # Proxy Port
proxy_login = "wr37kDWXUGoa"  # Proxy Username
proxy_pass = "USMuWej9iXz8"  # Proxy Password

# Set up the proxy string
proxies = {
    "https": f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}",
    "http": f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
}

# Step 1: Create Datadome Task Request to Capsolver
headers = {"Content-Type": "application/json"}

payload = {
    "clientKey": CAPSOLVER_API_KEY,
    "task": {
        "type": "DatadomeTask",
        "websiteURL": TARGET_URL,
        "proxy": f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
    }
}

# Make the request and ensure the JSON is sent correctly
response = requests.post("https://api.capsolver.com/createTask", headers=headers, data=json.dumps(payload))
task_result = response.json()

# Check if task creation was successful
if "taskId" not in task_result:
    print("Error: Task creation failed:", task_result)
    exit()

task_id = task_result["taskId"]
print(f"Task created successfully! Task ID: {task_id}")

# Step 2: Poll for the solution
while True:
    check_payload = {"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}
    result_response = requests.post("https://api.capsolver.com/getTaskResult", headers=headers, data=json.dumps(check_payload))
    result_json = result_response.json()

    if result_json.get("status") == "ready":
        solution = result_json.get("solution")
        break

    print("Waiting for solution...")
    time.sleep(3)

# Extract solved cookies and user-agent
cookies = solution.get("cookies", {})
user_agent = solution.get("userAgent", "")

if not cookies:
    print("Error: Empty cookies, try again.")
    exit()

cookie_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])
print(f"Use these cookies for requests: {cookie_string}")
print(f"Use this user-agent for requests: {user_agent}")

# Step 3: Make the authenticated request using solved cookies and user-agent
session = requests.Session()
session.proxies = proxies

headers = {
    "Cookie": cookie_string,
    "User-Agent": user_agent
}

response = session.get(TARGET_URL, headers=headers)
print(response.text)