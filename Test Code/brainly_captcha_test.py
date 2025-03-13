import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

# === CONFIGURATION ===
CAPSOLVER_API_KEY = "CAP-93BF0B9A68800E2D4F3CF7B585853A90"  # 🔹 Replace with your actual Capsolver key
BRAINLY_URL = "https://brainly.com/question/48003838"

# ✅ Use one of the required User-Agents from Capsolver docs
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# ✅ Your proxy formatted correctly (username:password@ip:port)
PROXY = "12.176.171.19:8080:wr37kDWXUGoa:USMuWej9iXz8"

# === SETUP SELENIUM ===
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# === EXTRACT CAPTCHA PARAMETERS ===
def get_captcha_data():
    driver = setup_driver()
    driver.get(BRAINLY_URL)
    print(f"✅ Opened {BRAINLY_URL} successfully.")

    time.sleep(5)  # Allow CAPTCHA to load

    print("🔎 Searching for CAPTCHA iframe...")
    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        captcha_url = iframe.get_attribute("src")

        if "geo.captcha-delivery.com" not in captcha_url:
            raise Exception("❌ CAPTCHA URL does not match expected DataDome format.")

        print(f"✅ Extracted CAPTCHA URL: {captcha_url}")

    except Exception as e:
        print(f"❌ Failed to find CAPTCHA: {e}")
        driver.quit()
        return None, None, None

    # Extract cookies
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    datadome_cookie = cookies.get("datadome", "")

    print(f"✅ Extracted DataDome Cookie: {datadome_cookie}")

    driver.quit()
    return captcha_url, USER_AGENT, datadome_cookie

# === SOLVE CAPTCHA WITH CAPSOLVER ===
def solve_captcha(captcha_url, user_agent, proxy):
    print("\n🚀 Sending CAPTCHA request to Capsolver...")

    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "DatadomeSliderTask",
            "websiteURL": "https://brainly.com",  # ✅ Correct "websiteURL"
            "captchaUrl": captcha_url,  # ✅ Extracted fresh CAPTCHA URL
            "proxy": proxy,  # ✅ Use Capsolver's proxy format
            "userAgent": user_agent  # ✅ Required fixed User-Agent
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Debugging: Show request payload
    print("\n📜 Request Payload:\n", json.dumps(payload, indent=2))

    response = requests.post("https://api.capsolver.com/createTask", json=payload, headers=headers)

    if response.status_code != 200:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)  # Show full response error
        return None

    result = response.json()
    print("\n🔍 Capsolver Response:", json.dumps(result, indent=2))

    if result.get("errorId") != 0:
        print("❌ Error creating CAPTCHA task:", result.get("errorDescription"))
        return None

    task_id = result["taskId"]
    print(f"✅ Task Created. Task ID: {task_id}")

    return get_captcha_solution(task_id)

# === GET CAPTCHA SOLUTION ===
def get_captcha_solution(task_id):
    print("\n⏳ Waiting for CAPTCHA solution...")
    while True:
        time.sleep(5)  # Wait before polling
        response = requests.post("https://api.capsolver.com/getTaskResult", json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id})
        result = response.json()

        if result.get("status") == "ready":
            print("✅ CAPTCHA Solved!")
            return result["solution"]["cookie"]

        if result.get("status") == "failed":
            print("❌ CAPTCHA solving failed.")
            return None

        print("🔄 Still solving...")

# === MAIN SCRIPT EXECUTION ===
if __name__ == "__main__":
    captcha_url, user_agent, datadome_cookie = get_captcha_data()
    
    if captcha_url:
        solution_cookie = solve_captcha(captcha_url, user_agent, PROXY)
        if solution_cookie:
            print("\n🎉 Successfully solved CAPTCHA! Use this cookie:")
            print(f"datadome={solution_cookie}")
        else:
            print("\n❌ CAPTCHA solution failed.")
    else:
        print("\n❌ Could not retrieve CAPTCHA URL. Exiting.")