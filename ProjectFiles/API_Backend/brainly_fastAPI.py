import os
import time
import glob
import shutil
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, HttpUrl
import uvicorn
from typing import Optional, List, Dict, Any

# Import the Brainly scraper modules
import brainly_scraper

# Create FastAPI app
app = FastAPI(
    title="Brainly Scraper API",
    description="API for scraping Brainly questions and answers",
    version="1.0.0"
)

# Path to Downloaded Files folder
DOWNLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Downloaded Files")

# Ensure the downloads directory exists
os.makedirs(DOWNLOADS_PATH, exist_ok=True)

# Models for API requests and responses
class ScrapeRequest(BaseModel):
    url: HttpUrl
    
class ScrapeResponse(BaseModel):
    success: bool
    community_file: Optional[str] = None
    expert_file: Optional[str] = None
    has_expert_answer: bool
    message: str

@app.get("/")
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "name": "Brainly Scraper API", 
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This information page"},
            {"path": "/scrape", "method": "POST", "description": "Scrape a Brainly question URL"},
            {"path": "/files", "method": "GET", "description": "List all downloaded files"},
            {"path": "/files/{filename}", "method": "GET", "description": "Get a specific downloaded file"}
        ]
    }

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_brainly_url(request: ScrapeRequest):
    """
    Scrape a Brainly question URL to get community and expert answers if available.
    
    Parameters:
    - url: The Brainly question URL to scrape
    
    Returns:
    - Information about the scraped files and their locations
    """
    url = str(request.url)
    
    # Clean up any old files that might interfere with our download detection
    cleanup_old_downloads()
    
    try:
        # Use the existing scraper to process the question
        brainly_scraper.process_brainly_question(url)
        
        # Get the downloaded files
        community_file = find_latest_file("brainly_community_answer_")
        expert_file = find_latest_file("brainly_expert_answer_")
        
        # Prepare the response
        if community_file:
            response = ScrapeResponse(
                success=True,
                community_file=os.path.basename(community_file),
                expert_file=os.path.basename(expert_file) if expert_file else None,
                has_expert_answer=bool(expert_file),
                message="Scraping completed successfully"
            )
        else:
            response = ScrapeResponse(
                success=False,
                has_expert_answer=False,
                message="Failed to scrape the page. Possible captcha or connection issue."
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping URL: {str(e)}")

@app.get("/files", response_model=List[str])
async def list_files():
    """List all downloaded HTML files."""
    try:
        html_files = glob.glob(os.path.join(DOWNLOADS_PATH, "*.html"))
        return [os.path.basename(file) for file in html_files]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/files/{filename}", response_class=HTMLResponse)
async def get_file(filename: str):
    """Get a specific downloaded HTML file."""
    file_path = os.path.join(DOWNLOADS_PATH, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    """Download a specific HTML file."""
    file_path = os.path.join(DOWNLOADS_PATH, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    return FileResponse(
        path=file_path, 
        filename=filename,
        media_type="text/html"
    )

def find_latest_file(prefix):
    """Find the most recent file with the given prefix."""
    matching_files = glob.glob(os.path.join(DOWNLOADS_PATH, f"{prefix}*.html"))
    if not matching_files:
        return None
    
    return max(matching_files, key=os.path.getctime)

def cleanup_old_downloads(max_age_hours=24):
    """Clean up old downloaded files to prevent disk space issues."""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for file_path in glob.glob(os.path.join(DOWNLOADS_PATH, "*.html")):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > max_age_seconds:
                os.remove(file_path)
                print(f"Removed old file: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    uvicorn.run("brainly_fastAPI:app", host="0.0.0.0", port=8000, reload=True) 