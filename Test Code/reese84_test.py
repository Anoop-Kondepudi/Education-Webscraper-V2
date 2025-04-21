import requests

url = "https://incapsula-reese84-api.p.rapidapi.com/reese84"

payload = {
	"url": "https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad?d=www.coursehero.com",
	"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
headers = {
	"x-rapidapi-key": "d9d2828e55mshcd858ec0a03be28p1d51f2jsna548dab87e79",
	"x-rapidapi-host": "incapsula-reese84-api.p.rapidapi.com",
	"Content-Type": "application/json"
}

# Create a session
session = requests.Session()

# Parse and add cookies to the session
cookie_string = "visid_incap_987752=vIOn6VrgR/66LGR+8GD/wIIO9mcAAAAAQUIPAAAAAADQofhnVCBGJTz6qHX785q3; incap_ses_4556_987752=rmQDDJE5yTLxRTlU9ik6P4IO9mcAAAAAI7jf2+BGDqSGO1y3VssqFA=="
cookies = {}
for cookie in cookie_string.split('; '):
    name, value = cookie.split('=', 1)
    cookies[name] = value

session.cookies.update(cookies)

# Use the session to make the request
response = session.post(url, json=payload, headers=headers)

print(response.json())