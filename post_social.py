import os
import glob
import re
import time
import json
import subprocess
import datetime
import requests

# ---------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------------------------
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
IG_USER_ID = os.environ.get("IG_USER_ID")
TRIGGER_TYPE = os.environ.get("TRIGGER_TYPE", "schedule")
SITE_BASE_URL = "https://pabsmophobia.com"
DEFAULT_IMAGE = "https://pabsmophobia.com/images/library/Pabsmo.jpg"
POSTED_HISTORY_FILE = "posted_history.json"

# List of files to strictly ignore if discovered
IGNORE_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "copilot-instructions.md",
    "CODE_OF_CONDUCT.md",
    "PULL_REQUEST_TEMPLATE.md"
]

# ---------------------------------------------------------------------------
# STATE MANAGEMENT (Prevents Double-Posting)
# ---------------------------------------------------------------------------
def load_posted_history():
    """Loads the set of previously published relative file paths."""
    if os.path.exists(POSTED_HISTORY_FILE):
        try:
            with open(POSTED_HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading posted history: {e}")
    return set()

def save_posted_history(posted_set):
    """Saves the updated set of published relative file paths."""
    try:
        with open(POSTED_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(posted_set)), f, indent=2)
        print(f"Successfully updated {POSTED_HISTORY_FILE}")
    except Exception as e:
        print(f"Error saving posted history: {e}")

# ---------------------------------------------------------------------------
# CONTENT BUILDERS (Events, Blog Hub, and Individual Markdown Posts)
# ---------------------------------------------------------------------------
def get_events_payload():
    """Payload for the static Events page (Shared Mondays and Thursdays)."""
    return {
        "title": "Upcoming Paranormal Investigations & Events",
        "description": "Join us on our next hunt! Check out where we are heading next, secure your spot, and come investigate with the Pabsmophobia team.",
        "url": f"{SITE_BASE_URL}/events",
        "image": DEFAULT_IMAGE,
        "tags": ["ParanormalEvents", "GhostHunt", "Pabsmophobia", "UKParanormal"]
    }

def get_blog_hub_payload():
    """Payload for the main Blog archive page (Shared Tuesdays and Fridays)."""
    return {
        "title": "Explore All Pabsmophobia Articles & Newsletters",
        "description": "Catch up on our latest paranormal investigations, ghost-hunting equipment deep dives, and community updates on our main blog hub!",
        "url": f"{SITE_BASE_URL}/blog",
        "image": DEFAULT_IMAGE,
        "tags": ["ParanormalBlog", "GhostStories", "Pabsmophobia", "Newsletter"]
    }

def get_latest_markdown_payload():
    """Finds unposted Markdown files and builds payload for instant push posting."""
    posted_files = load_posted_history()
    files = glob.glob("newsletter/*.md") + glob.glob("_posts/*.md")
    valid_files = [f for f in files if os.path.basename(f) not in IGNORE_FILES and f not in posted_files]

    if not valid_files:
        return None, None

    target_file = max(valid_files, key=os.path.getmtime)
    print(f"Selected new Markdown file: {target_file}")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    def extract_val(pattern, default=""):
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            val = match.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            return val.strip()
        return default

    title = extract_val(r'^title:\s*(.*)$', "New Paranormal Article")
    description = extract_val(r'^description:\s*(.*)$', "")
    image = extract_val(r'^image:\s*(.*)$', DEFAULT_IMAGE)

    tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.*\n?)+)', content)
    tags = re.findall(r'-\s*(.*)', tags_match.group(1)) if tags_match else []

    if not image.startswith("http"):
        image = f"{SITE_BASE_URL}/{image.lstrip('/')}"

    relative_filepath = target_file.replace("\\", "/")

    payload = {
        "title": title,
        "description": description,
        "url": f"{SITE_BASE_URL}/post?file={relative_filepath}",
        "image": image,
        "tags": [t.strip() for t in tags]
    }
    return payload, target_file

# ---------------------------------------------------------------------------
# SOCIAL API INTEGRATIONS
# ---------------------------------------------------------------------------
def get_page_access_token():
    """Exchanges system token for a dedicated Page Access Token."""
    if not FB_PAGE_ID or not META_ACCESS_TOKEN:
        print("Warning: FB_PAGE_ID or META_ACCESS_TOKEN is missing.")
        return META_ACCESS_TOKEN

    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    try:
        res = requests.get(url).json()
        if "data" in res:
            for page in res["data"]:
                if str(page.get("id")) == str(FB_PAGE_ID):
                    print("Successfully retrieved Page Access Token.")
                    return page.get("access_token")
            print(f"Warning: Page ID {FB_PAGE_ID} not found in accounts list for provided META_ACCESS_TOKEN.")
    except Exception as e:
        print(f"Error fetching Page Access Token: {e}")

    print("Fallback: Using direct System User Token.")
    return META_ACCESS_TOKEN

def post_to_facebook(data, page_token):
    message = f"{data['title']}\n\n{data['description']}\n\nRead the full article here:\n{data['url']}"
    
    endpoint = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    payload = {
        "url": data['image'],
        "message": message,
        "access_token": page_token
    }
    response = requests.post(endpoint, data=payload).json()
    print("Facebook Photo API Response:", response)
    return response

def post_to_instagram(data, page_token):
    if not IG_USER_ID:
        print("Skipping Instagram: IG_USER_ID not provided.")
        return

    hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in data['tags']]) if data.get('tags') else "#Pabsmophobia #Paranormal"
    caption = f"{data['title']}\n\n{data['description']}\n\n🔗 Link in bio to read full post!\n\n{hashtags}"

    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    container_payload = {
        "image_url": data['image'],
        "caption": caption,
        "access_token": page_token
    }
    res = requests.post(container_url, data=container_payload).json()
    container_id = res.get("id")

    if not container_id:
        print("Failed to create Instagram container:", res)
        return

    print(f"Container {container_id} created. Checking processing status...")

    # Step 2: Poll status until FINISHED or ERROR
    status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={page_token}"
    for attempt in range(12):
        status_res = requests.get(status_url).json()
        status = status_res.get("status_code")
        
        if status == "FINISHED":
            print("Instagram media processing complete.")
            break
        elif status == "ERROR":
            print(f"Instagram media processing failed: {status_res}")
            return
        
        print(f"Status is '{status}'. Waiting 5s (attempt {attempt + 1}/12)...")
        time.sleep(5)

    # Step 3: Publish Container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": container_id,
        "access_token": page_token
    }
    pub_res = requests.post(publish_url, data=publish_payload).json()
    print("Instagram API Response:", pub_res)

# ---------------------------------------------------------------------------
# MAIN EXECUTION ROUTER
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    post_data = None
    tracked_file = None

    # RULE 1: If triggered by a manual push with a new .md file, post it instantly!
    if TRIGGER_TYPE == "push":
        print("Triggered by Push event. Checking for unposted markdown files...")
        post_data, tracked_file = get_latest_markdown_payload()

    # RULE 2: If it's a scheduled cron run, use the day-of-the-week mapping
    if not post_data:
        current_day = datetime.datetime.now().strftime("%A")
        print(f"Triggered by Schedule ({current_day}). Evaluating calendar...")

        if current_day in ["Monday", "Thursday"]:
            print("Scheduled Content: EVENTS PAGE")
            post_data = get_events_payload()

        elif current_day in ["Tuesday", "Friday"]:
            print("Scheduled Content: BLOG HUB (/blog)")
            post_data = get_blog_hub_payload()
        else:
            print(f"No scheduled posting rule for {current_day}. Exiting cleanly.")

    # Execute posting if a valid payload is established
    if post_data:
        page_access_token = get_page_access_token()
        post_to_facebook(post_data, page_access_token)
        post_to_instagram(post_data, page_access_token)

        # If it was a tracked markdown file, save it to history so it doesn't re-post
        if tracked_file:
            posted_history = load_posted_history()
            posted_history.add(tracked_file)
            save_posted_history(posted_history)
    else:
        print("No content action required for this run.")
