import os
import glob
import re
import time
import json
import subprocess
import requests

# ---------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------------------------
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
IG_USER_ID = os.environ.get("IG_USER_ID")
SITE_BASE_URL = "https://pabsmophobia.com"
DEFAULT_IMAGE = "https://pabsmophobia.com/images/library/Pabsmo.jpg"
POSTED_HISTORY_FILE = "posted_history.json"

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
# FILE FINDER & PARSER
# ---------------------------------------------------------------------------
def get_latest_markdown_file():
    """
    Finds the newest unposted Markdown file by querying Git commit history.
    Falls back to OS file modification time if Git fails.
    """
    posted_files = load_posted_history()
    ignore = ["README.md", "CONTRIBUTING.md"]

    # --- METHOD 1: Try Git log (Most reliable for commit order) ---
    try:
        cmd = [
            "git", "log", "--name-only", "--format=", 
            "--", "newsletter/*.md", "_posts/*.md", "*.md"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        git_files = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        for filepath in git_files:
            filename = os.path.basename(filepath)
            if filename not in ignore and filepath not in posted_files:
                if os.path.exists(filepath):
                    print(f"Selected via Git history: {filepath}")
                    return filepath
    except Exception as e:
        print(f"Git lookup skipped/failed ({e}). Falling back to local file times...")

    # --- METHOD 2: Fallback to local glob / mtime ---
    files = glob.glob("newsletter/*.md") + glob.glob("_posts/*.md") + glob.glob("*.md")
    valid_files = [
        f for f in files 
        if os.path.basename(f) not in ignore and f not in posted_files
    ]

    if not valid_files:
        return None

    selected = max(valid_files, key=os.path.getmtime)
    print(f"Selected via file modification time: {selected}")
    return selected

def parse_markdown(filepath):
    """Extracts metadata from front matter or provides defaults."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def extract_val(pattern, default=""):
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            val = match.group(1).strip()
            # Strip outer single/double quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            return val.strip()
        return default

    title = extract_val(r'^title:\s*(.*)$', "New Post Alert!")
    description = extract_val(r'^description:\s*(.*)$', "")
    slug = extract_val(r'^slug:\s*(.*)$', "")
    image = extract_val(r'^image:\s*(.*)$', DEFAULT_IMAGE)

    tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.*\n?)+)', content)
    tags = re.findall(r'-\s*(.*)', tags_match.group(1)) if tags_match else []

    if not slug:
        slug = os.path.splitext(os.path.basename(filepath))[0]

    # Standardize image URL
    if not image.startswith("http"):
        image = f"{SITE_BASE_URL}/{image.lstrip('/')}"

    return {
        "title": title,
        "description": description,
        "url": f"{SITE_BASE_URL}/{slug}",
        "image": image,
        "tags": [t.strip() for t in tags]
    }

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
    except Exception as e:
        print(f"Error fetching Page Access Token: {e}")

    print("Fallback: Using direct System User Token.")
    return META_ACCESS_TOKEN

def post_to_facebook(data, page_token):
    message = f"{data['title']}\n\n{data['description']}\n\nRead more:\n{data['url']}"
    endpoint = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "link": data['url'],
        "access_token": page_token
    }
    response = requests.post(endpoint, data=payload).json()
    print("Facebook API Response:", response)
    return response

def post_to_instagram(data, page_token):
    if not IG_USER_ID:
        print("Skipping Instagram: IG_USER_ID not provided.")
        return

    hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in data['tags']])
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
# MAIN EXECUTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    target_file = get_latest_markdown_file()

    if target_file:
        print(f"Processing target file: {target_file}")
        post_data = parse_markdown(target_file)
        page_access_token = get_page_access_token()

        post_to_facebook(post_data, page_access_token)
        post_to_instagram(post_data, page_access_token)

        # Record file as posted so it's skipped in future runs
        posted_history = load_posted_history()
        posted_history.add(target_file)
        save_posted_history(posted_history)
    else:
        print("No new markdown files to post. Exiting cleanly.")
