import os
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

# Use the same Downloads path as the original scraper
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "../Cookies/homeworkstudy_cookies.json")
IMAGES_PATH = os.path.join(DOWNLOADS_PATH, "images")

# Create images directory if it doesn't exist
os.makedirs(IMAGES_PATH, exist_ok=True)

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

def download_image(session, img_url, base_url):
    """Download image and return local path."""
    try:
        if img_url.startswith('/'):
            img_url = f"https://study.com{img_url}"
        elif not img_url.startswith(('http://', 'https://')):
            img_url = f"{base_url}/{img_url}"

        response = session.get(img_url, stream=True)
        response.raise_for_status()

        # Create a filename from the URL
        img_filename = os.path.basename(img_url.split('?')[0])
        local_path = os.path.join(IMAGES_PATH, img_filename)

        # Save the image
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"images/{img_filename}"
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
        return img_url

def process_math_equations(html_content):
    """Convert {eq} tags to MathJax format."""
    # Replace {eq}...{/eq} with \(...\)
    html_content = re.sub(r'\{eq\}(.*?)\{/eq\}', r'\\(\1\\)', html_content, flags=re.DOTALL)
    return html_content

def process_content(content, session, base_url):
    """Process HTML content to fix images and equations."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Download and update image sources
    for img in soup.find_all('img'):
        if img.get('src'):
            local_path = download_image(session, img['src'], base_url)
            img['src'] = local_path

    # Convert to string and process equations
    processed_content = str(soup)
    processed_content = process_math_equations(processed_content)
    
    return processed_content

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
            .imageplugin {{ margin: 15px 0; }}
            .imageplugin img {{ max-width: 100%; }}
            .imageplugin caption {{ text-align: center; margin-top: 5px; }}
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
        <script>
            MathJax.Hub.Config({{
                tex2jax: {{
                    inlineMath: [['\\\\(','\\\\)']],
                    displayMath: [['\\\\[','\\\\]']],
                    processEscapes: true
                }}
            }});
        </script>
    </body>
    </html>
    """

def extract_content(html_content, session, base_url):
    """Extract question, answer, and context from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract question
    question_div = soup.find('div', {'ng-non-bindable': True, 'itemprop': 'text'})
    question_text = process_content(str(question_div), session, base_url) if question_div else "Question not found"
    
    # Extract answer
    answer_div = soup.find('div', {'test-id': 'answer_content'})
    answer_html = process_content(str(answer_div), session, base_url) if answer_div else "<p>Answer not found</p>"
    
    # Extract context
    context = {}
    holding_company = soup.find('h2', string=lambda text: text and 'Holding Company' in text)
    if holding_company:
        context['title'] = holding_company.get_text(strip=True)
        explanation = holding_company.find_next('p')
        if explanation:
            context['explanation'] = process_content(str(explanation), session, base_url)
    
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
        
        # Get base URL for relative paths
        base_url = '/'.join(url.split('/')[:3])
        
        # Extract content
        question_text, answer_html, context = extract_content(response.text, session, base_url)
        
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