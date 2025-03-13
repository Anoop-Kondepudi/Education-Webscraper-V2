import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Use the same Downloads path as the Brainly scraper
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

def setup_driver():
    """Set up minimal Firefox WebDriver."""
    options = webdriver.FirefoxOptions()
    options.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False)
    options.profile = profile
    return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

def scrape_homework_study(url):
    """Scrape static HTML as fast as possible."""
    driver = setup_driver()
    try:
        driver.get(url)
        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return None

if __name__ == "__main__":
    # Test URL
    test_url = "https://homework.study.com/explanation/what-is-2-2.html"
    html_content = scrape_homework_study(test_url)
    if html_content:
        output_path = os.path.join(DOWNLOADS_PATH, "homework_study_test.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML content saved to: {output_path}")
