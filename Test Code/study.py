import requests

# API endpoint
api_url = "https://herobot.me/api/study/unlock"

# URL to unlock
target_url = "https://homework.study.com/explanation/separate-income-statements-of-quail-corp-and-its-80-owned-subsidiary-savannah-corp-for-2016-are-as-follows-quail-savannah-sales-rev-800-000-300-000-gain-on-equipment-35-000-cost-of-sales-4000.html"

# Headers
headers = {
    "Authorization": "ZELLYAUTH",
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "url": target_url
}

try:
    # Send POST request
    response = requests.post(api_url, json=payload, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        print("Success!")
        print(response.json())  # Print the response data
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)  # Print error message if any

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
