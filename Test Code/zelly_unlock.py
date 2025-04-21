import requests
import re
import mimetypes
import random
import string
import capsolver
import base64
import urllib3
import json
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#link here
link = 'https://www.coursehero.com/file/140135505/Parcial-Analiticapdf/'

def recaptcha():
    try:
        print("Attempting to solve recaptcha...")
        capsolver.api_key = "CAP-93BF0B9A68800E2D4F3CF7B585853A90" #add capsolver id
        solution = capsolver.solve({
                "type": "ReCaptchaV2EnterpriseTaskProxyLess",
                "websiteURL": "https://www.coursehero.com",
                "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
                "apiDomain": "www.recaptcha.net",
                "pageAction": "login"
                })

        print("Recaptcha solved successfully")
        return solution['gRecaptchaResponse']

    except Exception as e:
        print(f"Error solving recaptcha: {e}")
        return (500)

# Set to True to use proxies, False to bypass them for testing
USE_PROXIES = False

proxies = {
    'http': f'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337', #add your proxies
    'https': f'http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337' #add your proxies
} if USE_PROXIES else None

# Set a default user agent value
useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

# 1. Create a session and load cookies to bypass initial security
session = requests.Session()

print("Loading cookies from JSON file to help access the login page...")
try:
    with open('zcoursehero_cookie.json', 'r') as f:
        cookies_data = json.load(f)

    # Add all cookies from the JSON file to the session
    for cookie in cookies_data:
        session.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie['domain'],
            path=cookie['path'],
            secure=cookie['secure']
        )
    print(f"Loaded {len(cookies_data)} cookies successfully")
except Exception as e:
    print(f"Error loading cookies: {e}")

# 2. Access the login page with the initial cookies
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Dnt': '1',
    'Referer': 'https://www.coursehero.com/',
    'sec-ch-ua': "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': useragent
}

print("Accessing login page with initial cookies...")
try:
    response = session.get('https://www.coursehero.com/login/?login_user_type=&ref=login', headers=headers, proxies=proxies)
    print(f"Login page status code: {response.status_code}")
except Exception as e:
    print(f"Error accessing login page: {e}")

# 3. Solve CAPTCHA and log in to get fresh authentication
print("Preparing to log in...")
time.sleep(1)  # Small delay to make the request pattern more human-like

recaptcha_token = 500
while recaptcha_token == 500:
    recaptcha_token = recaptcha()

data = {
    'password': 'pzkudvqxdt@ibolinva.com',  #ch account
    'email': 'pzkudvqxdt@ibolinva.com',     #ch account
    'submit': 'true',
    'remember_me': '1',
    'g-recaptcha-response': recaptcha_token
}

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.coursehero.com',
    'priority': 'u=1, i',
    'referer': 'https://www.coursehero.com/login/?login_user_type=&ref=login',
    'sec-ch-ua': "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': useragent,
    'x-newrelic-id': 'Ug8CUVVbGwIDUlVUBgkGVg=='
}

print("Attempting to log in with credentials...")
try:
    response = session.post('https://www.coursehero.com/ajax/login.php', headers=headers, data=data, proxies=proxies)
    print(f"Login response status code: {response.status_code}")
    print(f"Login response: {response.text[:200]}...")  # Print first 200 chars of response
except Exception as e:
    print(f"Error during login: {e}")

# 4. Now we should have fresh authentication cookies in our session
if response.status_code == 200:
    print('Successfully logged in, session should now have fresh authentication cookies')
    
    # Print all cookies in the session to verify we have new ones
    print("Current session cookies:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value[:10]}... (domain: {cookie.domain})")
    
    # 5. Process the document with our authenticated session
    link = link.replace('/collection/', '/file/')
    print(f"\nProcessing link: {link}")

    if '/file/' in link:
        searchDocId = re.search('file/(.+?)/', link)
    else:
        searchDocId = re.search('documents/(.+?)/', link)

    if searchDocId and "https://www.coursehero.com" in link:
        print(f"Found document ID: {searchDocId.group(1)}")

        try:
            print("Checking unlocks remaining with authenticated session...")
            resp = session.get('https://www.coursehero.com/api/v1/users/unlocks/uploads/', headers=headers, proxies=proxies, verify=False)
            print(f"Unlocks API response status: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"Error checking unlocks. Response: {resp.text[:200]}...")
                print("This suggests our session may not be properly authenticated. Trying to proceed anyway...")
            else:
                unlocksJSON = resp.json()
                print(f"Unlocks remaining: {unlocksJSON.get('unlocks_remaining', 'Not found')}")
            
            # Proceed with document access
            documentID = searchDocId.group(1)
            print(f"Searching for document {documentID}...")
            
            resp = session.get(f"https://www.coursehero.com/api/v1/documents/{documentID}/", headers=headers, proxies=proxies, verify=False)
            print(f"Document API response status: {resp.status_code}")
            
            if resp.status_code == 200:
                documentJSON = resp.json()
                documentID = documentJSON['db_filename']
                documentName = documentJSON['title']
                documentThumbnail = documentJSON['thumbnail']
                documentCHURL = documentJSON['resource_url']
                print(f"Found document: {documentName}")

                print("Attempting to unlock document with authenticated session...")
                resp = session.post(f"https://www.coursehero.com/api/v1/users/unlocks/content/document/id/{documentID}/", headers=headers, proxies=proxies, verify=False)
                print(f"Unlock response status: {resp.status_code}")
                print(f"Unlock response: {resp.text[:200]}...")
                
                if resp.status_code == 200:
                    print("Document unlocked successfully, downloading...")
                    resp = session.get(f"https://www.coursehero.com/api/v1/documents/download/{documentID}/", headers=headers, proxies=proxies, verify=False)
                    print(f"Download response status: {resp.status_code}")
                    
                    if resp.status_code == 200:
                        extension = mimetypes.guess_extension(resp.headers.get('content-type', 'application/octet-stream'))
                        if extension is None:
                            extension = '.pdf'  # Default to PDF if we can't determine

                        documentContent = resp.content
                        documentFile = f"{documentName}{extension}"
                        contentType = resp.headers.get('content-type', 'unknown')
                        print(f"Saving document with content type: {contentType}")

                        with open(f"answer{extension}", "wb") as f:
                            f.write(documentContent)

                        print('Document unlocked and saved successfully!')
                    else:
                        print(f'Error downloading document: {resp.text[:200]}...')
                        print("Trying direct document download as fallback...")
                        resp = session.get(link, headers=headers, proxies=proxies, verify=False)
                        print(f"Direct access response status: {resp.status_code}")
                        
                        if resp.status_code == 200 and len(resp.content) > 1000:
                            print("Saving content from direct link...")
                            with open("answer_direct.html", "wb") as f:
                                f.write(resp.content)
                            print("Saved direct content to answer_direct.html")
                else:
                    print(f'Error unlocking document: {resp.text[:200]}...')
                    print("Trying direct document download as fallback...")
                    resp = session.get(link, headers=headers, proxies=proxies, verify=False)
                    print(f"Direct access response status: {resp.status_code}")
                    
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        print("Saving content from direct link...")
                        with open("answer_direct.html", "wb") as f:
                            f.write(resp.content)
                        print("Saved direct content to answer_direct.html")
            else:
                print(f'Error fetching document info: {resp.text[:200]}...')
                print("Trying direct link as fallback...")
                resp = session.get(link, headers=headers, proxies=proxies, verify=False)
                print(f"Direct access response status: {resp.status_code}")
                
                if resp.status_code == 200 and len(resp.content) > 1000:
                    print("Saving content from direct link...")
                    with open("answer_direct.html", "wb") as f:
                        f.write(resp.content)
                    print("Saved direct content to answer_direct.html")
        except Exception as e:
            print(f"Error in document processing: {e}")
    else:
        print("Invalid link format or couldn't extract document ID")
else:
    print(f"Login failed with status code: {response.status_code}")
    print("Trying direct link as fallback...")
    resp = session.get(link, headers=headers, proxies=proxies, verify=False)
    print(f"Direct access response status: {resp.status_code}")
    
    if resp.status_code == 200 and len(resp.content) > 1000:
        print("Saving content from direct link...")
        with open("answer_direct.html", "wb") as f:
            f.write(resp.content)
        print("Saved direct content to answer_direct.html")

print("Script completed execution")