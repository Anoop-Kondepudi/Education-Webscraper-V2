# Ended up just using inspect eleement and getting the parameters manually.
# Also downloaded the HTML to get the valid link.
# Now using this info, we can properly form the payload/parameters/headers to send to Capsolver API to get the token.
# Thus, this code is now scraped.

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Firefox profile path
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/lzrz03yv.default"

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Keep GUI visible
    options.add_argument(f"-P {FIREFOX_PROFILE_PATH}")  # Use custom profile
    return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

# Start Firefox
driver = setup_driver()

# Pause execution until user presses Enter
input("Manually navigate to the CAPTCHA page, then press Enter to continue...")

# Switch to iframe (if CAPTCHA is inside one)
try:
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)
    print("Switched to iframe.")
except:
    print("No iframe detected. Continuing...")

# Extract gt and challenge values
try:
    gt = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "geetest_gt"))
    ).get_attribute("value")

    challenge = driver.find_element(By.ID, "geetest_challenge").get_attribute("value")

    print(f"\n✅ Extracted gt: {gt}\n✅ Extracted challenge: {challenge}")
except Exception as e:
    print(f"\n❌ Error extracting CAPTCHA parameters: {e}")

# Switch back to main content (if iframe was used)
driver.switch_to.default_content()

# Keep the browser open for debugging
input("\nPress Enter to exit and close Firefox...")
driver.quit()