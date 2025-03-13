import json
import os
import cloudscraper
from bs4 import BeautifulSoup
import time
import re

# Path to cookies file
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/quizlet_cookies.json")

# Path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

# List of CSS selectors to remove (but NOT blocking JavaScript)
REMOVE_SELECTORS = [
    "#__next > header",
    "#__next > div.SiteUnsupportedBrowserAlertBanner",
    "#__next > div.m1nn3s6i > aside.s1bcqqqo",
    "#mainContainer > main > div > div > div > main > div > section:nth-child(2)",
    "#mainContainer > main > div > div > div > main > div > section",
    "#mainContainer > footer",
    "#mainContainer > main > div > div > div > div > div > div:nth-child(2) > div.t1fxaylt > div.aaaxqvh"
]

# Custom JavaScript to continuously remove unwanted elements (while keeping JS-enabled)
# JavaScript to click "Show All Steps" and remove unwanted elements
JS_SCRIPT = """
<script>
    function removeElements() {
        let selectors = [
            "#__next > header",
            "#__next > div.SiteUnsupportedBrowserAlertBanner",
            "#__next > div.m1nn3s6i > aside.s1bcqqqo",
            "#mainContainer > main > div > div > div > main > div > section:nth-child(2)",
            "#mainContainer > main > div > div > div > main > div > section",
            "#mainContainer > footer",
            "#mainContainer > main > div > div > div > div > div > div:nth-child(2) > div.t1fxaylt > div.aaaxqvh"
        ];
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => el.remove());
        });
    }

    function clickShowAllSteps() {
        let button = document.querySelector("button");  // Adjust this if needed
        if (button && button.innerText.includes("Show All Steps")) {
            button.click();
            console.log("✅ Clicked 'Show All Steps' button!");
        } else {
            console.log("⚠️ 'Show All Steps' button not found.");
        }
    }

    // Click the button first, then remove elements
    setTimeout(clickShowAllSteps, 1000);  // Click after 1 second
    setTimeout(removeElements, 2000);  // Remove elements after 2 seconds
    setInterval(removeElements, 500);  // Keep cleaning every 500ms
</script>
"""

def load_cookies():
    """Loads cookies from JSON into a dictionary for Cloudscraper"""
    try:
        with open(COOKIES_PATH, "r", encoding="utf-8") as file:
            cookies = json.load(file)
        
        # Convert cookies into a dictionary format for Cloudscraper
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        print("✅ Cookies loaded successfully!")
        return cookie_dict

    except FileNotFoundError:
        print(f"❌ ERROR: Cookies file not found at {COOKIES_PATH}. Please check the file location!")
        return {}

    except Exception as e:
        print(f"⚠️ Failed to load cookies: {e}")
        return {}

def clean_html(html):
    """Injects JavaScript into the fully loaded Quizlet HTML"""
    soup = BeautifulSoup(html, "html.parser")

    # Inject the custom JavaScript at the end of <body>
    if soup.body:
        soup.body.append(BeautifulSoup(JS_SCRIPT, "html.parser"))

    return str(soup)

def scrape_quizlet(url):
    """Scrapes Quizlet page using Cloudscraper and injects JavaScript for cleanup"""
    scraper = cloudscraper.create_scraper()

    # Load cookies and add them to the request
    cookies = load_cookies()
    
    # Load the page with JavaScript enabled (Cloudscraper allows JS execution)
    response = scraper.get(url, cookies=cookies)

    # Inject JavaScript to remove unwanted elements AFTER page fully loads
    final_html = clean_html(response.text)

    # Create a more descriptive filename based on URL
    # Extract question ID or set name from URL if possible
    match = re.search(r'\/([^\/]+?)(?:-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})?$', url)
    if match:
        file_id = match.group(1)
    else:
        file_id = str(int(time.time()))  # Use timestamp as fallback
    
    filename = f"quizlet_{file_id}.html"
    filepath = os.path.join(DOWNLOADS_PATH, filename)
    
    # Ensure the Downloads directory exists
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)
    
    # Save the formatted HTML
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(final_html)

    print(f"✅ Cleaned HTML saved as {filename} in {DOWNLOADS_PATH}")
    return filepath

if __name__ == "__main__":
    # Test URL - you can change this for testing different Quizlet pages
    test_url = "https://quizlet.com/415105651/practice-lab-3-flash-cards/"
    print(f"🚀 Testing Quizlet scraper with URL: {test_url}")
    
    # Run the scraper
    output_file = scrape_quizlet(test_url)
    
    print(f"\n✅ Quizlet scraping complete!")
    print(f"✅ Output saved as: {output_file}")