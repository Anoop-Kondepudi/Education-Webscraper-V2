import time
import os
import cloudscraper
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Proxy Configuration (with authentication)
PROXY_HOST = "12.176.171.19"
PROXY_PORT = "8080"
PROXY_USER = "wr37kDWXUGoa"
PROXY_PASS = "USMuWej9iXz8"

PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# Function to initialize Selenium WebDriver with proxy authentication
def setup_driver():
    """Sets up Firefox WebDriver for Selenium with proxy authentication."""
    options = webdriver.FirefoxOptions()
    options.headless = True  # Runs in the background
    options.add_argument("--headless")

    # Set proxy for Firefox (but Firefox doesn't support authentication in prefs, so manual workaround needed)
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.http", PROXY_HOST)
    options.set_preference("network.proxy.http_port", int(PROXY_PORT))
    options.set_preference("network.proxy.ssl", PROXY_HOST)
    options.set_preference("network.proxy.ssl_port", int(PROXY_PORT))

    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    service = FirefoxService(GeckoDriverManager().install(), log_output=None)
    driver = webdriver.Firefox(service=service, options=options)
    
    return driver

# Function to get Brainly HTML using Cloudscraper with Proxy Authentication
def get_brainly_page(url):
    """Fetches the Brainly page HTML using Cloudscraper with a proxy and authentication."""
    scraper = cloudscraper.create_scraper()

    proxies = {
        "http": PROXY_URL
    }

    response = scraper.get(url, proxies=proxies)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page with Cloudscraper: {response.status_code}")
        return None

    return response.text  # Return the raw HTML (without JS execution)

# Function to render JavaScript with Selenium
def render_with_selenium(html):
    """Loads Cloudscraper HTML into Selenium to execute JavaScript."""
    driver = setup_driver()

    # Load the raw HTML into Selenium
    driver.get("data:text/html;charset=utf-8," + html)
    time.sleep(5)  # Allow JavaScript to execute

    # Get the fully rendered HTML
    rendered_html = driver.page_source
    driver.quit()
    
    return rendered_html

# Function to save the final HTML after JS execution
def save_page_html(html):
    """Saves the fully loaded Brainly page as an HTML file."""
    filename = os.path.join(os.path.dirname(__file__), f"brainly_page_{int(time.time())}.html")
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ Brainly page saved as {filename}")
    return filename  # Return the saved file path

# Main function to scrape Brainly
def scrape_brainly(url):
    """Uses Cloudscraper + Selenium + Proxy Authentication to get full Brainly HTML."""
    print("🚀 Fetching Brainly page using Cloudscraper (with Proxy Auth)...")
    raw_html = get_brainly_page(url)
    
    if not raw_html:
        print("❌ Failed to retrieve page with Cloudscraper.")
        return None
    
    print("🌐 Rendering page in Selenium to load JavaScript...")
    full_html = render_with_selenium(raw_html)
    
    print("🔍 Saving final page...")
    return save_page_html(full_html)

# Example usage
if __name__ == "__main__":
    brainly_url = "https://brainly.com/question/123456"  # Replace with an actual Brainly URL
    formatted_result = scrape_brainly(brainly_url)
    
    if formatted_result:
        print(f"🎉 Successfully scraped: {formatted_result}")