import requests

# API endpoint
url = "https://herobot.me/api/bartleby/unlock"

# Headers
headers = {
    "Authorization": "ZELLYAUTH",
    "Content-Type": "application/json"
}

# JSON data with hardcoded link
data = {
    "url": "https://www.bartleby.com/questions-and-answers/1-1/871a766d-1b27-4914-869e-382b1cf5ec54"
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Print the response
print(response.status_code)
print(response.text)