import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔹 Configurations
API_KEY = "YOUR_CAPSOLVER_API_KEY"
BRAINLY_URL = "https://brainly.com/question/48003838"
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

# 🔹 Setup Firefox Driver
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)
    
    print("\n🚀 Launching Firefox with custom profile...")
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# 🔹 Function to Extract CAPTCHA Parameters
def extract_captcha_params(driver):
    print("\n🔎 Searching for CAPTCHA iframe...")

    # Wait for iframe
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        print("✅ Switched to CAPTCHA iframe.")
    except:
        print("⚠️ No iframe detected. Continuing in main document...")

    # **NEW FIX**: Wait for JavaScript variable `window.dd` to be available
    print("\n⏳ Waiting for CAPTCHA script to fully load...")
    for _ in range(10):  # Try for up to 10 seconds
        try:
            script = """
            if (typeof window.dd !== "undefined") {
                return JSON.stringify(window.dd);
            } else {
                return null;
            }
            """
            dd_data = driver.execute_script(script)
            if dd_data:  # Ensure it's not None
                break
            print("🔄 window.dd not available yet. Retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ JavaScript execution error: {e}")
    
    if not dd_data:
        print("❌ Failed to extract CAPTCHA parameters: window.dd is missing.")
        return None
    
    print("✅ Extracted DataDome Parameters:\n", dd_data)
    return json.loads(dd_data)

# 🔹 Solve CAPTCHA via Capsolver
def solve_captcha(dd_data):
    print("\n🚀 Sending CAPTCHA data to Capsolver...")

    payload = {
        "clientKey": API_KEY,
        "task": {
            "type": "DataDomeTask",
            "captchaUrl": f"https://{dd_data['host']}/captcha/?initialCid={dd_data['cid']}&hash={dd_data['hsh']}&cid={dd_data['cookie']}&t={dd_data['t']}&s={dd_data['s']}&e={dd_data['e']}",
            "proxy": "",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    }

    response = requests.post("https://api.capsolver.com/createTask", json=payload)
    result = response.json()

    if "taskId" not in result:
        print("❌ Error creating CAPTCHA solving task:", result)
        return None

    task_id = result["taskId"]
    print(f"✅ Task created: {task_id}, waiting for solution...")

    while True:
        time.sleep(3)
        check_payload = {"clientKey": API_KEY, "taskId": task_id}
        check_res = requests.post("https://api.capsolver.com/getTaskResult", json=check_payload)
        check_resp = check_res.json()

        if check_resp.get("status") == "ready":
            print("✅ CAPTCHA solved successfully!")
            return check_resp["solution"]

        if check_resp.get("errorId"):
            print("❌ Error solving CAPTCHA:", check_resp)
            return None

# 🔹 Submit Solved CAPTCHA to Brainly
def submit_captcha(driver, solution):
    print("\n🔄 Injecting solved CAPTCHA into the webpage...")

    try:
        validate_token = solution["validate"]
        driver.execute_script(f'document.getElementById("geetest_validate").value = "{validate_token}";')

        submit_button = driver.find_element(By.ID, "submit_button")
        submit_button.click()

        print("✅ CAPTCHA bypassed successfully!")
    except Exception as e:
        print(f"❌ Error injecting CAPTCHA solution: {e}")

# 🔹 Main Execution
print("\n🖥️ Starting Firefox...")
driver = setup_driver()

print("\n🌍 Navigating to Brainly...")
driver.get(BRAINLY_URL)

time.sleep(3)
print(f"✅ Opened {BRAINLY_URL} successfully.")

# Extract CAPTCHA parameters
dd_data = extract_captcha_params(driver)

if dd_data:
    # Solve CAPTCHA
    solution = solve_captcha(dd_data)

    if solution:
        # Submit the solved CAPTCHA
        submit_captcha(driver, solution)

# Keep browser open for debugging
input("\nPress Enter to exit and close Firefox...")
driver.quit()