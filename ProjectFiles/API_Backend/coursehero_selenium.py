import time
import os
import re
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import base64

# Path to Firefox profile for Coursehero
FIREFOX_PROFILE_PATH = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/43gkv1wz.coursehero"

# Path to Downloaded Files folder
DOWNLOADS_PATH = "/Users/anoopkondepudi/Desktop/Education Webscraper V2/Education-Webscraper-V2/ProjectFiles/Downloaded Files"

# Maximum number of refresh attempts
MAX_REFRESH_ATTEMPTS = 3

def setup_driver():
    """Set up Firefox WebDriver with appropriate configurations."""
    options = webdriver.FirefoxOptions()
    
    # Use existing profile if available
    if os.path.exists(FIREFOX_PROFILE_PATH):
        print(f"Using Firefox profile: {FIREFOX_PROFILE_PATH}")
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
    else:
        print("Warning: Firefox profile path not found, using default profile")
    
    # Configure download preferences
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", DOWNLOADS_PATH)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.manager.closeWhenDone", True)
    
    # Create and return the driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return driver

def extract_document_id(url):
    """Extract document ID from a Coursehero URL."""
    pattern = r"\/file\/([^\/]+)\/"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def list_files():
    """Get a list of all files in the download directory."""
    try:
        files = os.listdir(DOWNLOADS_PATH)
        print(f"Files in directory ({len(files)} total):")
        for i, file in enumerate(files):
            print(f"  {i+1}. {file}")
        return set(files)
    except Exception as e:
        print(f"Error listing files: {e}")
        return set()

def is_temporary_file(filename):
    """Check if a file is a temporary download file."""
    temp_patterns = ['.part', '.crdownload', '.download']
    return any(pattern in filename for pattern in temp_patterns)

def is_access_denied(driver):
    """Check if the page shows an access denied error."""
    try:
        # Try the provided XPath
        access_denied_element = driver.find_elements(By.XPATH, "/html/body/div/div[1]/div[1]/div/div[1]")
        if access_denied_element:
            text = access_denied_element[0].text
            if "Access denied" in text:
                print(f"⚠️ Access denied detected: '{text}'")
                return True
                
        # Also check for error text anywhere on the page
        page_source = driver.page_source.lower()
        if "access denied" in page_source or "error 15" in page_source:
            print("⚠️ Access denied text found on page")
            return True
            
        return False
    except Exception as e:
        print(f"Error checking for access denied: {e}")
        return False

def monitor_downloads(initial_files, timeout=60):  # Extended timeout for complete downloads
    """Monitor for new files and return the first completed download."""
    start_time = time.time()
    print(f"Starting file monitoring (timeout: {timeout} seconds)...")
    
    temp_files_detected = set()
    
    while time.time() - start_time < timeout:
        try:
            current_files = set(os.listdir(DOWNLOADS_PATH))
            
            # Check for new temporary files (downloads in progress)
            new_temp_files = {f for f in current_files - initial_files if is_temporary_file(f)}
            for temp_file in new_temp_files - temp_files_detected:
                print(f"🔄 Download in progress: {temp_file}")
                temp_files_detected.add(temp_file)
            
            # Check for new completed files (not temporary and not in initial set)
            new_completed_files = {f for f in current_files - initial_files if not is_temporary_file(f)}
            
            if new_completed_files:
                # Sort by modification time to get the most recent file
                completed_files_with_mtime = []
                for file in new_completed_files:
                    file_path = os.path.join(DOWNLOADS_PATH, file)
                    mtime = os.path.getmtime(file_path)
                    completed_files_with_mtime.append((file, mtime))
                
                # Sort by modification time (newest first)
                completed_files_with_mtime.sort(key=lambda x: x[1], reverse=True)
                newest_file = completed_files_with_mtime[0][0]
                
                print(f"✅ Download completed: {newest_file}")
                return os.path.join(DOWNLOADS_PATH, newest_file)
        except Exception as e:
            print(f"Error during monitoring: {e}")
        
        time.sleep(0.25)
    
    print("⏱️ Monitoring timeout reached. No completed downloads detected.")
    return None

def send_request_with_refresh(driver, url, download_event):
    """Send request with automatic refresh if access denied."""
    try:
        attempts = 0
        while attempts < MAX_REFRESH_ATTEMPTS and not download_event.is_set():
            attempts += 1
            print(f"Thread: Sending request to {url} (attempt {attempts}/{MAX_REFRESH_ATTEMPTS})")
            
            driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            if is_access_denied(driver):
                print(f"🔄 Access denied detected. Refreshing page (attempt {attempts}/{MAX_REFRESH_ATTEMPTS})")
                time.sleep(1)
                continue
            else:
                print("Thread: Request sent successfully (no access denied detected)")
                break
                
        if attempts >= MAX_REFRESH_ATTEMPTS:
            print("❌ Max refresh attempts reached. Still getting access denied.")
    except Exception as e:
        print(f"Thread: Error sending request: {e}")

def scrape_coursehero(url):
    """Access Coursehero content directly and monitor for downloads."""
    print(f"🚀 Starting Coursehero scraper for URL: {url}")
    
    # Extract document ID from URL
    document_id = extract_document_id(url)
    if not document_id:
        print(f"❌ Could not extract document ID from URL: {url}")
        return None, None
    
    print(f"📄 Extracted document ID: {document_id}")
    
    # Ensure download directory exists
    if not os.path.exists(DOWNLOADS_PATH):
        os.makedirs(DOWNLOADS_PATH)
    
    # Check initial files
    print("\n📋 INITIAL FILES:")
    initial_files = list_files()
    
    # Setup driver
    driver = setup_driver()
    
    try:
        # Build download URL
        download_url = f"https://www.coursehero.com/api/v1/documents/unlock-and-download/{document_id}/"
        print(f"\n⬇️ Will send request to: {download_url}")
        
        # Create an event to signal when download is complete
        download_complete = threading.Event()
        
        # Start a thread to send the request (non-blocking)
        request_thread = threading.Thread(
            target=send_request_with_refresh, 
            args=(driver, download_url, download_complete)
        )
        request_thread.daemon = True
        request_thread.start()
        
        # Wait a moment for the request to start
        time.sleep(1)
        print("Main thread continuing with file monitoring...")
        
        # Monitor for downloads
        downloaded_file = monitor_downloads(initial_files)
        
        # Signal that download is complete (to stop refreshing)
        download_complete.set()
        
        # Check final files
        print("\n📋 FINAL FILES:")
        list_files()
        
        if downloaded_file:
            filename = os.path.basename(downloaded_file)
            print(f"\n✅ SUCCESS: File downloaded to: {filename}")
            return downloaded_file, driver
        else:
            print("\n❌ FAILED: No completed download detected after timeout")
            return None, driver
            
    except Exception as e:
        print(f"❌ Main thread error: {e}")
        return None, driver

def extract_question_id(url):
    """Extract question ID from a Coursehero tutor question URL."""
    pattern = r"\/tutors-problems\/[^\/]+\/(\d+)-"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def download_attachment_with_js(driver, att_id, qa_thread_id, question_id, is_answer=False):
    """Download a single attachment using JavaScript iframe method with proper download completion handling."""
    # Create images directory if it doesn't exist
    image_dir = os.path.join(DOWNLOADS_PATH, "question_images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Get list of files before download
    initial_files = set(os.listdir(DOWNLOADS_PATH))
    print(f"📊 Initial files count: {len(initial_files)}")
    
    # Construct download URL
    download_url = f"https://www.coursehero.com/load_question_attachment.php?q_att_id={att_id}&thread_id={qa_thread_id}"
    print(f"📥 Downloading: {download_url}")
    
    # Use JavaScript iframe method to trigger download
    js_script = f"""
    var iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = '{download_url}';
    document.body.appendChild(iframe);
    return true;
    """
    driver.execute_script(js_script)
    print("✅ Download initiated via JavaScript iframe")
    
    # First, detect the temporary (.part) file
    max_wait = 10  # seconds
    start_time = time.time()
    temp_file = None
    
    print("🔍 Looking for new download file...")
    while time.time() - start_time < max_wait and not temp_file:
        current_files = set(os.listdir(DOWNLOADS_PATH))
        new_files = current_files - initial_files
        
        for file in new_files:
            if file.endswith('.part') or file.endswith('.download') or file.endswith('.crdownload'):
                temp_file = file
                print(f"🔄 Download in progress: {temp_file}")
                break
                
        if not temp_file:
            # Also check for completed files (maybe download was fast)
            completed_files = [f for f in new_files if not (f.endswith('.part') or 
                                                          f.endswith('.download') or 
                                                          f.endswith('.crdownload'))]
            if completed_files:
                print(f"✅ Download already completed: {completed_files[0]}")
                temp_file = "COMPLETED"  # Special flag
                break
                
        time.sleep(0.2)  # Short sleep between checks
    
    # If we found a temporary file, wait for it to complete
    completed_file = None
    
    if temp_file and temp_file != "COMPLETED":
        print(f"⏳ Waiting for download to complete: {temp_file}")
        
        # Wait for temporary file to disappear and be replaced with final file
        expected_final_file = temp_file.replace('.part', '').replace('.download', '').replace('.crdownload', '')
        
        # Wait for the temporary file to be replaced with the final file
        wait_start = time.time()
        max_completion_wait = 30  # seconds
        
        while time.time() - wait_start < max_completion_wait:
            current_files = set(os.listdir(DOWNLOADS_PATH))
            
            # Check if temp file is gone
            if temp_file not in current_files:
                # Check if final file exists
                if expected_final_file in current_files:
                    completed_file = expected_final_file
                    print(f"✅ Download completed: {completed_file}")
                    break
                    
                # If neither temp nor expected file exists, check for any new file
                new_files = current_files - initial_files
                completed_files = [f for f in new_files if not (f.endswith('.part') or 
                                                              f.endswith('.download') or 
                                                              f.endswith('.crdownload'))]
                if completed_files:
                    completed_file = completed_files[0]
                    print(f"✅ Download completed with different name: {completed_file}")
                    break
            
            # Also check if file completed but kept the same name
            if temp_file in current_files:
                # Check if file size stopped changing (indicating it's complete)
                file_path = os.path.join(DOWNLOADS_PATH, temp_file)
                try:
                    size1 = os.path.getsize(file_path)
                    time.sleep(1)
                    size2 = os.path.getsize(file_path)
                    
                    if size1 == size2 and size1 > 0:
                        # File size stable, might be complete
                        completed_file = temp_file
                        print(f"✅ Download appears complete (stable size): {completed_file}")
                        break
                except:
                    pass
                    
            time.sleep(0.5)
    elif temp_file == "COMPLETED":
        # Download already completed
        current_files = set(os.listdir(DOWNLOADS_PATH))
        new_files = current_files - initial_files
        completed_files = [f for f in new_files if not (f.endswith('.part') or 
                                                      f.endswith('.download') or 
                                                      f.endswith('.crdownload'))]
        if completed_files:
            completed_file = max(completed_files, key=lambda f: os.path.getmtime(os.path.join(DOWNLOADS_PATH, f)))
    
    # If we found a completed file, copy and rename it
    if completed_file:
        source_path = os.path.join(DOWNLOADS_PATH, completed_file)
        file_extension = os.path.splitext(completed_file)[1]
        if not file_extension:
            file_extension = '.jpg'  # Default extension
        
        # Create new filename
        prefix = "a" if is_answer else "q"
        new_filename = f"question_{question_id}_{prefix}_image_{att_id}{file_extension}"
        dest_path = os.path.join(image_dir, new_filename)
        
        print(f"🔄 Moving: {completed_file} -> {new_filename}")
        
        try:
            # Copy instead of move in case there's an issue
            import shutil
            shutil.copy2(source_path, dest_path)
            print(f"✅ File copied successfully to: {dest_path}")
            
            # Return the relative path for HTML
            return os.path.join("question_images", new_filename)
        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return None
    else:
        print(f"⏱️ Timed out waiting for download to complete")
        return None

def scrape_coursehero_question(url):
    """Access Coursehero tutor question and create an HTML file with base64-encoded images."""
    print(f"🚀 Starting Coursehero tutor question scraper for URL: {url}")
    
    # Extract question ID from URL
    question_id = extract_question_id(url)
    if not question_id:
        print(f"❌ Could not extract question ID from URL: {url}")
        return None, None
    
    print(f"❓ Extracted question ID: {question_id}")
    
    # Setup driver
    driver = setup_driver()
    
    try:
        # Step 1: Unlock the question
        unlock_url = f"https://www.coursehero.com/unlock-question/{question_id}"
        print(f"\n🔓 Unlocking question: {unlock_url}")
        
        driver.get(unlock_url)
        time.sleep(3)  # Wait for unlock to process
        
        # Step 2: Get question content
        content_url = f"https://www.coursehero.com/api/v1/questions/{question_id}/"
        print(f"\n📝 Getting question content: {content_url}")
        
        driver.get(content_url)
        time.sleep(2)
        
        # Parse the JSON response
        try:
            # Get pre element which should contain the JSON
            pre_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            json_text = pre_element.text
            import json
            question_data = json.loads(json_text)
            
            # Extract threads which contain both question and answer
            threads = question_data.get("threads", [])
            
            # First, clean up any previous downloads to avoid confusion
            import os
            import glob
            for file in glob.glob(os.path.join(DOWNLOADS_PATH, "IMG_*")):
                try:
                    os.remove(file)
                    print(f"🧹 Cleaned up existing file: {file}")
                except:
                    pass
            
            for file in glob.glob(os.path.join(DOWNLOADS_PATH, "image*.jpg")):
                try:
                    os.remove(file)
                    print(f"🧹 Cleaned up existing file: {file}")
                except:
                    pass
            
            # Process question thread
            question_thread = next((t for t in threads if t.get("type") == "question"), {})
            question_text = question_thread.get("formatted_display_text", "No question found")
            
            # Process question attachments
            question_attachments = []
            if question_thread and "attachment" in question_thread and question_thread["attachment"]:
                attachments = question_thread.get("attachment", [])
                print(f"\n🖼️ Found {len(attachments)} question attachments")
                
                for attachment in attachments:
                    att_id = attachment.get("question_attachment_id")
                    qa_thread_id = question_thread.get("qa_thread_id")
                    filename = attachment.get("users_filename", "")
                    
                    if att_id and qa_thread_id:
                        question_attachments.append({
                            "att_id": att_id,
                            "qa_thread_id": qa_thread_id,
                            "filename": filename,
                            "is_answer": False  # This is a question attachment
                        })
            
            # Process answer thread
            answer_thread = next((t for t in threads if t.get("type") == "answer"), {})
            answer_text = answer_thread.get("formatted_display_text", "")
            answer_explanation = answer_thread.get("formatted_explanation", "")
            
            if answer_explanation and answer_explanation != answer_text:
                if answer_text:
                    answer_text += "<br>"
                answer_text += answer_explanation
                
            if not answer_text:
                answer_text = "No answer found"
            
            # Process answer attachments
            answer_attachments = []
            if answer_thread and "attachment" in answer_thread and answer_thread["attachment"]:
                attachments = answer_thread.get("attachment", [])
                print(f"\n🖼️ Found {len(attachments)} answer attachments")
                
                for attachment in attachments:
                    att_id = attachment.get("question_attachment_id")
                    qa_thread_id = answer_thread.get("qa_thread_id")
                    filename = attachment.get("users_filename", "")
                    
                    if att_id and qa_thread_id:
                        answer_attachments.append({
                            "att_id": att_id,
                            "qa_thread_id": qa_thread_id,
                            "filename": filename,
                            "is_answer": True  # This is an answer attachment
                        })
            
            # Combine all attachments to process
            all_attachments = question_attachments + answer_attachments
            print(f"\n📊 Processing a total of {len(all_attachments)} attachments")
            
            # Download all attachments and convert to base64            
            base64_images = []
            
            # Function to download a single attachment with retries
            def download_and_encode_attachment(attachment, max_retries=3):
                att_id = attachment["att_id"]
                qa_thread_id = attachment["qa_thread_id"]
                is_answer = attachment["is_answer"]
                
                # Create a unique ID for this download
                import uuid
                download_id = str(uuid.uuid4())[:8]
                
                download_url = f"https://www.coursehero.com/load_question_attachment.php?q_att_id={att_id}&thread_id={qa_thread_id}"
                print(f"\n📥 Downloading attachment: ID {att_id} ({"Answer" if is_answer else "Question"} attachment)")
                
                for retry in range(max_retries):
                    try:
                        # Clear any existing files with same names to avoid conflicts
                        for existing_file in glob.glob(os.path.join(DOWNLOADS_PATH, f"*{att_id}*")):
                            try:
                                os.remove(existing_file)
                                print(f"🧹 Cleaned up potential conflict: {existing_file}")
                            except:
                                pass
                        
                        # Get a clean snapshot of the directory before download
                        current_files_before = set(os.listdir(DOWNLOADS_PATH))
                        print(f"📊 Files before download: {len(current_files_before)}")
                        
                        # Download using JavaScript iframe with a unique marker
                        js_script = f"""
                        var iframe = document.createElement('iframe');
                        iframe.id = 'download_frame_{download_id}';
                        iframe.style.display = 'none';
                        iframe.src = '{download_url}';
                        document.body.appendChild(iframe);
                        return true;
                        """
                        driver.execute_script(js_script)
                        
                        # Wait for the download to complete dynamically
                        found_file = None
                        max_wait = 20  # seconds
                        start_time = time.time()
                        
                        while time.time() - start_time < max_wait and not found_file:
                            # Get current files
                            current_files_after = set(os.listdir(DOWNLOADS_PATH))
                            new_files = current_files_after - current_files_before
                            
                            # Check for completed downloads
                            completed_files = [f for f in new_files if not (f.endswith('.part') or 
                                                                        f.endswith('.download') or 
                                                                        f.endswith('.crdownload'))]
                            
                            if completed_files:
                                # Get the newest file
                                try:
                                    newest_file = max(completed_files, 
                                                   key=lambda f: os.path.getmtime(os.path.join(DOWNLOADS_PATH, f)))
                                    found_file = newest_file
                                    print(f"✅ Found new file: {found_file}")
                                    break
                                except Exception as e:
                                    print(f"⚠️ Error finding newest file: {e}")
                            
                            # Check for part files
                            part_files = [f for f in new_files if f.endswith('.part') or 
                                                       f.endswith('.download') or 
                                                       f.endswith('.crdownload')]
                            if part_files:
                                print(f"🔄 Download in progress: {part_files}")
                            
                            # Short wait between checks
                            time.sleep(0.2)
                        
                        # Clean up the iframe
                        driver.execute_script(f"var elem = document.getElementById('download_frame_{download_id}'); if(elem) elem.remove();")
                        
                        # If no file found, try again
                        if not found_file:
                            print(f"⚠️ No file found on attempt {retry+1}/{max_retries}, retrying...")
                            continue
                        
                        # Verify the file exists and has content
                        source_path = os.path.join(DOWNLOADS_PATH, found_file)
                        if not os.path.exists(source_path):
                            print(f"⚠️ File disappeared: {source_path}, retrying...")
                            continue
                            
                        file_size = os.path.getsize(source_path)
                        if file_size == 0:
                            print(f"⚠️ File is empty (0 bytes): {source_path}, retrying...")
                            continue
                            
                        print(f"📊 Downloaded file size: {file_size} bytes")
                        
                        # Make sure file isn't being written to anymore
                        size1 = file_size
                        time.sleep(0.5)
                        size2 = os.path.getsize(source_path)
                        
                        if size1 != size2:
                            print(f"⚠️ File still being written to: {source_path}, waiting...")
                            # Wait for it to stabilize
                            stable_count = 0
                            while stable_count < 3 and time.time() - start_time < max_wait:
                                size1 = os.path.getsize(source_path)
                                time.sleep(0.5)
                                size2 = os.path.getsize(source_path)
                                if size1 == size2:
                                    stable_count += 1
                                else:
                                    stable_count = 0
                        
                        # Determine the MIME type
                        file_extension = os.path.splitext(found_file)[1].lower()
                        mime_type = "image/jpeg"  # Default
                        if file_extension == ".png":
                            mime_type = "image/png"
                        elif file_extension == ".gif":
                            mime_type = "image/gif"
                        elif file_extension == ".pdf":
                            mime_type = "application/pdf"
                        
                        # Encode the file to base64
                        with open(source_path, "rb") as image_file:
                            encoded_data = image_file.read()
                            if not encoded_data:
                                print(f"⚠️ No data read from file: {source_path}, retrying...")
                                continue
                                
                            encoded_string = base64.b64encode(encoded_data).decode('utf-8')
                            encoded_length = len(encoded_string)
                            
                            if encoded_length == 0:
                                print(f"⚠️ Base64 encoding produced 0 length string, retrying...")
                                continue
                                
                            print(f"📊 Base64 encoded string length: {encoded_length} characters")
                        
                        # Create the result object
                        result = {
                            "att_id": att_id,
                            "base64": encoded_string,
                            "mime_type": mime_type,
                            "original_filename": attachment.get("filename", ""),
                            "is_answer": is_answer,
                            "file_size": file_size
                        }
                        
                        # Delete the original file
                        try:
                            os.remove(source_path)
                            print(f"🗑️ Deleted original file: {source_path}")
                        except Exception as e:
                            print(f"⚠️ Could not delete original file: {e}")
                        
                        # Success!
                        return result
                        
                    except Exception as e:
                        print(f"❌ Error on attempt {retry+1}/{max_retries}: {e}")
                        if retry == max_retries - 1:
                            print(f"❌ All retries failed for attachment {att_id}")
                            return None
                
                # If we get here, all retries failed
                return None
            
            # Process all attachments
            for i, attachment in enumerate(all_attachments):
                print(f"\n⏳ Processing attachment {i+1}/{len(all_attachments)}")
                result = download_and_encode_attachment(attachment)
                
                if result:
                    result["download_order"] = i
                    base64_images.append(result)
                    print(f"✅ Successfully processed attachment {i+1}/{len(all_attachments)}")
                else:
                    print(f"❌ Failed to process attachment {i+1}/{len(all_attachments)}")
            
            # Check if we successfully processed all images
            print(f"\n📊 Successfully encoded {len(base64_images)}/{len(all_attachments)} images")
            
            # Create a mapping of attachment IDs to base64 data
            attachment_map = {}
            for img in base64_images:
                attachment_map[str(img["att_id"])] = img
            
            # Track which images have been inserted inline
            used_image_ids = set()
            
            # Fix the question text - replace image references with base64 images
            for att_id, img in attachment_map.items():
                if not img["is_answer"]:  # Only process question images for question text
                    patterns = [
                        f'<img src="\\/qa\\/attachment\\/{att_id}\\/"[^>]*>',
                        f'<img src="/qa/attachment/{att_id}/"[^>]*>',
                        f'<img[^>]*src="/qa/attachment/{att_id}/"[^>]*>',
                        f'<figure class="image"><img src="\\/qa\\/attachment\\/{att_id}\\/"[^>]*><\\/figure>',
                        f'<figure class="image"><img src="/qa/attachment/{att_id}/"[^>]*></figure>'
                    ]
                    
                    replacement = f'<img src="data:{img["mime_type"]};base64,{img["base64"]}" alt="{img["original_filename"]}" />'
                    
                    # Check if the image is referenced in the text
                    found_in_text = False
                    for pattern in patterns:
                        if re.search(pattern, question_text):
                            found_in_text = True
                            used_image_ids.add(att_id)
                            question_text = re.sub(pattern, replacement, question_text)
                            
            # Fix the answer text - replace image references with base64 images
            for att_id, img in attachment_map.items():
                if img["is_answer"]:  # Only process answer images for answer text
                    patterns = [
                        f'<img src="\\/qa\\/attachment\\/{att_id}\\/"[^>]*>',
                        f'<img src="/qa/attachment/{att_id}/"[^>]*>',
                        f'<img[^>]*src="/qa/attachment/{att_id}/"[^>]*>',
                        f'<figure class="image"><img src="\\/qa\\/attachment\\/{att_id}\\/"[^>]*><\\/figure>',
                        f'<figure class="image"><img src="/qa/attachment/{att_id}/"[^>]*></figure>'
                    ]
                    
                    replacement = f'<img src="data:{img["mime_type"]};base64,{img["base64"]}" alt="{img["original_filename"]}" />'
                    
                    # Check if the image is referenced in the text
                    found_in_text = False
                    for pattern in patterns:
                        if re.search(pattern, answer_text):
                            found_in_text = True
                            used_image_ids.add(att_id)
                            answer_text = re.sub(pattern, replacement, answer_text)
            
            # Generate HTML for attachments that were NOT included inline
            question_attachments_html = ""
            answer_attachments_html = ""
            
            for img in base64_images:
                att_id = str(img["att_id"])
                if att_id not in used_image_ids:
                    # Create appropriate HTML only for images not already in text
                    img_html = (
                        f'<div>\n'
                        f'<p>{img["original_filename"]}</p>\n'
                        f'<img src="data:{img["mime_type"]};base64,{img["base64"]}" '
                        f'alt="{img["original_filename"]}" />\n'
                        f'</div>\n'
                    )
                    
                    # Add to appropriate section
                    if img["is_answer"]:
                        answer_attachments_html += img_html
                    else:
                        question_attachments_html += img_html
            
            # Create HTML file with proper styling
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CourseHero Question {question_id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; line-height: 1.6; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .question, .answer {{ padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
                    .question {{ background-color: #f0f7ff; border: 1px solid #d0e3ff; }}
                    .answer {{ background-color: #f5fff0; border: 1px solid #d6ffc7; }}
                    h2 {{ color: #333; }}
                    img {{ max-width: 100%; height: auto; margin: 10px 0; border: 1px solid #ddd; }}
                    .metadata {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
                    .attachments {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #eee; }}
                    figure.image {{ margin: 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>CourseHero Question and Answer</h1>
                    
                    <div class="metadata">
                        <p>Category: {question_data.get("question", {}).get("category", {}).get("subject", "Unknown")}</p>
                        <p>Question ID: {question_id}</p>
                        <p>Date Asked: {question_data.get("question", {}).get("date_asked", "Unknown")}</p>
                    </div>
                    
                    <div class="question">
                        <h2>Question:</h2>
                        {question_text}
                        <div class="attachments">
                            {question_attachments_html}
                        </div>
                    </div>
                    
                    <div class="answer">
                        <h2>Answer:</h2>
                        {answer_text}
                        <div class="attachments">
                            {answer_attachments_html}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save HTML file
            html_path = os.path.join(DOWNLOADS_PATH, f"question_{question_id}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"\n✅ SUCCESS: HTML file created at: {html_path}")
            return html_path, driver
            
        except Exception as e:
            print(f"❌ Error parsing question data: {e}")
            import traceback
            traceback.print_exc()
            return None, driver
            
    except Exception as e:
        print(f"❌ Error accessing tutor question: {e}")
        return None, driver

if __name__ == "__main__":
    # Uncomment to test document download
    # test_url = "https://www.coursehero.com/file/151322757/Unit-B-Module-3-Lesson-4-Assignmentdocxpdf/"
    # result, driver = scrape_coursehero(test_url)
    
    # Test tutor question scraping
    #test_url = "https://www.coursehero.com/tutors-problems/Electrical-Engineering/21477282-A-60-Hz-synchronous-generator-has-a-transient-reactance-of-02-pu-and/"
    #test_url = "https://www.coursehero.com/tutors-problems/Nursing/44508985--1-Crossword-Puzzle-The-Pediatric-Examination-Directions/"
    #test_url = "https://www.coursehero.com/tutors-problems/Civil-Engineering/39562113--2-A-survey-using-moving-observer-method-was-conducted-to/"
    #test_url = "https://www.coursehero.com/tutors-problems/Physics/60895488-A-20-kg-kangaroo-is-bouncing-as-kangaroos-are-wont-to-do-During-a/"
    # The above url doesnt work (AI Answered questions doesnt work)
    test_url = "https://www.coursehero.com/tutors-problems/Computer-Science/67803192-Write-up-the-results-of-your-evaluation-of-the-checksum-Be-sure-to/"
    # None image problem also having issues, must fix.
    result, driver = scrape_coursehero_question(test_url)
    
    if result:
        print(f"🎉 Document/question processed and saved to: {result}")
    else:
        print("⚠️ No document/question was processed")
    
    # Wait for user input before closing the browser
    input("Press Enter to close the browser...")
    driver.quit()
    print("🖥️ Browser closed") 