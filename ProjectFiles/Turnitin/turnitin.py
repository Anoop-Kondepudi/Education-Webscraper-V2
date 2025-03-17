import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

def navigate_to_turnitin():
    # Define the URL to navigate to
    url = "https://scopedlens.com/self-service/submission/create"
    
    # Path to the Firefox profile
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/q4q811t1.turnitin"
    
    # Path to the cookies file
    cookies_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "Cookies", "turnitin_cookies.json")
    
    # Set up Firefox options with the specified profile
    options = Options()
    options.profile = firefox_profile_path
    
    # Initialize Firefox browser
    driver = webdriver.Firefox(options=options)
    
    try:
        # First, navigate to the domain (needed to set cookies properly)
        driver.get("https://scopedlens.com")
        
        # Load and set cookies
        with open(cookies_file_path, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            # Remove potential problematic attributes that browser might reject
            if 'sameSite' in cookie:
                del cookie['sameSite']
            if 'storeId' in cookie:
                del cookie['storeId']
            if 'id' in cookie:
                del cookie['id']
            
            driver.add_cookie(cookie)
        
        # Now navigate to the target URL
        driver.get(url)
        
        # Wait for and get the quota information
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h6')))
        quota_element = driver.find_element(By.XPATH, '/html/body/div/div/div/h6')
        quota_text = quota_element.text
        
        # Extract just the quota numbers (e.g., "0/50")
        quota_numbers = re.search(r'(\d+\s*/\s*\d+)', quota_text)
        if quota_numbers:
            quota_value = quota_numbers.group(1).replace(" ", "")  # Remove any spaces
        else:
            quota_value = "Unknown"
        
        # Display the quota information
        print(f"Quota: {quota_value}")
        
        # Wait for the options to be available
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_region_0"]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_region_1"]')))
        
        # Ask the user which region they want to select
        choice = input("Select a Region:\n1. International\n2. United Kingdom\nEnter 1 or 2: ")
        
        # Select the appropriate option based on user input
        if choice == "1":
            international_option = driver.find_element(By.XPATH, '//*[@id="id_region_0"]')
            international_option.click()
            print("Selected: International")
        elif choice == "2":
            uk_option = driver.find_element(By.XPATH, '//*[@id="id_region_1"]')
            uk_option.click()
            print("Selected: United Kingdom")
        else:
            print("Invalid choice. Please enter 1 or 2.")
        
        # Wait for the upload element to be available
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_upload_document"]')))
        
        # Ask for the document path to upload
        doc_path = input("Enter the full path to the document you want to upload: ")
        
        # Check if the file exists
        if not os.path.exists(doc_path):
            print(f"Error: File not found at {doc_path}")
        else:
            # Send the file path to the upload input
            upload_element = driver.find_element(By.XPATH, '//*[@id="id_upload_document"]')
            upload_element.send_keys(doc_path)
            print(f"Uploaded: {os.path.basename(doc_path)}")
            
        # Wait for the title field to be available and get its contents
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_title"]')))
        title_element = driver.find_element(By.XPATH, '//*[@id="id_title"]')
        
        # Get the value of the title field
        id_title = title_element.get_attribute("value")
        
        # Print the title to the console
        print(f"Title field content: {id_title}")
        
        # Wait for exclusion options to be available
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_bibliography"]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_quotes"]')))
        
        # Ask for exclusion options
        exclusion_choice = input("Select Exclusion Options:\n1. None\n2. Both\n3. Bibliography\n4. Quotes\nEnter 1, 2, 3, or 4: ")
        
        bibliography_checkbox = driver.find_element(By.XPATH, '//*[@id="id_exclude_bibliography"]')
        quotes_checkbox = driver.find_element(By.XPATH, '//*[@id="id_exclude_quotes"]')
        
        # Apply the exclusion choices
        if exclusion_choice == "1":
            # Make sure neither is selected
            if bibliography_checkbox.is_selected():
                bibliography_checkbox.click()
            if quotes_checkbox.is_selected():
                quotes_checkbox.click()
            print("Selected: No exclusions")
        elif exclusion_choice == "2":
            # Select both
            if not bibliography_checkbox.is_selected():
                bibliography_checkbox.click()
            if not quotes_checkbox.is_selected():
                quotes_checkbox.click()
            print("Selected: Both exclusions (Bibliography and Quotes)")
        elif exclusion_choice == "3":
            # Bibliography only
            if not bibliography_checkbox.is_selected():
                bibliography_checkbox.click()
            if quotes_checkbox.is_selected():
                quotes_checkbox.click()
            print("Selected: Exclude Bibliography only")
        elif exclusion_choice == "4":
            # Quotes only
            if bibliography_checkbox.is_selected():
                bibliography_checkbox.click()
            if not quotes_checkbox.is_selected():
                quotes_checkbox.click()
            print("Selected: Exclude Quotes only")
        else:
            print("Invalid choice. No exclusions selected.")
            
        # Wait for small matches method options to be available
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_small_matches_method_0"]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_small_matches_method_1"]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_small_matches_method_2"]')))
        
        # Ask for small matches method
        small_matches_choice = input("Select Exclude small matches method:\n1. Disabled\n2. By Words\n3. By Percentage\nEnter 1, 2, or 3: ")
        
        # Apply the small matches method choice
        if small_matches_choice == "1":
            disabled_option = driver.find_element(By.XPATH, '//*[@id="id_exclude_small_matches_method_0"]')
            if not disabled_option.is_selected():
                disabled_option.click()
            print("Selected: Disabled small matches exclusion")
        elif small_matches_choice == "2":
            words_option = driver.find_element(By.XPATH, '//*[@id="id_exclude_small_matches_method_1"]')
            if not words_option.is_selected():
                words_option.click()
            print("Selected: Exclude small matches by Words")
            
            # Wait for the words input field to be available
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_small_matches_value_words"]')))
            
            # Ask for the word count threshold
            word_count = input("Enter word count threshold: ")
            
            try:
                # Validate input is an integer
                word_count = int(word_count)
                # Find the input field and enter the word count
                words_input = driver.find_element(By.XPATH, '//*[@id="id_exclude_small_matches_value_words"]')
                words_input.clear()  # Clear any existing value
                words_input.send_keys(str(word_count))
                print(f"Set word count threshold to: {word_count}")
            except ValueError:
                print("Invalid input. Word count must be a number.")
                
        elif small_matches_choice == "3":
            percentage_option = driver.find_element(By.XPATH, '//*[@id="id_exclude_small_matches_method_2"]')
            if not percentage_option.is_selected():
                percentage_option.click()
            print("Selected: Exclude small matches by Percentage")
            
            # Wait for the percentage input field to be available
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_exclude_small_matches_value_percentage"]')))
            
            # Ask for the percentage threshold
            percentage_value = input("Enter percentage threshold: ")
            
            try:
                # Validate input is a number
                percentage_value = int(percentage_value)
                # Find the input field and enter the percentage
                percentage_input = driver.find_element(By.XPATH, '//*[@id="id_exclude_small_matches_value_percentage"]')
                percentage_input.clear()  # Clear any existing value
                percentage_input.send_keys(str(percentage_value))
                print(f"Set percentage threshold to: {percentage_value}%")
            except ValueError:
                print("Invalid input. Percentage must be a number.")
                
        else:
            print("Invalid choice. Using default (Disabled).")
        
        # Wait for the submit button to be available and click it
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit-button"]')))
        submit_button = driver.find_element(By.XPATH, '//*[@id="submit-button"]')
        submit_button.click()
        print("Submission form submitted successfully")
        
        # Monitor the status after submission
        import time
        
        # Wait for the status table to appear
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[5]')))
            
            status = ""
            processing_seconds = 0
            start_time = time.time()
            
            # Keep checking the status every second until it's SUCCESS or an error state
            while True:
                try:
                    status_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[5]')
                    status = status_element.text.strip()
                    processing_seconds += 1
                    
                    # Calculate minutes and seconds for display
                    minutes = processing_seconds // 60
                    seconds = processing_seconds % 60
                    time_display = f"{minutes:02d}:{seconds:02d}"
                    
                    print(f"Current status: {status} (Processing time: {time_display})")
                    
                    # Check if processing is complete
                    if status == "SUCCESS":
                        # Calculate final time using actual elapsed time for more accuracy
                        final_seconds = int(time.time() - start_time)
                        final_minutes = final_seconds // 60
                        final_seconds_remainder = final_seconds % 60
                        final_time_display = f"{final_minutes:02d}:{final_seconds_remainder:02d}"
                        
                        print(f"Processing completed successfully! Total time: {final_time_display} ({final_minutes} minutes and {final_seconds_remainder} seconds)")
                        processing_time = final_time_display
                        
                        # Get the href instead of just reporting success
                        try:
                            details_link = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[1]/a')
                            href = details_link.get_attribute("href")
                            
                            # If the href is a relative URL, construct the full URL
                            if href.startswith("/"):
                                details_url = f"https://scopedlens.com{href}"
                            else:
                                details_url = href
                            
                            print(f"Navigating to details page: {details_url}")
                            
                            # Navigate to the details URL
                            driver.get(details_url)
                            
                            # Wait for the details page to load
                            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')))
                            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[5]/td')))
                            
                            # Get the Similarity Index information
                            similarity_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')
                            similarity_text = similarity_element.text.strip()
                            
                            # Get the Similarity Report download link if available
                            similarity_links = similarity_element.find_elements(By.TAG_NAME, 'a')
                            similarity_download_url = "No download link available"
                            if similarity_links:
                                similarity_download_url = similarity_links[0].get_attribute("href")
                            
                            # Get the AI Writing Index information
                            ai_index_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[5]/td')
                            ai_index_text = ai_index_element.text.strip()
                            
                            # Get the AI Report download link if available
                            ai_links = ai_index_element.find_elements(By.TAG_NAME, 'a')
                            ai_download_url = "No download link available"
                            if ai_links:
                                ai_download_url = ai_links[0].get_attribute("href")
                            
                            # Display the results
                            print(f"Similarity Index: {similarity_text}")
                            print(f"Similarity Report Download: {similarity_download_url}")
                            
                            print(f"AI Index: {ai_index_text}")
                            print(f"AI Report Download: {ai_download_url}")
                            
                            # Update the status to include these results
                            status = f"SUCCESS - Similarity: {similarity_text}, AI Index: {ai_index_text}"
                            
                            # Save the reports information
                            similarity_report = {
                                'index': similarity_text,
                                'download_url': similarity_download_url
                            }
                            
                            ai_report = {
                                'index': ai_index_text,
                                'download_url': ai_download_url
                            }
                            
                        except Exception as e:
                            print(f"Failed to get report information: {e}")
                        
                        break
                    elif status != "STARTED" and status != "":
                        # Calculate final time using actual elapsed time for more accuracy
                        final_seconds = int(time.time() - start_time)
                        final_minutes = final_seconds // 60
                        final_seconds_remainder = final_seconds % 60
                        final_time_display = f"{final_minutes:02d}:{final_seconds_remainder:02d}"
                        
                        print(f"Processing failed with status: {status}. Total time: {final_time_display} ({final_minutes} minutes and {final_seconds_remainder} seconds)")
                        processing_time = final_time_display
                        
                        # Get the href instead of clicking the link
                        try:
                            details_link = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div/table/tbody/tr/td[1]/a')
                            href = details_link.get_attribute("href")
                            
                            # If the href is a relative URL, construct the full URL
                            if href.startswith("/"):
                                details_url = f"https://scopedlens.com{href}"
                            else:
                                details_url = href
                            
                            print(f"Navigating to details page: {details_url}")
                            
                            # Navigate to the details URL
                            driver.get(details_url)
                            
                            # Wait for the error details page to load
                            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')))
                            
                            # Get the error message
                            error_element = driver.find_element(By.XPATH, '/html/body/div/div/div/div/table/tbody/tr[4]/td')
                            error_message = error_element.text.strip()
                            
                            # Display the error message
                            print(f"Error: {error_message}")
                            
                            # Update the status to include the error message
                            status = f"{status} - Error: {error_message}"
                        except Exception as e:
                            print(f"Failed to get detailed error information: {e}")
                        
                        break
                    
                    # Wait for 1 second before checking again
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error checking status: {e}")
                    processing_time = "Error during processing"
                    break
        
        except Exception as e:
            print(f"Could not find status element: {e}")
            status = "STATUS_ELEMENT_NOT_FOUND"
            processing_time = "N/A"
        
        # Keep the browser open until user manually closes it
        input("Press Enter to close the browser...")
        
        # Return the title value, quota value, final status, and processing time
        return id_title, quota_value, status, processing_time
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None, None
    
    finally:
        driver.quit()

if __name__ == "__main__":
    id_title, quota_value, status, processing_time = navigate_to_turnitin()
    print(f"Saved title value: {id_title}")
    print(f"Your quota: {quota_value}")
    print(f"Final status: {status}")
    print(f"Total processing time: {processing_time}")