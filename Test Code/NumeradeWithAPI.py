import requests

# API endpoint
url = "https://herobot.me/api/numerade/unlock"

# Headers
headers = {
    "Authorization": "ZELLYAUTH",
    "Content-Type": "application/json"
}

# JSON data with hardcoded link
data = {
    "url": "https://www.numerade.com/ask/question/after-1-second-a-ball-dropped-from-rest-will-have-fallen-about-1-0-m-2-20-m-3-5-m-4-0-m-5-0-m-53166/"
}

# Make the POST request
response = requests.post(url, json=data, headers=headers)

# Print the response
print(response.status_code)
print(response.text)