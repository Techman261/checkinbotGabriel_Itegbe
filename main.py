# INF601 - Advanced Programming in Python
# Gabriel Itegbe
# Scheduled Check-In Bot

import os
import requests
import json
from dotenv import load_dotenv
import time

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
    
    # API uses limit and offset for pagination
    limit = 50 
    offset = 0
    
    while True:
        # Pass author to filter server-side, and use offset for pagination
        resp = requests.get(
            f"{BASE_URL}/api/v1/posts", 
            headers=headers,
            params={"author": INSTRUCTOR_ID, "limit": limit, "offset": offset}
        )
        
        if resp.status_code != 200:
            print(f"Failed to fetch posts. Status code: {resp.status_code}")
            break
            
        posts = resp.json()
        
        # If the list is empty, we have reached the end of the posts
        if not posts: 
            break 
            
        for post in posts:
            collected_data.append({
                "title": post.get("title"),
                "body": post.get("body"),
                "tags": post.get("tags"),
                "timestamp": post.get("created_at")
            })
            
            attachments = post.get("attachments", [])
            for att in attachments:
                file_url = att.get("download_url")
                file_name = att.get("filename")
                
                if file_url and file_name:
                    print(f"Downloading attachment: {file_name}")
                    blob_resp = requests.get(f"{BASE_URL}{file_url}", headers=headers)
                    
                    if blob_resp.status_code == 200:
                        with open(os.path.join(FILES_DIR, file_name), "wb") as f:
                            f.write(blob_resp.content)
                        
        # Increase the offset to get the next batch of posts
        offset += limit
        
        # Pause for 1 second so the server doesn't disconnect us
        time.sleep(1)

    with open(JSON_PATH, "w") as f:
        json.dump(collected_data, f, indent=4)
    print("Post collection complete.")
def process_checkins():
    """Task 2: Find check-ins and reply to them."""
    print("Looking for check-ins...")
    
    # Get your own user ID to check existing comments
    me_resp = requests.get(f"{BASE_URL}/api/v1/me", headers=headers)
    if me_resp.status_code != 200:
        print("Could not fetch user profile.")
        return
    my_id = me_resp.json().get("id")
    
    limit = 50
    offset = 0
    
    while True:
        resp = requests.get(
            f"{BASE_URL}/api/v1/posts",
            headers=headers,
            params={"author": INSTRUCTOR_ID, "limit": limit, "offset": offset}
        )
        if resp.status_code != 200:
            break
            
        posts = resp.json()
        if not posts:
            break
            
        for post in posts:
            title = post.get("title", "")
            
            # Identify instructor check-in posts
            if "check-in" in title.lower():
                post_id = post.get("id")
                
                # Fetch existing comments
                comments_resp = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/comments", headers=headers)
                if comments_resp.status_code == 200:
                    existing_comments = comments_resp.json()
                    
                    # Verify if you have already commented
                    already_replied = any(str(comment.get("author_id")) == str(my_id) for comment in existing_comments)
                    
                    if not already_replied:
                        reply_payload = {"body": "Checking in!"}
                        post_resp = requests.post(
                            f"{BASE_URL}/api/v1/posts/{post_id}/comments", 
                            headers=headers, 
                            json=reply_payload
                        )
                        
                        if post_resp.status_code == 423:
                            print(f"Window closed for check-in {post_id}.")
                        elif post_resp.status_code == 201:
                            print(f"Successfully checked in for post {post_id}.")
                        else:
                            print(f"Failed to check in. Status: {post_resp.status_code}")
                    else:
                        print(f"Already checked in for post {post_id}.")
        
        offset += limit

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("PRACTICE_API_TOKEN is not set. Check your .env file.")
    setup_directories()
    collect_posts()
    process_checkins()