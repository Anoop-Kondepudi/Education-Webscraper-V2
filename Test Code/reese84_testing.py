import requests
import json

session = requests.Session()

clearcaptcha_token='02592653b2b64121879fef6787589bda'

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0' #add user agent
 
data = {
    'token': clearcaptcha_token,
    'jsurl': 'https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad',
    'user_agent': useragent
}
 
response = requests.post('http://api.clearcaptcha.com/captcha/incapsula_reese84_sub', data = data)
print(response.text)

# Save first response text
with open("response.txt", "w") as file:
    file.write(response.text)

response_json = response.json()

# Save first response_json
with open("response_json.txt", "w") as file:
    file.write(json.dumps(response_json, indent=4))

post_data = response_json['data']['post_data']

# Save post_data
with open("post_data.txt", "w") as file:
    file.write(str(post_data))
 
headers = {
    "Accept":"application/json; charset=utf-8",
    "Content-Type": "text/plain; charset=utf-8",
    "Origin": "https://www.coursehero.com",
    "Referer": "https://www.coursehero.com/",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": useragent
}
 
response = session.post('https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad?d=www.coursehero.com', headers = headers, data = post_data,  verify = False)

# Save second response text
with open("coursehero_response.txt", "w") as file:
    file.write(response.text)

response_json = response.json()

# Save second response_json
with open("coursehero_response_json.txt", "w") as file:
    file.write(json.dumps(response_json, indent=4))

reese84_token = response.json()["token"]

# Save reese84_token
with open("reese84_token.txt", "w") as file:
    file.write(reese84_token)

print("All data has been saved to text files.")