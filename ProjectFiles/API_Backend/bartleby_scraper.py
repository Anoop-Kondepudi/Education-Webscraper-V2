import time
import os
import json
import cloudscraper
from bs4 import BeautifulSoup

# Function to load Bartleby cookies from JSON file
def load_cookies():
    """Loads Bartleby cookies from the JSON file."""
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "Cookies", "bartleby_cookies.json")
    
    try:
        with open(cookies_path, "r", encoding="utf-8") as file:
            cookies_data = json.load(file)
            
        # Convert the cookies to the format expected by requests/cloudscraper
        cookies_dict = {}
        for cookie in cookies_data:
            if not cookie.get('session', False) or cookie.get('value'):  # Only use non-session cookies or cookies with values
                cookies_dict[cookie['name']] = cookie['value']
                
        print(f"✅ Loaded {len(cookies_dict)} cookies for Bartleby")
        return cookies_dict
    except Exception as e:
        print(f"❌ Failed to load cookies: {str(e)}")
        return {}

# Function to fetch Bartleby page using Cloudscraper
def get_bartleby_page(url):
    """Fetches the Bartleby page HTML using Cloudscraper with cookies."""
    try:
        scraper = cloudscraper.create_scraper()
        cookies = load_cookies()
        
        # Set cookies to the scraper session
        for name, value in cookies.items():
            scraper.cookies.set(name, value)
        
        response = scraper.get(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: {response.status_code}")
            return None
            
        print(f"✅ Successfully fetched page ({len(response.text)} bytes)")
        return response.text  # Return the raw HTML
    except Exception as e:
        print(f"❌ Error during fetch: {str(e)}")
        return None

# Function to clean HTML by removing specified selectors
def clean_html(html):
    """Removes specified selectors from the HTML."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # List of selectors to remove
        selectors_to_remove = [
            "#APP_LAYOUT_STICKY_CONTAINER_ID",
            "#APP_LAYOUT_RAILS_CONTAINER_ID > div > div.styles__AppLayoutBaseRailWithMargins-sc-ef9b07f2-13.styles__AppLayoutMainContentLeftToTopRotationRail-sc-ef9b07f2-14.ewrpEf.fqCnEe",
            "#Expert-Solution > div.styles__QuestionWithAnswerContainer-sc-3354f32b-0.iwINRK > div.styles__QuestionHeadingContainer-sc-3354f32b-23.cQzfmR > div.styles__QuestionHeadingWithShareSolution-sc-3354f32b-22.fYRcWH > div.styles__QuestionHeaderWrapper-sc-3354f32b-1.iUpVmK > img",
            "#Expert-Solution > div.styles__QuestionWithAnswerContainer-sc-3354f32b-0.iwINRK > div.styles__QuestionHeadingContainer-sc-3354f32b-23.cQzfmR > div.styles__QuestionHeadingWithShareSolution-sc-3354f32b-22.fYRcWH > div.styles__QuestionHeaderWrapper-sc-3354f32b-1.iUpVmK > div.styles__CertificationLabel-sc-3354f32b-11.eiVyjT",
            "#qna-answer-container-id > div.styles__QuestionWithAnswerContainer-sc-3354f32b-0.iwINRK > div.styles__QuestionHeadingContainer-sc-3354f32b-23.cQzfmR > div.styles__QuestionHeadingWithShareSolution-sc-3354f32b-22.fYRcWH > div.styles__QuestionHeaderWrapper-sc-3354f32b-1.Qgpse > div.styles__IconFeaturesContainer-sc-86dceb8-0.dagFwz",
            "#qna-answer-container-id > div.styles__BookmarkButtonContainer-sc-70138c7b-13.knplcx",
            "#Expert-Solution > div.styles__MyAnswerStepsWrapper-sc-251af6e9-1.kiDDqr > div.styles__MyAnswerBottomContainer-sc-251af6e9-2.McIdp",
            "#APP_LAYOUT_NO_RAILS_CONTAINER_ID",
            "#bartleby-main > div.styles__AppLayoutFooter-sc-ef9b07f2-12.cAaTIY"
        ]
        
        # Remove each selector
        for selector in selectors_to_remove:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
                
        print(f"✅ Removed {len(selectors_to_remove)} selector patterns from HTML")
        return str(soup)
    except Exception as e:
        print(f"⚠️ Error cleaning HTML: {str(e)}")
        return html  # Return original HTML if cleaning fails

# Function to save the scraped HTML
def save_page_html(html, url):
    """Saves the scraped Bartleby page as an HTML file."""
    # Extract a portion of the URL to use in the filename
    url_part = url.split('/')[-1] if '/' in url else 'page'
    filename = os.path.join(os.path.dirname(__file__), f"bartleby_{url_part}_{int(time.time())}.html")
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ Bartleby page saved as {filename}")
    return filename  # Return the saved file path

# Main function to scrape Bartleby
def scrape_bartleby(url):
    """Uses Cloudscraper to get Bartleby HTML with cookies."""
    print(f"🚀 Fetching Bartleby page: {url}")
    raw_html = get_bartleby_page(url)
    
    if not raw_html:
        print("❌ Failed to retrieve page with Cloudscraper.")
        return None
    
    print("🔍 Cleaning HTML...")
    cleaned_html = clean_html(raw_html)
    
    print("💾 Saving page content...")
    return save_page_html(cleaned_html, url)

# Example usage
if __name__ == "__main__":
    # Example Bartleby question URL
    bartleby_url = "https://www.bartleby.com/questions-and-answers/give-grievances-process/f912112a-7717-4553-8990-3af5cf4ced3c"
    
    formatted_result = scrape_bartleby(bartleby_url)
    
    if formatted_result:
        print(f"🎉 Successfully scraped and saved: {formatted_result}")
    else:
        print("❌ Failed to scrape Bartleby page.") 