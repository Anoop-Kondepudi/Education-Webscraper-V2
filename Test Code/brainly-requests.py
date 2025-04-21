import asyncio
from rnet import Client, Impersonate, Proxy
import json
import re
from bs4 import BeautifulSoup

async def scrape_brainly_question(url):
    # Create a client with Chrome browser fingerprint
    client = Client(
        impersonate=Impersonate.Chrome134,  # Use Chrome fingerprint
        cookie_store=True,
        follow_redirects=True,
        timeout=30000
    )
    
    print(f"Scraping Brainly question: {url}")
    
    # Set up headers based on the raw data you provided
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": "\"Chromium\";v=\"134\", \"Google Chrome\";v=\"134\", \"Not-A.Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    
    # First, visit the homepage to get cookies
    print("Step 1: Visiting Brainly homepage to get initial cookies...")
    home_resp = await client.get("https://brainly.com/", headers=headers)
    print(f"Homepage status: {home_resp.status_code}")
    
    # Wait a bit to mimic human behavior
    await asyncio.sleep(2)
    
    # Now visit the question page
    print("Step 2: Visiting the question page...")
    response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    
    # Parse the HTML content
    html_content = await response.text()
    
    # Save the HTML for debugging
    with open('brainly_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Saved HTML to brainly_page.html")
    
    # Check if we got a DataDome challenge
    if "DataDome" in html_content or "captcha" in html_content.lower():
        print("Detected DataDome protection or CAPTCHA challenge")
        
        # Try to bypass by adding DataDome cookies
        print("Step 3: Attempting to bypass DataDome protection...")
        
        # Add DataDome cookies (these are examples, real values would be different)
        client.set_cookies("brainly.com", [
            {"name": "datadome", "value": "q1XbF3HYcGUVs8QGrjuFhXH8j~6Iv1vRN2DBRXHRrfr6Y3TYmVX_yyOy2f4UXlTLM6DDO_Xrr~TPXx6J_uCJfRFl7lT~1UVPDJzJeXFjHKnYG8rkVyDrYT~1UBpAMvKn"},
        ])
        
        # Try again with the cookies
        await asyncio.sleep(2)
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Still failed after DataDome bypass attempt. Status code: {response.status_code}")
            return None
        
        html_content = await response.text()
        
        # Save the HTML after bypass attempt
        with open('brainly_page_after_bypass.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Saved HTML after bypass attempt to brainly_page_after_bypass.html")
        
        # Check if we're still getting a challenge
        if "DataDome" in html_content or "captcha" in html_content.lower():
            print("Still getting DataDome protection after bypass attempt")
            return None
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract question details
    question_data = {}
    
    # Get the question title
    question_title_elem = soup.select_one('h1')
    if question_title_elem:
        question_data['title'] = question_title_elem.get_text(strip=True)
    
    # Get the question asker
    asker_elem = soup.select_one('[data-testid="question_box_header"]')
    if asker_elem:
        asker_text = asker_elem.get_text(strip=True)
        asker_match = re.search(r'Asked by\s+(\w+)', asker_text)
        if asker_match:
            question_data['asker'] = asker_match.group(1)
        
        # Get the question date
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', asker_text)
        if date_match:
            question_data['date'] = date_match.group(1)
    
    # Extract answers
    answers = []
    answer_elements = soup.select('[data-testid="answer_box"]')
    
    for answer_elem in answer_elements:
        answer_data = {}
        
        # Get answer text
        answer_text_elem = answer_elem.select_one('[data-testid="answer_box_text"]')
        if answer_text_elem:
            answer_data['text'] = answer_text_elem.get_text(strip=True)
        
        # Check if answer is verified
        verified_elem = answer_elem.select_one('[data-testid="verified_answer"]')
        answer_data['verified'] = verified_elem is not None
        
        # Get rating
        rating_elem = answer_elem.select_one('[data-testid="rating_stars"]')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+\.\d+)', rating_text)
            if rating_match:
                answer_data['rating'] = float(rating_match.group(1))
        
        # Get number of people helped
        helped_elem = answer_elem.select_one('[data-testid="helped_people"]')
        if helped_elem:
            helped_text = helped_elem.get_text(strip=True)
            helped_match = re.search(r'(\d+)K?', helped_text)
            if helped_match:
                helped_count = helped_match.group(1)
                if 'K' in helped_text:
                    helped_count = float(helped_count) * 1000
                answer_data['people_helped'] = int(helped_count)
        
        # Get answerer name
        answerer_elem = answer_elem.select_one('[data-testid="user_info"]')
        if answerer_elem:
            answerer_text = answerer_elem.get_text(strip=True)
            answerer_match = re.search(r'Answered by\s+(\w+)', answerer_text)
            if answerer_match:
                answer_data['answerer'] = answerer_match.group(1)
        
        answers.append(answer_data)
    
    question_data['answers'] = answers
    
    return question_data

async def main():
    url = "https://brainly.com/question/21951123"
    question_data = await scrape_brainly_question(url)
    
    if question_data:
        # Save the data to a JSON file
        with open('brainly_question.json', 'w', encoding='utf-8') as f:
            json.dump(question_data, f, indent=2)
        print("Data saved to brainly_question.json")
        
        # Print a summary
        print("\nQuestion Summary:")
        print(f"Title: {question_data.get('title', 'N/A')}")
        print(f"Asked by: {question_data.get('asker', 'N/A')}")
        print(f"Date: {question_data.get('date', 'N/A')}")
        print(f"Number of answers: {len(question_data.get('answers', []))}")
        
        # Print the first answer
        if question_data.get('answers'):
            first_answer = question_data['answers'][0]
            print("\nFirst Answer:")
            print(f"Text: {first_answer.get('text', 'N/A')[:100]}...")
            print(f"Verified: {first_answer.get('verified', False)}")
            print(f"Rating: {first_answer.get('rating', 'N/A')}")
            print(f"People helped: {first_answer.get('people_helped', 'N/A')}")
            print(f"Answered by: {first_answer.get('answerer', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())