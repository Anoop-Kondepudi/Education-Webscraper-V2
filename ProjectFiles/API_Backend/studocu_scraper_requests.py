import cloudscraper
import os
import json
from bs4 import BeautifulSoup

def clean_html(html_content):
    """
    Remove specified elements from the HTML content and add CSS/JavaScript
    to prevent them from respawning
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Define selectors to remove
    selectors_to_remove = [
        "#header-position-handle",
        "#onetrust-consent-sdk",
        "#viewer-wrapper > div._f8ee41b9198f",
        "#page-container > div:nth-child(8) > div",
        "#main-wrapper > div._06ef8c092b85._7bd920b7ff0c > div > div._abc22daaacf0 > div._be945ce042ab._6f3dca40cabd._df890a73cf52._51b4ea13e1fb",
        "#sidebar",
        "#main-wrapper > div._06ef8c092b85._7bd920b7ff0c > aside > button",
        "#viewer-wrapper > div._f677a7fe81a8._2ff01c1a5338 > div._e8ed7581cbdb"        
    ]
    
    # 1. First remove elements statically with BeautifulSoup
    for selector in selectors_to_remove:
        try:
            elements = soup.select(selector)
            for element in elements:
                if element:
                    element.decompose()
            
            if elements:
                print(f"Removed {len(elements)} elements matching: {selector}")
            else:
                print(f"No elements found for selector: {selector}")
        except Exception as e:
            print(f"Error processing selector '{selector}': {e}")
    
    # 2. Add CSS to hide these elements permanently
    css_content = "\n".join([f"{selector} {{ display: none !important; visibility: hidden !important; }}" 
                            for selector in selectors_to_remove])
    
    style_tag = soup.new_tag("style")
    style_tag["type"] = "text/css"
    style_tag.string = css_content
    
    # Add the style tag to the head
    if soup.head:
        soup.head.append(style_tag)
    else:
        # Create head if it doesn't exist
        head_tag = soup.new_tag("head")
        head_tag.append(style_tag)
        if soup.html:
            soup.html.insert(0, head_tag)
        else:
            soup.append(head_tag)
    
    # 3. Add JavaScript to continually remove these elements
    js_selectors = ',\n        '.join([f"document.querySelector('{selector}')" for selector in selectors_to_remove])
    
    js_content = f"""
    <script type="text/javascript">
    // Function to remove unwanted elements
    function removeUnwantedElements() {{
        const elementsToRemove = [
        {js_selectors}
        ];
        
        for (const element of elementsToRemove) {{
            if (element) {{
                element.remove();
            }}
        }}
    }}
    
    // Run immediately
    removeUnwantedElements();
    
    // Set up MutationObserver to detect DOM changes
    const observer = new MutationObserver(function(mutations) {{
        removeUnwantedElements();
    }});
    
    // Start observing once DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {{
        observer.observe(document.body, {{ 
            childList: true, 
            subtree: true 
        }});
        
        // Also run on intervals as backup
        setInterval(removeUnwantedElements, 500);
    }});
    
    // Fallback for immediate action
    setTimeout(removeUnwantedElements, 0);
    setTimeout(removeUnwantedElements, 500);
    setTimeout(removeUnwantedElements, 1000);
    setTimeout(removeUnwantedElements, 2000);
    </script>
    """
    
    script_tag = BeautifulSoup(js_content, 'html.parser')
    
    # Add the script tag at the end of body
    if soup.body:
        soup.body.append(script_tag)
    else:
        # Create body if it doesn't exist (unlikely but just in case)
        body_tag = soup.new_tag("body")
        body_tag.append(script_tag)
        if soup.html:
            soup.html.append(body_tag)
        else:
            soup.append(body_tag)
    
    return str(soup)

def fetch_studocu_document():
    url = (
        "https://www.studocu.com/en-us/document/"
        "truong-dai-hoc-su-pham-thai-nguyen/su-pham-ngu-van/"
        "chuyen-de-2-nlxh-nghi-luan-xa-hoi-cac-lam-hay-va-chi-tiet/"
        "111501672?origin=home-recent-1"
    )

    # Load cookies from JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 
                             "ProjectFiles", "Cookies", "studocu_cookies.json")
    
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        cookie_string = ""
        for cookie in cookies_data:
            # Skip empty values and session cookies that are marked as session=true
            if cookie.get('value') and not (cookie.get('session', False) is True):
                if cookie_string:
                    cookie_string += "; "
                cookie_string += f"{cookie['name']}={cookie['value']}"
        
        print(f"Successfully loaded cookies from: {cookies_path}")
    except Exception as e:
        print(f"Error loading cookies: {e}")
        # Fallback to empty cookie string if something goes wrong
        cookie_string = ""

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Cookie": cookie_string,
        "Priority": "u=0,i",
        "Referer": "https://www.studocu.com/en-us/home",
        "Sec-CH-UA": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        ),
    }

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    response.raise_for_status()
    
    # Clean HTML by removing specified elements
    cleaned_html = clean_html(response.text)
    
    # Define downloads directory
    DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)
    
    # Extract filename from URL
    url_parts = url.strip('/').split('/')
    filename = url_parts[-1].split('?')[0] if url_parts else 'studocu_document'
    
    # Save the document
    document_path = os.path.join(DOWNLOADS_PATH, f"{filename}.html")
    with open(document_path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)
    
    print(f"Saved cleaned document to: {os.path.abspath(document_path)}")

if __name__ == "__main__":
    fetch_studocu_document()
