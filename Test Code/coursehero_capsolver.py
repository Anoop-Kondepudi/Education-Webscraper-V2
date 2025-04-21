import requests
import re
import mimetypes
import base64
import json
import urllib3
import capsolver  # Ensure you have installed the capsolver package

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------- Configuration --------------------------
# Target document/collection URL on CourseHero
link = 'https://www.coursehero.com/file/140135505/Parcial-Analiticapdf/'

# API keys for Capsolver (update with your actual keys)
CAPSOLVER_API_KEY_RECAPTCHA = "CAP-BF3A913B93C1406DB8D4772118D2E44694DF0EB9DD657FF38C5A5C30712159C7"
CAPSOLVER_API_KEY_REESE84 = "CAP-BF3A913B93C1406DB8D4772118D2E44694DF0EB9DD657FF38C5A5C30712159C7"

# CourseHero login credentials – update these
COURSEHERO_EMAIL = 'your_coursehero_email'
COURSEHERO_PASSWORD = 'your_coursehero_password'

# Standard user agent
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0'

# Create a persistent session
session = requests.Session()

# -------------------------- Capsolver ReCaptcha Function --------------------------
def recaptcha():
    """
    Solve the CourseHero reCAPTCHA challenge using Capsolver.
    """
    try:
        capsolver.api_key = CAPSOLVER_API_KEY_RECAPTCHA  # Set the reCAPTCHA API key
        solution = capsolver.solve({
            "type": "ReCaptchaV2EnterpriseTaskProxyLess",
            "websiteURL": "https://www.coursehero.com",
            "websiteKey": "6Lee8D4bAAAAAC3mq6sHfelhKEZJEk667GmJOy4m",
            "anchor": "",
            "apiDomain": "www.recaptcha.net",
            "pageAction": "login"
        })
        token = solution['gRecaptchaResponse']
        print("Recaptcha Token Obtained:", token)
        return token
    except Exception as e:
        print("Error solving reCAPTCHA:", e)
        return 500

# -------------------------- Capsolver Reese84 Functions --------------------------
def get_reese84_solution():
    """
    Send an AntiImperva task to Capsolver to obtain the raw Reese84 payload.
    Returns the solution dict with the payload and userAgent.
    """
    reese_url = "https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad"
    payload = {
        "clientKey": CAPSOLVER_API_KEY_REESE84,
        "task": {
            "type": "AntiImpervaTaskProxyLess",
            "reeseScriptUrl": reese_url,
            "websiteURL": "https://www.coursehero.com/"
        }
    }
    
    print("Sending Reese84 task to Capsolver...")
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    if res.status_code != 200:
        print("Failed to create Reese84 task:", res.text)
        return None

    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Error creating task:", res.text)
        return None

    print(f"Reese84 task created, taskId: {task_id}. Waiting for solution...")
    
    # Poll until solution is ready (you could add a delay between polls if needed)
    while True:
        poll_payload = {"clientKey": CAPSOLVER_API_KEY_REESE84, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=poll_payload)
        resp = res.json()
        status = resp.get("status")
        
        if status == "ready":
            solution = resp.get("solution", {})
            print("Reese84 solution obtained.")
            return solution
        elif status == "failed" or resp.get("errorId"):
            print("Reese84 solve failed:", res.text)
            return None

def post_reese_payload(payload_text, user_agent):
    """
    Post the raw Reese84 payload (obtained from Capsolver) to CourseHero 
    to get the final reese84 token.
    """
    reese_url = "https://www.coursehero.com/Ifainesse-What-mine-Alasterd-the-How-I-haile-Lad"
    # Append query parameter if necessary
    if "?" not in reese_url:
        post_url = f"{reese_url}?d=www.coursehero.com"
    else:
        post_url = reese_url
    
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "text/plain; charset=utf-8",
        "Origin": "https://www.coursehero.com",
        "Referer": "https://www.coursehero.com/",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "upgrade-insecure-requests": "1",
        "user-agent": user_agent
    }
    
    resp = session.post(post_url, headers=headers, data=payload_text, verify=False)
    if resp.status_code != 200:
        print("Post reese84-payload failed:", resp.status_code, resp.text)
        return None

    data = resp.json()
    token = data.get('token')
    if not token:
        print("No token found in the response:", resp.text)
        return None
    
    print("Successfully received Reese84 token:", (token[:30] + "...") if len(token) > 30 else token)
    return token

# -------------------------- Main Flow --------------------------
def main():
    # Step 1: Fetch the CourseHero login page to establish session cookies
    login_page_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Dnt': '1',
        'Referer': 'https://www.coursehero.com/',
        'sec-ch-ua': "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': useragent
    }
    resp = session.get('https://www.coursehero.com/login/?login_user_type=&ref=login', headers=login_page_headers, verify=False)
    print("CourseHero login page fetched.")

    # Step 2: Obtain the Reese84 token using Capsolver BEFORE login
    reese_solution = get_reese84_solution()
    if not reese_solution or "reese84Payload" not in reese_solution or "userAgent" not in reese_solution:
        print("Failed to obtain a valid Reese84 solution.")
        return

    reese84_token = post_reese_payload(reese_solution["reese84Payload"], reese_solution["userAgent"])
    if not reese84_token:
        print("Failed to obtain the Reese84 token.")
        return

    # Set the Reese84 token as a cookie in the session.
    session.cookies.set("reese84", reese84_token, domain='www.coursehero.com', path='/', secure=True)
    print("Reese84 token set in session cookies.")

    # Step 3: Solve the reCAPTCHA using Capsolver
    recaptcha_token = 500
    while recaptcha_token == 500:
        recaptcha_token = recaptcha()

    # Step 4: Submit the login request with email, password, and the solved reCAPTCHA
    login_data = {
        'email': COURSEHERO_EMAIL,
        'password': COURSEHERO_PASSWORD,
        'submit': 'true',
        'remember_me': '1',
        'g-recaptcha-response': recaptcha_token
    }
    
    login_headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.coursehero.com',
        'priority': 'u=1, i',
        'referer': 'https://www.coursehero.com/login/?login_user_type=&ref=login',
        'sec-ch-ua': "\"Chromium\";v=\"135\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"135\"",
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': useragent,
        'x-newrelic-id': 'Ug8CUVVbGwIDUlVUBgkGVg=='
    }
    
    login_response = session.post('https://www.coursehero.com/api/v2/login/', headers=login_headers, data=login_data, verify=False)
    print("Login response:", login_response.text)
    
    if login_response.status_code == 200:
        print("Logged in successfully.")
        # Continue with your document unlocking and downloading as in your original flow.
        modified_link = link.replace('/collection/', '/file/')
        if '/file/' in modified_link:
            searchDocId = re.search('file/(.+?)/', modified_link)
        else:
            searchDocId = re.search('documents/(.+?)/', modified_link)
        
        if searchDocId and "https://www.coursehero.com" in modified_link:
            unlocks_resp = session.get('https://www.coursehero.com/api/v1/users/unlocks/uploads/', headers=login_headers, verify=False)
            unlocksJSON = unlocks_resp.json()
            
            try:
                if unlocksJSON['unlocks_remaining'] > 0:
                    documentID = searchDocId.group(1)
                    doc_resp = session.get(f"https://www.coursehero.com/api/v1/documents/{documentID}/", headers=login_headers, verify=False)
                    
                    if doc_resp.status_code == 200:
                        documentJSON = doc_resp.json()
                        documentID_api = documentJSON['db_filename']
                        documentName = documentJSON['title']
                        
                        unlock_resp = session.post(f"https://www.coursehero.com/api/v1/users/unlocks/content/document/id/{documentID_api}/", headers=login_headers, verify=False)
                        download_resp = session.get(f"https://www.coursehero.com/api/v1/documents/download/{documentID_api}/", headers=login_headers, verify=False)
                        if download_resp.status_code == 200:
                            extension = mimetypes.guess_extension(download_resp.headers['content-type'])
                            if extension is None:
                                extension = '.xlsx'
                            with open(f"answer{extension}", "wb") as f:
                                f.write(download_resp.content)
                            print("Document unlocked and downloaded successfully.")
                        else:
                            print("Error downloading the document.")
                    else:
                        print("Error fetching document details.")
            except Exception as e:
                print("Exception during document unlocking:", e)
        else:
            print("Invalid document link provided.")
    else:
        print("Login failed.")

# -------------------------- Run the Script --------------------------
if __name__ == '__main__':
    main()
