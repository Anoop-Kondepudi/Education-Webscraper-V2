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
            
            session = requests.Session()
            for cookie in cookies_data:
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path']
                }
                
                if not cookie.get('session', False):
                    if 'expirationDate' in cookie:
                        cookie_dict['expires'] = cookie['expirationDate']
                
                session.cookies.set(**cookie_dict)
            
            return session.cookies
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading cookies: {e}")
        return None

def generate_html(question_text, answer_html, context):
    """Generate formatted HTML with the provided content."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" async
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>Study.com Answer | Hero Bot</title>
        <style>
            body {{ background-color: #1B1D28; color: white; font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; background: #282E3D; padding: 20px; border-radius: 10px; }}
            .title {{ text-align: center; margin-bottom: 20px; }}
            .contentBox {{ background-color: #FFFFFF; color: #000; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
            img {{ max-width: 100%; height: auto; display: block; margin: 10px auto; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">Study.com Question & Answer | Hero Bot</h1>
            <div class='contentBox'>
                <h2>Question</h2>
                {question_text}
            </div>
            {f'''
            <div class='contentBox'>
                <h2>Explanation</h2>
                {context["explanation"]}
            </div>
            ''' if context else ''}
            <div class='contentBox'>
                <h2>Answer & Explanation</h2>
                {answer_html}
            </div>
        </div>
    </body>
    </html>
    """

def extract_content(html_content):
    """Extract question, answer, and context from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract question
    question_div = soup.find('div', {'ng-non-bindable': True, 'itemprop': 'text'})
    question_text = str(question_div) if question_div else "Question not found"
    
    # Extract answer
    answer_div = soup.find('div', {'test-id': 'answer_content'})
    answer_html = str(answer_div) if answer_div else "<p>Answer not found</p>"
    
    # Extract context (explanation and title)
    context = {}
    holding_company = soup.find('h2', string=lambda text: text and 'Holding Company' in text)
    if holding_company:
        context['title'] = holding_company.get_text(strip=True)
        explanation = holding_company.find_next('p')
        if explanation:
            context['explanation'] = str(explanation)
    
    return question_text, answer_html, context

def scrape_homework_study(url):
    """Scrape content and generate HTML file."""
    try:
        session = requests.Session()
        cookies = load_cookies()
        if cookies:
            session.cookies = cookies
        session.headers.update(get_headers())
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Extract content
        question_text, answer_html, context = extract_content(response.text)
        
        # Generate HTML
        html_content = generate_html(question_text, answer_html, context)
        
        # Create filename from URL
        filename = url.split('/')[-1].replace('.html', '') + '_answer.html'
        output_path = os.path.join(DOWNLOADS_PATH, filename)
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Answer saved to: {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    # Test URL
    test_url = "https://homework.study.com/explanation/the-figure-below-shows-a-front-wheel-driven-vehicle-just-about-to-climb-up-a-slope-in-the-figure-below-t-d-is-the-driving-torque-applied-by-the-engine-to-the-front-wheel-f-dis-the-driving-force-m.html"
    success = scrape_homework_study(test_url)
    
    if not success:
        print("Failed to scrape content.") 