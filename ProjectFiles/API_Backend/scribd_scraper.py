import time
import os
import json
import requests
import re
from bs4 import BeautifulSoup

# Define paths
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")
COOKIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Cookies", "scribd_cookies.json")

# Function to load Scribd cookies from JSON file
def load_cookies():
    """Loads Scribd cookies from the JSON file if available."""
    try:
        if os.path.exists(COOKIES_PATH):
            with open(COOKIES_PATH, "r", encoding="utf-8") as file:
                cookies_data = json.load(file)
                
            # Convert the cookies to the format expected by requests
            cookies_dict = {}
            for cookie in cookies_data:
                if not cookie.get('session', False) or cookie.get('value'):  # Only use non-session cookies or cookies with values
                    cookies_dict[cookie['name']] = cookie['value']
                    
            print(f"✅ Loaded {len(cookies_dict)} cookies for Scribd")
            return cookies_dict
        else:
            print("ℹ️ No cookies file found. Proceeding without cookies.")
            return {}
    except Exception as e:
        print(f"❌ Failed to load cookies: {str(e)}")
        return {}

# Function to fetch Scribd document using the embed URL
def get_scribd_document(doc_id):
    """Fetches the Scribd document HTML using the embed URL."""
    try:
        session = requests.Session()
        cookies = load_cookies()
        
        # Set cookies to the session
        for name, value in cookies.items():
            session.cookies.set(name, value)
            
        # Construct the embed URL
        embed_url = f'https://www.scribd.com/embeds/{doc_id}/content'
        
        # Add user agent to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"🔄 Fetching Scribd document: {embed_url}")
        response = session.get(embed_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch document: {response.status_code}")
            return None
            
        print(f"✅ Successfully fetched document ({len(response.text)} bytes)")
        return response.text  # Return the raw HTML
    except Exception as e:
        print(f"❌ Error during fetch: {str(e)}")
        return None

# Function to clean and enhance HTML (optional)
def clean_html(html):
    """Cleans and enhances the Scribd HTML (placeholder for future enhancements)."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Add title if doesn't exist
        if not soup.title:
            title_tag = soup.new_tag("title")
            title_tag.string = "Scribd Document"
            if soup.head:
                soup.head.append(title_tag)
            else:
                head_tag = soup.new_tag("head")
                head_tag.append(title_tag)
                soup.insert(0, head_tag)
                
        # You can add more cleaning/enhancement here as needed
        
        print("✅ HTML cleaned and enhanced")
        return str(soup)
    except Exception as e:
        print(f"⚠️ Error cleaning HTML: {str(e)}")
        return html  # Return original HTML if cleaning fails

# Function to save the scraped HTML
def save_document_html(html, doc_id):
    """Saves the scraped Scribd document as an HTML file."""
    # Ensure downloads directory exists
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)
    
    # Create filename with timestamp
    filename = os.path.join(DOWNLOADS_PATH, f"scribd_{doc_id}_{int(time.time())}.html")
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ Scribd document saved as {filename}")
    return filename  # Return the saved file path

# Extract document ID from Scribd URL
def extract_doc_id(url):
    """Extracts the document ID from a Scribd URL."""
    # Match different Scribd URL patterns
    matches = re.findall(r'https:\/\/(?:www\.|id\.|es\.)scribd\.com\/(document|doc|presentation)\/(\d+)\/', url)
    
    if matches and len(matches) > 0:
        _, doc_id = matches[0]  # Get the document ID from the first match
        return doc_id
    
    print("❌ Could not extract document ID from URL")
    return None

# Main function to scrape Scribd
def scrape_scribd(url):
    """Scrapes a Scribd document from the provided URL."""
    print(f"🚀 Processing Scribd URL: {url}")
    
    # Extract document ID from the URL
    doc_id = extract_doc_id(url)
    if not doc_id:
        return None
    
    # Fetch the document HTML
    html_content = get_scribd_document(doc_id)
    if not html_content:
        print("❌ Failed to retrieve document.")
        return None
    
    # Clean and enhance the HTML (optional)
    cleaned_html = clean_html(html_content)
    
    # Save the document
    print("💾 Saving document...")
    return save_document_html(cleaned_html, doc_id)

# Example usage
if __name__ == "__main__":
    # Example Scribd document URL
    scribd_url = "https://www.scribd.com/document/645158549/MODULE-4-PROBLEMS-docx"
    
    result_file = scrape_scribd(scribd_url)
    
    if result_file:
        print(f"🎉 Successfully scraped and saved: {result_file}")
    else:
        print("❌ Failed to scrape Scribd document.") 