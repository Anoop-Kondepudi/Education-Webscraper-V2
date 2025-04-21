import requests
import re
url = input("Enter the Chegg question URL: ").strip()

headers = {
    "Host": "www.chegg.com",
    "Connection": "Close",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://www.google.com/",
    "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
}


try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status Code:", response.status_code)

    if response.status_code == 200:

        # Extract UUID using regex
        match = re.search(r'"uuid"\s*:\s*"([^"]+)"', response.text)
        if match:
            uuid = match.group(1)
            print("UUID found:", uuid)
        else:
            print("UUID not found.")
    else:
        print("Request failed with status:", response.status_code)

except requests.exceptions.ConnectTimeout:
    print("Connection timed out")
except Exception as e:
    print("An error occurred:", e)
