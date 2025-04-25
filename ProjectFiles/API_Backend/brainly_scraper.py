import os
import time
import glob
import shutil
import signal
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Import the scraper modules
import brainly_community
import brainly_expert

# Path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

# Cache the geckodriver path to avoid reinstalling it multiple times
GECKO_DRIVER_PATH = None

# Keep track of active browser instances for cleanup
active_browsers = []

def get_gecko_driver_path():
    """Get and cache the geckodriver path"""
    global GECKO_DRIVER_PATH
    if GECKO_DRIVER_PATH is None:
        GECKO_DRIVER_PATH = GeckoDriverManager().install()
        print(f"✅ GeckoDriver installed at: {GECKO_DRIVER_PATH}")
    return GECKO_DRIVER_PATH

def get_latest_downloaded_file():
    """Get the most recently downloaded HTML file"""
    html_files = glob.glob(os.path.join(DOWNLOADS_PATH, "*.html"))
    if not html_files:
        return None
    
    return max(html_files, key=os.path.getctime)

def rename_downloaded_file(file_type):
    """Rename the most recently downloaded file to indicate its type"""
    latest_file = get_latest_downloaded_file()
    
    if not latest_file:
        print(f"❌ No file found to rename for {file_type}")
        return None
    
    # Extract question ID from the file name if possible
    file_name = os.path.basename(latest_file)
    question_id = None
    
    # Try to extract question ID from filename or URL
    if "-" in file_name:
        parts = file_name.split("-")
        for part in parts:
            if part.strip().isdigit():
                question_id = part.strip()
                break
    
    # If not found in filename, try from URL
    if not question_id and "question/" in latest_file:
        try:
            question_id = latest_file.split("question/")[1].split("/")[0].split(".")[0]
        except:
            pass
    
    # Create new file name
    if question_id:
        new_name = f"brainly_{file_type}_answer_{question_id}.html"
    else:
        timestamp = int(time.time())
        new_name = f"brainly_{file_type}_answer_{timestamp}.html"
    
    new_path = os.path.join(DOWNLOADS_PATH, new_name)
    
    # Rename the file
    try:
        shutil.move(latest_file, new_path)
        print(f"✅ Renamed file to: {new_name}")
        return new_path
    except Exception as e:
        print(f"❌ Error renaming file: {e}")
        return latest_file

def cleanup_resources():
    """Clean up any resources when the script exits"""
    print("\n🧹 Cleaning up resources...")
    
    # Nothing to clean up currently as browser instances are handled in their own modules
    print("✅ Cleanup complete")

def signal_handler(sig, frame):
    """Handle interruption signals (Ctrl+C)"""
    print("\n⚠️ Received termination signal. Closing gracefully...")
    cleanup_resources()
    sys.exit(0)

def process_brainly_question(url):
    """Process a Brainly question URL to get both community and expert answers if available"""
    print(f"🚀 Starting Brainly scraper for URL: {url}")
    
    # Pre-install geckodriver to avoid multiple installations
    get_gecko_driver_path()
    
    # Step 1: Scrape the community answer and check for expert answer existence
    print("\n📥 GETTING COMMUNITY ANSWER...")
    community_success, has_expert_answer = brainly_community.scrape_brainly(url)
    
    # Wait a moment to ensure file is fully written and browser is fully closed
    time.sleep(2)
    
    # Step 2: Rename the community answer file
    if community_success:
        community_file = rename_downloaded_file("community")
        
        if not community_file:
            print("❌ Failed to get community answer, stopping process")
            return
    else:
        print("❌ Failed to get community answer, stopping process")
        return
    
    # Small delay before starting the next browser instance
    time.sleep(1)
    
    # Step 3: If expert answer exists, scrape it
    if has_expert_answer:
        print("\n📥 GETTING EXPERT ANSWER...")
        brainly_expert.scrape_brainly(url)
        
        # Wait a moment to ensure file is fully written
        time.sleep(2)
        
        # Step 4: Rename the expert answer file
        expert_file = rename_downloaded_file("expert")
        
        if expert_file:
            print(f"✅ Expert answer saved as: {os.path.basename(expert_file)}")
        else:
            print("❌ Failed to save expert answer")
    else:
        print("\nℹ️ No expert answer available for this question")
    
    print("\n✅ Brainly scraping complete!")
    print(f"✅ Community answer saved as: {os.path.basename(community_file)}")

def main():
    """Main function that sets up signal handlers and initiates the process"""
    # Set up signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Example URL - you can change this or accept command line arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://brainly.com/question/9080526"
    
    try:
        process_brainly_question(url)
    except Exception as e:
        print(f"Error in main process: {e}")
    finally:
        cleanup_resources()

if __name__ == "__main__":
    main()
