from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import os
from datetime import datetime
import websockets
import asyncio
import re
import requests

def monitor_coursehero_content():
    # Set up logging
    log_dir = "coursehero_logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"coursehero_log_{timestamp}.txt")
    network_file = os.path.join(log_dir, f"network_requests_{timestamp}.json")
    
    def log_message(message):
        print(message)
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')}: {message}\n")

    # Set up Firefox with custom profile
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/43gkv1wz.coursehero"
    options = Options()
    options.add_argument("-profile")
    options.add_argument(firefox_profile_path)
    
    # Enable browser console and network monitoring
    options.set_preference("devtools.console.stdout.content", True)
    options.set_preference("devtools.chrome.enabled", True)
    options.set_preference("devtools.debugger.remote-enabled", True)
    
    log_message(f"Starting CourseHero monitoring with Firefox profile: {firefox_profile_path}")
    
    # Create a driver with specified options
    driver = webdriver.Firefox(options=options)
    
    try:
        # Open the URL
        url = "https://www.coursehero.com/tutors-problems/Physics/60895488-A-20-kg-kangaroo-is-bouncing-as-kangaroos-are-wont-to-do-During-a/?justUnlocked=1"
        driver.get(url)
        log_message(f"Opened URL: {url}")
        
        # Set up more robust network request monitoring
        driver.execute_script("""
            window.network_requests = [];
            window.xhr_details = {};
            window.fetch_details = {};
            window.performance.setResourceTimingBufferSize(1000);
            
            // Track DOM mutations to catch when articles/paragraphs are added
            const mutationObserver = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach(node => {
                            if (node.tagName === 'ARTICLE' || 
                               (node.tagName === 'P' && node.parentElement && node.parentElement.tagName === 'ARTICLE')) {
                                console.log('DOM MUTATION - Added:', node.tagName, 
                                           'Content:', node.textContent.substring(0, 50) + '...',
                                           'Path:', getNodePath(node));
                                
                                window.network_requests.push({
                                    type: 'dom_mutation',
                                    element: node.tagName,
                                    content: node.textContent,
                                    time: new Date().getTime(),
                                    path: getNodePath(node)
                                });
                            }
                        });
                    }
                });
            });
            
            function getNodePath(node) {
                let path = '';
                while (node && node.nodeType === Node.ELEMENT_NODE) {
                    let selector = node.nodeName.toLowerCase();
                    if (node.id) {
                        selector += '#' + node.id;
                    } else if (node.className) {
                        selector += '.' + Array.from(node.classList).join('.');
                    }
                    path = selector + (path ? ' > ' + path : '');
                    node = node.parentNode;
                }
                return path;
            }
            
            // Start observing the target node for configured mutations
            mutationObserver.observe(document.body, { 
                childList: true, 
                subtree: true 
            });
            
            // Monitor XHR requests
            const originalXHR = window.XMLHttpRequest;
            window.XMLHttpRequest = function() {
                const xhr = new originalXHR();
                const originalOpen = xhr.open;
                const originalSend = xhr.send;
                
                xhr.open = function() {
                    xhr.requestMethod = arguments[0];
                    xhr.requestUrl = arguments[1];
                    return originalOpen.apply(xhr, arguments);
                };
                
                xhr.send = function() {
                    const requestData = arguments[0] || null;
                    const requestId = Date.now() + Math.random().toString(36).substring(2);
                    const startTime = new Date().getTime();
                    
                    xhr.addEventListener('load', function() {
                        try {
                            const response = this.responseText;
                            const requestInfo = {
                                id: requestId,
                                url: xhr.requestUrl,
                                method: xhr.requestMethod,
                                requestData: requestData,
                                status: this.status,
                                responseSize: response.length,
                                responsePreview: response.substring(0, 200) + '...',
                                startTime: startTime,
                                endTime: new Date().getTime()
                            };
                            
                            // Store full response separately to avoid memory issues in the main array
                            window.xhr_details[requestId] = {
                                fullResponse: response
                            };
                            
                            // Check if response contains HTML or article-like content
                            if (response.includes('<article') || 
                                response.includes('<p>') || 
                                response.includes('kangaroo')) {
                                requestInfo.containsRelevantContent = true;
                                console.log('XHR with relevant content:', xhr.requestUrl);
                            }
                            
                            window.network_requests.push(requestInfo);
                        } catch (e) {
                            console.error('Error capturing XHR:', e);
                        }
                    });
                    
                    return originalSend.apply(xhr, arguments);
                };
                
                return xhr;
            };
            
            // Monitor fetch requests
            const originalFetch = window.fetch;
            window.fetch = function() {
                const requestUrl = arguments[0];
                const requestOptions = arguments[1] || {};
                const requestMethod = requestOptions.method || 'GET';
                const requestId = Date.now() + Math.random().toString(36).substring(2);
                const startTime = new Date().getTime();
                
                return originalFetch.apply(this, arguments)
                    .then(response => {
                        // Clone the response so we can read the body without consuming it
                        const clonedResponse = response.clone();
                        
                        clonedResponse.text().then(responseText => {
                            try {
                                const requestInfo = {
                                    id: requestId,
                                    url: requestUrl.toString(),
                                    method: requestMethod,
                                    requestData: requestOptions.body || null,
                                    status: response.status,
                                    responseSize: responseText.length,
                                    responsePreview: responseText.substring(0, 200) + '...',
                                    startTime: startTime,
                                    endTime: new Date().getTime()
                                };
                                
                                // Store full response separately
                                window.fetch_details[requestId] = {
                                    fullResponse: responseText
                                };
                                
                                // Check if response contains HTML or article-like content
                                if (responseText.includes('<article') || 
                                    responseText.includes('<p>') || 
                                    responseText.includes('kangaroo')) {
                                    requestInfo.containsRelevantContent = true;
                                    console.log('Fetch with relevant content:', requestUrl);
                                }
                                
                                window.network_requests.push(requestInfo);
                        } catch (e) {
                            console.error('Error capturing fetch:', e);
                        }
                        }).catch(err => {
                            console.error('Error reading fetch response:', err);
                        });
                        
                        return response;
                    });
            };
            
            // Monitor potential websocket connections
            const originalWebSocket = window.WebSocket;
            window.WebSocket = function(url, protocols) {
                const ws = new originalWebSocket(url, protocols);
                
                console.log('WebSocket connection created to:', url);
                window.network_requests.push({
                    type: 'websocket_connection',
                    url: url,
                    protocols: protocols,
                    time: new Date().getTime()
                });
                
                const originalSend = ws.send;
                ws.send = function(data) {
                    window.network_requests.push({
                        type: 'websocket_message',
                        url: url,
                        direction: 'outgoing',
                        data: typeof data === 'string' ? data : '[binary data]',
                        time: new Date().getTime()
                    });
                    return originalSend.apply(ws, arguments);
                };
                
                ws.addEventListener('message', function(event) {
                    window.network_requests.push({
                        type: 'websocket_message',
                        url: url,
                        direction: 'incoming',
                        data: typeof event.data === 'string' ? event.data : '[binary data]',
                        time: new Date().getTime()
                    });
                });
                
                return ws;
            };
        """)
        
        # Main container XPath to monitor
        main_container_xpath = '//*[@id="block_ssi:component:SsiQuestionLanding"]/div/div[2]/div/main/div[1]/div/div/div[2]/div/div[2]'
        article_xpath = f"{main_container_xpath}/article"
        
        # Wait for the main container to be present
        log_message("Waiting for the main container...")
        main_container = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, main_container_xpath))
        )
        log_message("Main container found!")
        
        # First, check if there's any JavaScript that might be generating the content
        js_sources = driver.execute_script("""
            const scripts = Array.from(document.querySelectorAll('script'));
            return scripts.map(s => {
                return {
                    src: s.src,
                    inline: !s.src && s.innerText.length > 0 ? s.innerText.substring(0, 300) + '...' : null
                };
            });
        """)
        
        log_message(f"Found {len(js_sources)} script elements on the page")
        for i, script in enumerate(js_sources):
            if script['src']:
                log_message(f"Script {i+1}: External source: {script['src']}")
            elif script['inline']:
                log_message(f"Script {i+1}: Inline script preview: {script['inline'][:100]}...")
                if "kangaroo" in script['inline']:
                    log_message(f"IMPORTANT: Found 'kangaroo' in inline script {i+1}")
        
        # Monitor for article creation
        article_found = False
        monitoring_attempts = 0
        max_monitoring_attempts = 30
        article_content = []
        
        while not article_found and monitoring_attempts < max_monitoring_attempts:
            try:
                log_message(f"Monitoring attempt {monitoring_attempts + 1}/{max_monitoring_attempts}...")
                
                # Check if article exists
                try:
                    article = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, article_xpath))
                    )
                    article_found = True
                    log_message("Article found!")
                    
                    # Get article HTML
                    article_html = article.get_attribute('outerHTML')
                    log_message(f"Article HTML: {article_html[:500]}...")
                    
                    # Collect paragraph elements and their text
                    paragraphs = article.find_elements(By.TAG_NAME, "p")
                    
                    if paragraphs:
                        log_message(f"Found {len(paragraphs)} paragraphs")
                        for i, p in enumerate(paragraphs, 1):
                            try:
                                p_text = p.text
                                article_content.append(p_text)
                                log_message(f"Paragraph {i}: {p_text}")
                            except Exception as e:
                                log_message(f"Error getting text for paragraph {i}: {e}")
                    else:
                        log_message("No paragraphs found in article. Checking for other content:")
                        article_text = article.text
                        log_message(f"Article text content: {article_text}")
                        article_content.append(article_text)
                
                except TimeoutException:
                    log_message("Article not found yet")
                
                monitoring_attempts += 1
                
                # Capture network activity at each step
                if monitoring_attempts % 5 == 0 or article_found:
                    network_data = driver.execute_script("return window.network_requests;")
                    log_message(f"Captured {len(network_data)} network requests so far")
                    
                    # Look for relevant requests that might contain our content
                    for req in network_data:
                        if 'containsRelevantContent' in req and req['containsRelevantContent']:
                            log_message(f"Potentially relevant request: {req['url']} ({req['method']})")
                
                time.sleep(2)
                
            except Exception as e:
                log_message(f"Error during monitoring: {e}")
                monitoring_attempts += 1
                time.sleep(2)
        
        if not article_found:
            log_message("Article never appeared after maximum monitoring attempts")
        
        # Get final network data for analysis
        all_network_data = driver.execute_script("return window.network_requests;")
        xhr_details = driver.execute_script("return window.xhr_details;")
        fetch_details = driver.execute_script("return window.fetch_details;")
        
        log_message(f"Total captured network activity: {len(all_network_data)} items")
        
        # Save network requests to a file for analysis
        with open(network_file, "w") as f:
            json.dump(all_network_data, f, indent=2)
        
        # Save detailed responses for requests that might contain our content
        relevant_requests_dir = os.path.join(log_dir, f"relevant_requests_{timestamp}")
        os.makedirs(relevant_requests_dir, exist_ok=True)
        
        relevant_count = 0
        for req in all_network_data:
            if req.get('type') == 'dom_mutation' and 'article' in req.get('element', '').lower():
                log_message(f"DOM mutation detected: Article element added at time {req.get('time')}")
                continue
                
            # Check if this request happened around when article appeared
            is_relevant = False
            
            if article_found and 'time' in req and isinstance(req.get('time'), (int, float)):
                # Consider requests that happened shortly before article was found
                req_id = req.get('id')
                
                # Check for content-related keywords in response
                has_keywords = False
                if req.get('containsRelevantContent'):
                    has_keywords = True
                
                if has_keywords or ('url' in req and ('question' in req['url'] or 'answer' in req['url'])):
                    is_relevant = True
                    relevant_count += 1
                    
                    # Get full response if available
                    full_response = None
                    if req_id and req_id in xhr_details:
                        full_response = xhr_details[req_id].get('fullResponse')
                    elif req_id and req_id in fetch_details:
                        full_response = fetch_details[req_id].get('fullResponse')
                    
                    # Save the full response to a separate file
                    if full_response:
                        req_file = os.path.join(relevant_requests_dir, f"request_{relevant_count}.txt")
                        with open(req_file, "w") as f:
                            f.write(f"URL: {req.get('url')}\n")
                            f.write(f"Method: {req.get('method')}\n")
                            f.write(f"Time: {req.get('time')}\n")
                            f.write("Response:\n")
                            f.write(full_response)
                        
                        log_message(f"Saved relevant request {relevant_count} to {req_file}")
                        
                        # Check if response contains our article content
                        for para in article_content:
                            if para and para in full_response:
                                log_message(f"FOUND CONTENT SOURCE! Request {relevant_count} contains paragraph text")
                                log_message(f"URL: {req.get('url')}")
                                log_message(f"Method: {req.get('method')}")
                                
                                with open(os.path.join(log_dir, "content_source.txt"), "w") as f:
                                    f.write(f"Content source found!\n")
                                    f.write(f"URL: {req.get('url')}\n")
                                    f.write(f"Method: {req.get('method')}\n")
                                    f.write(f"Request ID: {req_id}\n")
                                    f.write("Request details:\n")
                                    f.write(json.dumps(req, indent=2))
        
        log_message(f"Analysis complete. Found {relevant_count} potentially relevant requests.")
        log_message(f"Logs saved to: {log_file}")
        log_message(f"Network data saved to: {network_file}")
        
        # Keep the browser open for manual inspection
        input("Press Enter to close the browser...")
        
    except Exception as e:
        log_message(f"Error: {e}")
    
    finally:
        # Close the browser
        driver.quit()
        log_message("Browser closed")

def monitor_coursehero_websocket():
    # Set up logging
    log_dir = "coursehero_logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"websocket_log_{timestamp}.txt")
    
    def log_message(message):
        print(message)
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')}: {message}\n")

    # Firefox setup
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/43gkv1wz.coursehero"
    options = Options()
    options.add_argument("-profile")
    options.add_argument(firefox_profile_path)
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Open URL
        url = "https://www.coursehero.com/tutors-problems/Physics/60895488-A-20-kg-kangaroo-is-bouncing-as-kangaroos-are-wont-to-do-During-a/?justUnlocked=1"
        driver.get(url)
        log_message(f"Opened URL: {url}")
        
        # Add WebSocket monitoring
        driver.execute_script("""
            // Store WebSocket messages
            window.websocket_messages = [];
            
            // Override WebSocket to capture messages
            const OriginalWebSocket = window.WebSocket;
            window.WebSocket = function(url, protocols) {
                const ws = new OriginalWebSocket(url, protocols);
                
                console.log('WebSocket connection opened to:', url);
                window.websocket_messages.push({
                    type: 'connection',
                    url: url,
                    time: new Date().toISOString()
                });
                
                // Capture messages received from server
                ws.addEventListener('message', function(event) {
                    try {
                        let parsedData = null;
                        try {
                            parsedData = JSON.parse(event.data);
                        } catch (e) {
                            parsedData = event.data;
                        }
                        
                        window.websocket_messages.push({
                            type: 'received',
                            url: url,
                            data: parsedData,
                            rawData: event.data,
                            time: new Date().toISOString()
                        });
                        
                        console.log('WebSocket received:', parsedData);
                    } catch (error) {
                        console.error('Error processing WebSocket message:', error);
                    }
                });
                
                // Capture messages sent to server
                const originalSend = ws.send;
                ws.send = function(data) {
                    try {
                        let parsedData = null;
                        try {
                            parsedData = JSON.parse(data);
                        } catch (e) {
                            parsedData = data;
                        }
                        
                        window.websocket_messages.push({
                            type: 'sent',
                            url: url,
                            data: parsedData,
                            rawData: data,
                            time: new Date().toISOString()
                        });
                        
                        console.log('WebSocket sent:', parsedData);
                    } catch (error) {
                        console.error('Error processing outgoing WebSocket message:', error);
                    }
                    
                    return originalSend.apply(this, arguments);
                };
                
                return ws;
            };
            
            // Monitor article content changes
            const articleObserver = new MutationObserver(mutations => {
                const article = document.querySelector('[data-testid="ai-message"]');
                if (article) {
                    window.websocket_messages.push({
                        type: 'content_update',
                        content: article.innerText || article.textContent,
                        html: article.innerHTML,
                        time: new Date().toISOString()
                    });
                }
            });
            
            // Start observing once article exists
            function startObserving() {
                const article = document.querySelector('[data-testid="ai-message"]');
                if (article) {
                    articleObserver.observe(article, { 
                        childList: true, 
                        subtree: true,
                        characterData: true
                    });
                    return true;
                }
                return false;
            }
            
            // Try to start observing immediately, or wait for article to appear
            if (!startObserving()) {
                const checkInterval = setInterval(() => {
                    if (startObserving()) {
                        clearInterval(checkInterval);
                    }
                }, 500);
            }
        """)
        
        # Main container XPath
        main_container_xpath = '//*[@id="block_ssi:component:SsiQuestionLanding"]/div/div[2]/div/main/div[1]/div/div/div[2]/div/div[2]'
        article_xpath = f"{main_container_xpath}/article"
        
        # Wait for the main container
        log_message("Waiting for the main container...")
        main_container = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, main_container_xpath))
        )
        log_message("Main container found! Now waiting for content to stream in...")
        
        # Monitor for content appearing in the article
        max_monitoring_time = 90  # seconds
        start_time = time.time()
        last_content_length = 0
        content_stable_time = 0
        stable_threshold = 5  # seconds without content change
        
        while time.time() - start_time < max_monitoring_time:
            # Check for websocket messages
            ws_messages = driver.execute_script("return window.websocket_messages;")
            
            if ws_messages:
                log_message(f"Captured {len(ws_messages)} websocket events")
                
                # Save WebSocket messages to file
                ws_file = os.path.join(log_dir, f"websocket_data_{timestamp}.json")
                with open(ws_file, "w") as f:
                    json.dump(ws_messages, f, indent=2)
            
            # Try to get article content
            try:
                article = driver.find_element(By.XPATH, article_xpath)
                current_content = article.text
                
                if current_content:
                    if len(current_content) != last_content_length:
                        log_message(f"Content updated (length: {len(current_content)})")
                        content_stable_time = time.time()
                        last_content_length = len(current_content)
                    elif time.time() - content_stable_time > stable_threshold:
                        log_message("Content appears to be complete (no changes for 5 seconds)")
                        
                        # Save final content
                        content_file = os.path.join(log_dir, f"final_content_{timestamp}.txt")
                        with open(content_file, "w") as f:
                            f.write(current_content)
                        
                        log_message(f"Final content saved to {content_file}")
                        log_message(f"WebSocket data saved to {ws_file}")
                        break
            except:
                pass
            
            time.sleep(1)
        
        # Analyze WebSocket data to find the source of content
        ws_messages = driver.execute_script("return window.websocket_messages;")
        content_sources = []
        
        for msg in ws_messages:
            if msg.get('type') == 'received':
                try:
                    data = msg.get('data')
                    if isinstance(data, dict) and ('content' in data or 'answer' in data or 'text' in data):
                        content_sources.append(msg)
                except:
                    pass
        
        if content_sources:
            log_message(f"Found {len(content_sources)} potential content source messages")
            source_file = os.path.join(log_dir, f"content_sources_{timestamp}.json")
            with open(source_file, "w") as f:
                json.dump(content_sources, f, indent=2)
            log_message(f"Content sources saved to {source_file}")
        
        # Keep browser open for inspection
        input("Press Enter to close the browser...")
        
    except Exception as e:
        log_message(f"Error: {e}")
    
    finally:
        driver.quit()
        log_message("Browser closed")

def get_coursehero_answer(question_id, headless=False):
    """
    Extract AI-generated answer from CourseHero using Selenium.
    
    Args:
        question_id: The CourseHero question ID (from the URL)
        headless: Whether to run Firefox in headless mode
    
    Returns:
        The full AI-generated answer text
    """
    # Set up logging
    log_dir = "coursehero_logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"content_{timestamp}.txt")
    
    # Set up Firefox with custom profile (already logged in)
    firefox_profile_path = "/Users/anoopkondepudi/Library/Application Support/Firefox/Profiles/43gkv1wz.coursehero"
    options = Options()
    options.add_argument("-profile")
    options.add_argument(firefox_profile_path)
    options.headless = headless  # Set to True to run without UI
    
    print(f"Starting Firefox with profile: {firefox_profile_path}")
    driver = webdriver.Firefox(options=options)
    
    try:
        # Open the question URL
        url = f"https://www.coursehero.com/tutors-problems/Physics/{question_id}-A-20-kg-kangaroo-is-bouncing-as-kangaroos-are-wont-to-do-During-a/?justUnlocked=1"
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Add JavaScript to monitor the AI content
        print("Setting up content monitoring...")
        driver.execute_script("""
            window.aiContent = {
                fullText: "",
                updates: [],
                isComplete: false
            };
            
            // Function to check if content has changed
            function monitorAIContent() {
                const article = document.querySelector('[data-testid="ai-message"]');
                if (article) {
                    const currentText = article.innerText || article.textContent;
                    if (currentText && currentText !== window.aiContent.fullText) {
                        window.aiContent.fullText = currentText;
                        window.aiContent.updates.push({
                            time: new Date().toISOString(),
                            length: currentText.length,
                            text: currentText
                        });
                        
                        // Check if content appears to be complete
                        if (window.aiContent.updates.length > 5) {
                            const lastTwo = window.aiContent.updates.slice(-2);
                            if (lastTwo[0].text === lastTwo[1].text && 
                                lastTwo[0].text.length > 50) {
                                window.aiContent.isComplete = true;
                            }
                        }
                    }
                }
            }
            
            // Start monitoring
            window.aiContentInterval = setInterval(monitorAIContent, 500);
        """)
        
        # Wait for the main container
        print("Waiting for content container to appear...")
        main_container_xpath = '//*[@id="block_ssi:component:SsiQuestionLanding"]/div/div[2]/div/main/div[1]/div/div/div[2]/div/div[2]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, main_container_xpath))
        )
        
        # Wait and check for content
        max_wait_time = 90  # seconds
        wait_increment = 1
        total_wait = 0
        last_length = 0
        stable_count = 0
        
        print("Monitoring for answer content...")
        while total_wait < max_wait_time:
            # Check content status
            content_data = driver.execute_script("return window.aiContent;")
            
            current_text = content_data.get("fullText", "")
            is_complete = content_data.get("isComplete", False)
            
            # If we have new content, show progress
            if current_text and len(current_text) != last_length:
                last_length = len(current_text)
                print(f"Content length: {last_length} characters")
                stable_count = 0
            else:
                stable_count += 1
            
            # Check if content is stable (hasn't changed for a while)
            content_stable = (stable_count >= 10 and last_length > 50)
            
            # If content is complete or stable, we're done
            if (is_complete or content_stable) and last_length > 100:
                print(f"Content appears complete! Length: {last_length}")
                
                # Save content to file
                with open(log_file, "w") as f:
                    f.write(current_text)
                print(f"Content saved to: {log_file}")
                
                return current_text
            
            # Wait before checking again
            time.sleep(wait_increment)
            total_wait += wait_increment
        
        # If we got here, we timed out
        print(f"Timed out after {max_wait_time} seconds")
        
        # Try to get whatever content we have
        final_content = driver.execute_script("return window.aiContent.fullText;")
        if final_content:
            print(f"Returning partial content ({len(final_content)} characters)")
            with open(log_file, "w") as f:
                f.write(final_content)
            print(f"Partial content saved to: {log_file}")
            return final_content
        
        return "No content retrieved"
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        # Clean up JavaScript interval
        driver.execute_script("clearInterval(window.aiContentInterval);")
        
        if not headless:
            input("Press Enter to close the browser...")
        
        # Close browser
        driver.quit()
        print("Browser closed")

def main():
    # Set the question ID
    question_id = "60895488"  # The kangaroo physics problem
    
    print(f"Getting answer for question ID: {question_id}")
    answer = get_coursehero_answer(question_id, headless=False)
    
    if answer:
        print("\n=== ANSWER CONTENT ===")
        print(answer[:500] + "..." if len(answer) > 500 else answer)
        print(f"\nTotal length: {len(answer)} characters")
    else:
        print("Failed to retrieve answer")

if __name__ == "__main__":
    main()
