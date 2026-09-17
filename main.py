# INF601 - Advanced Programming in Python
# Gabriel Itegbe
# Scheduled Check-In Bot

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve configuration from environment variables
TOKEN = os.environ.get("PRACTICE_API_TOKEN")
BASE_URL = os.environ.get("PRACTICE_API_URL")
INSTRUCTOR_ID = os.environ.get("INSTRUCTOR_ID")

headers = {"Authorization": f"Bearer {TOKEN}"}

# --- NEW PATH LOGIC ---
# Get the absolute path to the directory where main.py lives
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the exact paths for the artifact folder and its contents
ARTIFACT_DIR = os.path.join(PROJECT_DIR, "artifact")
FILES_DIR = os.path.join(ARTIFACT_DIR, "files")
JSON_PATH = os.path.join(ARTIFACT_DIR, "collected.json")
# ----------------------

def setup_directories():
    """Ensure the artifact directories exist inside the project folder."""
    os.makedirs(FILES_DIR, exist_ok=True)

def collect_posts():
    """Task 1: Collect all instructor posts and download attachments."""
    print("Starting post collection...")
    collected_data = []
    page = 1
    
    while True:
        resp = requests.get(f"{BASE_URL}/api/v1/posts?page={page}", headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch posts. Status code: {resp.status_code}")
            break
            
        posts = resp.json()
        if not posts: 
            break # Exit loop if the page is empty
            
        for post in posts:
            if str(post.get("author_id")) == str(INSTRUCTOR_ID):
                
                # 1. Save the text data
                collected_data.append({
                    "title": post.get("title"),
                    "body": post.get("body"),
                    "tags": post.get("tags"),
                    "timestamp": post.get("created_at")
                })
                
                # 2. Handle attachments
                attachments = post.get("attachments", [])
                for file_info in attachments:
                    file_url = file_info.get("url")
                    file_name = file_info.get("name")
                    if file_url and file_name:
                        print(f"Downloading attachment: {file_name}")
                        file_resp = requests.get(file_url, headers=headers)
                        with open(f"artifact/files/{file_name}", "wb") as f:
                            f.write(file_resp.content)
                            
        page += 1

    # Save the collected data to collected.json
    with open(os.path.join(FILES_DIR, file_name), "wb") as f:
        json.dump(collected_data, f, indent=4)
    print("Post collection complete.")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("PRACTICE_API_TOKEN is not set. Check your .env file.")
    setup_directories()
    collect_posts()