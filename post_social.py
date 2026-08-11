import os
import glob
import re
import time
import requests

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
IG_USER_ID = os.environ.get("IG_USER_ID")
SITE_BASE_URL = "https://pabsmophobia.com"
DEFAULT_IMAGE = "https://pabsmophobia.com/images/library/Pabsmo.jpg"

def get_page_access_token():
    """Exchanges system token for a dedicated Page Access Token."""
    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    res = requests.get(url).json()
    
    if "data" in res:
        for page in res["data"]:
            if str(page.get("id")) == str(FB_PAGE_ID):
                print("Successfully retrieved Page Access Token.")
                return page.get("access_token")
                
    print("Fallback: Using direct System User Token.")
    return META_ACCESS_TOKEN

def get_latest_markdown_file():
    files = glob.glob("newsletter/*.md") + glob.glob("_posts/*.md") + glob.glob("*.md")
    ignore = ["README.md", "CONTRIBUTING.md"]
    valid_files = [f for f in files if os.path.basename(f) not in ignore]
    
    if not valid_files:
        return None
        
    return max(valid_files, key=os.path.getmtime)

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def extract_val(pattern, default=""):
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else default

    title = extract_val(r'title:\s*"(.*?)"', "New Post Alert!")
    description = extract_val(r'description:\s*"(.*?)"', "")
    slug = extract_val(r'slug:\s*"(.*?)"', "")
    image = extract_val(r'image:\s*"(.*?)"', DEFAULT_IMAGE)
    
    tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.*\n?)+)', content)
    tags = re.findall(r'-\s*(.*)', tags_match.group(1)) if tags_match else []

    if not slug:
        slug = os.path.splitext(os.path.basename(filepath))[0]
        
    return {
        "title": title,
        "description": description,
        "url": f"{SITE_BASE_URL}/{slug}",
        "image": image if image.startswith("http") else f"{SITE_BASE_URL}/{image.lstrip('/')}",
        "tags": [t.strip() for t in tags]
    }

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

def post_to_instagram(data):
    hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in data['tags']])
    caption = f"{data['title']}\n\n{data['description']}\n\n🔗 Link in bio to read full post!\n\n{hashtags}"

    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    container_payload = {
        "image_url": data['image'],
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
    res = requests.post(container_url, data=container_payload).json()
    container_id = res.get("id")

    if not container_id:
        print("Failed to create Instagram container:", res)
        return

    # Step 2: Wait for Instagram processing
    print(f"Container {container_id} created. Waiting 10s for IG to process image...")
    time.sleep(10)

    # Step 3: Publish Container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": container_id,
        "access_token": META_ACCESS_TOKEN
    }
    pub_res = requests.post(publish_url, data=publish_payload).json()
    print("Instagram API Response:", pub_res)

if __name__ == "__main__":
    target_file = get_latest_markdown_file()
    if target_file:
        post_data = parse_markdown(target_file)
        page_access_token = get_page_access_token()
        
        post_to_facebook(post_data, page_access_token)
        post_to_instagram(post_data)
