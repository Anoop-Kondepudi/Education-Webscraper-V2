import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import requests

def process_turnitin_task(task_id, input_data):
    """
    Process a Turnitin task using the provided input data.
    """
    # Define the URL to navigate to
    url = "https://scopedlens.com/self-service/submission/create"
    
    # Path to the Firefox profile
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/q4q811t1.turnitin"
    
    # Path to the cookies file
    cookies_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "Cookies", "turnitin_cookies.json")
    
    # Path to the Reports folder
    reports_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
    os.makedirs(reports_folder, exist_ok=True)  # Ensure the Reports folder exists
    
    # Set up Firefox options with the specified profile
    options = Options()
    options.profile = firefox_profile_path
    options.add_argument("--headless")  # Enable headless mode

    # Initialize Firefox browser
    driver = webdriver.Firefox(options=options)
    
    try:
        # Navigate to the domain to set cookies
        driver.get("https://scopedlens.com")
        
        # Load and set cookies
        with open(cookies_file_path, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            # Remove potential problematic attributes
            cookie.pop('sameSite', None)
            cookie.pop('storeId', None)
            cookie.pop('id', None)
            driver.add_cookie(cookie)
        
        # Navigate to the target URL
        driver.get(url)
        
        # Wait for and get the quota information
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h6')))
        quota_element = driver.find_element(By.XPATH, '/html/body/div/div/div/h6')
        quota_text = quota_element.text
        
        # Extract quota numbers
        quota_numbers = re.search(r'(\d+\s*/\s*\d+)', quota_text)
        quota_value = quota_numbers.group(1).replace(" ", "") if quota_numbers else "Unknown"
        
        # Select the region
        region_choice = input_data.get("region", "1")
        if region_choice == "1":
            driver.execute_script("document.querySelector('#id_region_0').click();")
        elif region_choice == "2":
            driver.execute_script("document.querySelector('#id_region_1').click();")
        else:
            raise ValueError("Invalid region choice")
        
        # Download the document from the provided URL
        file_url = input_data.get("file_url")
        doc_path = os.path.join(reports_folder, f"{task_id}_uploaded_file")
        response = requests.get(file_url)
        with open(doc_path, "wb") as f:
            f.write(response.content)
        
        # Upload the document
        upload_element = driver.find_element(By.XPATH, '//*[@id="id_upload_document"]')
        upload_element.send_keys(doc_path)
        
        # Apply exclusion options
        exclusion_choice = input_data.get("exclusion_options", "1")
        driver.execute_script(f"document.querySelector('#id_exclude_bibliography').checked = {exclusion_choice in ['2', '3']};")
        driver.execute_script(f"document.querySelector('#id_exclude_quotes').checked = {exclusion_choice in ['2', '4']};")
        
        # Apply small matches method
        small_matches_choice = input_data.get("small_matches_method", "1")
        if small_matches_choice == "2":
            word_count = input_data.get("small_matches_value", 0)
            driver.execute_script(f"document.querySelector('#id_exclude_small_matches_value_words').value = {word_count};")
        elif small_matches_choice == "3":
            percentage_value = input_data.get("small_matches_value", 0)
            driver.execute_script(f"document.querySelector('#id_exclude_small_matches_value_percentage').value = {percentage_value};")
        
        # Select report options
        report_choice = input_data.get("report_type", "1")
        include_similarity = report_choice in ["2", "3"]
        include_ai = report_choice in ["1", "3"]
        
        # Submit the form
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit-button"]')))
        driver.execute_script("document.querySelector('#submit-button').click();")
        
        # Monitor the status after submission
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[5]')))
        status = ""
        start_time = time.time()
        
        while True:
            status_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[5]')
            status = status_element.text.strip()
            
            if status == "SUCCESS":
                # Navigate to the details page
                details_link = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[1]/a')
                details_url = details_link.get_attribute("href")
                driver.get(details_url)
                
                # Extract report data
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')))
                similarity_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')
                similarity_text = similarity_element.text.strip()
                similarity_percentage = similarity_text.split("%")[0] + "%" if "%" in similarity_text else "N/A"
                
                ai_index_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[5]/td')
                ai_index_text = ai_index_element.text.strip()
                ai_content_percentage = ai_index_text.split("%")[0] + "%" if "%" in ai_index_text else "N/A"
                
                # Save the report data
                report_data = {
                    "Quota": quota_value,
                    "Similarity % Content": similarity_percentage,
                    "AI % Content": ai_content_percentage
                }
                report_file_path = os.path.join(reports_folder, f"{task_id}.json")
                with open(report_file_path, "w") as report_file:
                    json.dump(report_data, report_file, indent=4)
                break
            elif status not in ["STARTED", "PENDING", ""]:
                raise Exception(f"Processing failed with status: {status}")
            
            time.sleep(1)
    
    except Exception as e:
        # Save the error to the JSON file
        error_report = {"Error": str(e)}
        report_file_path = os.path.join(reports_folder, f"{task_id}.json")
        with open(report_file_path, "w") as report_file:
            json.dump(error_report, report_file, indent=4)
    
    finally:
        driver.quit()