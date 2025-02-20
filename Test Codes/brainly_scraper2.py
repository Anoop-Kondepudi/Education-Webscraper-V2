import json
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

# Path to cookies file
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/brainly_cookies.json")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.FirefoxOptions()
    options.headless = False  # Show GUI
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

# Load cookies into the browser
def load_cookies(driver):
    try:
        with open(COOKIES_PATH, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Cookies loaded successfully!")
    except Exception as e:
        print(f"⚠️ Failed to load cookies: {e}")

# Wait for page to fully render
def wait_for_page_load(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Give extra time for JavaScript rendering
    except Exception as e:
        print(f"⚠️ Page load timeout: {e}")

# Download images and replace URLs
def download_image(image_url):
    try:
        if not image_url.startswith("http"):
            print(f"⚠️ Skipping invalid image URL: {image_url}")
            return image_url  # Skip non-http URLs
        
        img_name = image_url.split("/")[-1]  # Extract filename
        img_path = os.path.join(IMAGE_DIR, img_name)
        
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(img_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"✅ Image saved: {img_path}")
            return f"file://{img_path}"  # Use absolute file path in HTML
        else:
            print(f"⚠️ Failed to download image: {image_url}")
            return image_url  # Keep original URL if download fails
    except Exception as e:
        print(f"⚠️ Image download error: {e}")
        return image_url  # Fallback to original URL

# Extract question and answers
def extract_content(driver):
    try:
        question_element = driver.find_element(By.CSS_SELECTOR, "#main-content > section > div > div > div:nth-child(1) > div")
        question = question_element.get_attribute("innerHTML")
    except Exception as e:
        print(f"⚠️ Failed to extract question: {e}")
        question = "Question not found"
    
    try:
        answer_element = driver.find_element(By.CSS_SELECTOR, "#main-content > div:nth-child(2) > div > div > div > section")
        answers = answer_element.get_attribute("innerHTML")
    except Exception as e:
        print(f"⚠️ Failed to extract answers: {e}")
        answers = "Answers not found"
    
    return question, answers

# Update image sources to local files
def update_image_sources(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url:
            local_img_path = download_image(img_url)
            img["src"] = local_img_path  # Update image src in HTML
            
    return str(soup)

# Save extracted content to HTML
def save_custom_html(question, answers):
    filename = os.path.join(os.path.dirname(__file__), f"brainly_extracted_{int(time.time())}.html")
    question = update_image_sources(question)
    answers = update_image_sources(answers)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Brainly Extracted Content</title>
    </head>
    <body>
        <h1>Question</h1>
        <div>{question}</div>
        <h2>Answers</h2>
        <div>{answers}</div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"✅ Extracted content saved as {filename}")
    return filename

# Main function to scrape Brainly page
def scrape_brainly(url):
    driver = setup_driver()
    driver.get("https://www.brainly.com/")  # Load Brainly home page first

    # Load cookies for login session
    load_cookies(driver)
    driver.refresh()
    time.sleep(3)

    print("✅ Logged in using saved cookies!")

    driver.get(url)
    wait_for_page_load(driver)
    
    # Extract question and answers
    question, answers = extract_content(driver)
    
    # Save custom HTML
    html_file = save_custom_html(question, answers)
    
    # Close the browser
    driver.quit()
    
    return html_file  # Return the saved file path

# Run script
if __name__ == "__main__":
    test_url = "https://brainly.com/question/48003838"  # Hardcoded Brainly link
    html_file = scrape_brainly(test_url)
    print(f"Downloaded formatted HTML file: {html_file}")
