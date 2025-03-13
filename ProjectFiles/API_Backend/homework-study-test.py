import os
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Use the same Downloads path as the original scraper
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/homeworkstudy_cookies.json")

def get_headers():
    """Generate headers with a random user agent."""
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def load_cookies():
    """Load cookies from the JSON file and convert to requests.cookies format."""
    try:
        with open(COOKIES_PATH, 'r') as f:
            cookies_data = json.load(f)
            
            # Create a new requests session and update its cookies
            session = requests.Session()
            for cookie in cookies_data:
                # Convert EditThisCookie format to requests format
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path']
                }
                
                # Add optional attributes if they exist
                if not cookie.get('session', False):  # Only add if not a session cookie
                    if 'expirationDate' in cookie:
                        cookie_dict['expires'] = cookie['expirationDate']
                
                # Create the cookie in the session
                session.cookies.set(**cookie_dict)
            
            return session.cookies
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading cookies: {e}")
        return None

def extract_content(html_content):
    """Extract question, answer, and context from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract question
    question_div = soup.find('div', {'ng-non-bindable': True}, string=True)
    question = question_div.get_text(strip=True) if question_div else None
    
    # Extract answer
    answer_div = soup.find('div', {'test-id': 'answer_content'})
    answer = str(answer_div) if answer_div else None
    
    # Extract context
    context = {}
    basic_addition = soup.find('h2', string='Basic Addition:')
    if basic_addition:
        context['title'] = basic_addition.get_text(strip=True)
        explanation = basic_addition.find_next('p')
        if explanation:
            context['explanation'] = str(explanation)
    
    return {
        'question': question,
        'answer': answer,
        'context': context
    }

def scrape_homework_study(url):
    """Scrape static HTML using requests."""
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Load and add cookies
        cookies = load_cookies()
        if cookies:
            session.cookies = cookies
        
        # Add headers to mimic a real browser
        session.headers.update(get_headers())
        
        # Make the request
        response = session.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Extract content
        content = extract_content(response.text)
        return content
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    finally:
        session.close()

if __name__ == "__main__":
    # Test URL
    test_url = "https://homework.study.com/explanation/separate-income-statements-of-quail-corp-and-its-80-owned-subsidiary-savannah-corp-for-2016-are-as-follows-quail-savannah-sales-rev-800-000-300-000-gain-on-equipment-35-000-cost-of-sales-4000.html"
    content = scrape_homework_study(test_url)
    
    if content:
        print(json.dumps(content, indent=2)) 