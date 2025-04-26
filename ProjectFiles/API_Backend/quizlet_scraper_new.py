import cloudscraper
import os
import json
from bs4 import BeautifulSoup

# Define downloads path constant
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

def clean_html(html_content):
    """
    First clicks the "Show all steps" button programmatically,
    then removes specified elements from the HTML content
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Define selectors to remove
    selectors_to_remove = [
        "#__next > header",
        "#__next > div.m1nn3s6i > aside.s1wjax6",
        "#mainContainer > main > div > div > div > main > div > section:nth-child(2)",
        "#mainContainer > main > div > div > div > main > div > section",
        "#mainContainer > footer",
        "#mainContainer > main > div > div > div > div > div > div:nth-child(2) > div.t1fxaylt > div.aaaxqvh",
        "#mainContainer > main > div > div > div > main > div > div > div > div > div:nth-child(2) > div > div.no-navigation.b1opuclq",
        # FLASHCARD SELECTORS
        "#setPageSetIntroWrapper > div > div.s11znhi6 > div.s1f9d2ar > div.sz2ipyx",
        "#setPageSetIntroWrapper > div > div.s11znhi6 > div.s14jj5m4",
        "#setPageSetIntroWrapper > div > div.m6zcupd > div.hideBelow--l",
        "#setPageSetIntroWrapper > div > div.m6zcupd > div.c1vv5ssw > div > div > div.m1hdujkg > div > div > div > div.hideBelow--l > div > div.lyzzf1s > div.sfwsws9 > div > label",
        "#setPageSetIntroWrapper > div > div.m6zcupd > div.c1vv5ssw > div > div > div.m1hdujkg > div > div > div > div.hideBelow--l > div > div.lyzzf1s > div.sfwsws9 > label",
        "#setPageSetDetails > div.s8uq31n > div > h3",
        "#setPageSetDetails > div.s8uq31n > div > div.s1vm0q0t",
        "#mainContainer > main > main > div > div.v13b6tlm.s1ji5s9p"
    ]
    
    # Define the "Show all steps" button selector
    show_steps_button_selector = "#mainContainer > main > div > div > div > main > div > div > div > div > div:nth-child(2) > div > div.b1opuclq > div > div.c19lz1jp > div > div > button"
    
    # 1. Add JavaScript to first click the "Show all steps" button, then remove elements
    js_selectors = ',\n        '.join([f"document.querySelector('{selector}')" for selector in selectors_to_remove])
    
    js_content = f"""
    <script type="text/javascript">
    // Function to click the "Show all steps" button
    function clickShowAllStepsButton() {{
        const showStepsButton = document.querySelector('{show_steps_button_selector}');
        if (showStepsButton) {{
            console.log('Found "Show all steps" button, clicking it...');
            showStepsButton.click();
            return true;
        }}
        console.log('Could not find "Show all steps" button');
        return false;
    }}
    
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
    
    // Function that will be called when DOM is ready
    function initializeCleaner() {{
        // First attempt to click the button
        const buttonClicked = clickShowAllStepsButton();
        
        // Set a delay to ensure the button click has time to expand content
        setTimeout(() => {{
            // Try clicking again if it wasn't successful the first time
            if (!buttonClicked) {{
                clickShowAllStepsButton();
            }}
            
            // Then remove unwanted elements
            removeUnwantedElements();
            
            // Set up MutationObserver to detect DOM changes
            const observer = new MutationObserver(function(mutations) {{
                // Don't remove elements that might be part of the expanded steps
                removeUnwantedElements();
            }});
            
            // Start observing once DOM is loaded
            observer.observe(document.body, {{ 
                childList: true, 
                subtree: true 
            }});
            
            // Also run on intervals as backup (less frequently to avoid performance issues)
            setInterval(removeUnwantedElements, 500);
        }}, 1000); // Give the button click time to take effect
    }}
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initializeCleaner);
    }} else {{
        initializeCleaner();
    }}
    
    // Add a backup in case the button appears later
    //setTimeout(initializeCleaner, 2000);
    //setTimeout(initializeCleaner, 3000);
    </script>
    """
    
    # 2. Add CSS to hide these elements (as a backup)
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
    
    # Add the script tag at the end of body
    script_tag = BeautifulSoup(js_content, 'html.parser')
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
    
    # 3. Only remove elements statically that we're sure won't affect functionality
    # We'll let the JavaScript handle the more complex elements
    safe_to_remove_statically = [
        "#__next > header",
        "#__next > div.m1nn3s6i > aside.s1wjax6",
        "#mainContainer > footer"
    ]
    
    for selector in safe_to_remove_statically:
        try:
            elements = soup.select(selector)
            for element in elements:
                if element:
                    element.decompose()
            
            if elements:
                print(f"Statically removed {len(elements)} elements matching: {selector}")
            else:
                print(f"No elements found for static removal: {selector}")
        except Exception as e:
            print(f"Error statically removing '{selector}': {e}")
    
    return str(soup)

def fetch_quizlet_page():
    url = "https://quizlet.com/415105651/practice-lab-3-flash-cards/"

    # Load cookies from JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 
                              "ProjectFiles", "Cookies", "quizlet_cookies.json")
    
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
        "Sec-CH-UA": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-CH-UA-Arch": '"x86"',
        "Sec-CH-UA-Bitness": '"64"',
        "Sec-CH-UA-Full-Version": '"135.0.7049.115"',
        "Sec-CH-UA-Full-Version-List": (
            '"Google Chrome";v="135.0.7049.115", "Not-A.Brand";v="8.0.0.0", '
            '"Chromium";v="135.0.7049.115"'
        ),
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Model": '""',
        "Sec-CH-UA-Platform": '"macOS"',
        "Sec-CH-UA-Platform-Version": '"15.4.1"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.7049.115 Safari/537.36"
        ),
    }

    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    response.raise_for_status()
    
    # Clean HTML by first clicking "Show all steps" then removing specified elements
    cleaned_html = clean_html(response.text)
    
    # Ensure downloads directory exists
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)
    
    # Extract filename from URL
    url_parts = url.strip('/').split('/')
    filename = url_parts[-1] if url_parts else 'page'
    
    # Save only the cleaned HTML to the downloads folder
    cleaned_filename = os.path.join(DOWNLOADS_PATH, f"{filename}.html")
    with open(cleaned_filename, "w", encoding="utf-8") as f:
        f.write(cleaned_html)
    print(f"Saved cleaned HTML to: {os.path.abspath(cleaned_filename)}")

if __name__ == "__main__":
    fetch_quizlet_page()