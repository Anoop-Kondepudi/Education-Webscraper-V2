import time
import os
import cloudscraper

# Function to fetch Homework.Study.com page using Cloudscraper
def get_homework_page(url):
    """Fetches the Homework.Study.com page HTML using Cloudscraper."""
    scraper = cloudscraper.create_scraper()

    response = scraper.get(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page with Cloudscraper: {response.status_code}")
        return None

    return response.text  # Return the raw HTML

# Function to save the scraped HTML
def save_page_html(html):
    """Saves the scraped Homework.Study.com page as an HTML file."""
    filename = os.path.join(os.path.dirname(__file__), f"homework_page_{int(time.time())}.html")
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ Homework.Study.com page saved as {filename}")
    return filename  # Return the saved file path

# Main function to scrape Homework.Study.com
def scrape_homework(url):
    """Uses Cloudscraper to get Homework.Study.com HTML."""
    print("🚀 Fetching Homework.Study.com page using Cloudscraper...")
    raw_html = get_homework_page(url)
    
    if not raw_html:
        print("❌ Failed to retrieve page with Cloudscraper.")
        return None
    
    print("🔍 Saving final page...")
    return save_page_html(raw_html)

# Example usage
if __name__ == "__main__":
    homework_url = "https://homework.study.com/question/123456"  # Replace with actual Homework.Study.com URL
    formatted_result = scrape_homework(homework_url)
    
    if formatted_result:
        print(f"🎉 Successfully scraped: {formatted_result}")
