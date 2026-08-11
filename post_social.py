import os
import glob
import re
import requests

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
IG_USER_ID = os.environ.get("IG_USER_ID")
SITE_BASE_URL = "https://pabsmophobia.com"
DEFAULT_IMAGE = "https://pabsmophobia.com/images/library/Pabsmo.jpg"  # Fallback image for Instagram

def get_latest_markdown_file():
    """Finds the most recently modified markdown file in post directories."""
    files = glob.glob("newsletter/*.md") + glob.glob("_posts/*.md") + glob.glob("*.md")
    # Exclude system markdown files
    ignore = ["README.md", "CONTRIBUTING.md"]
    valid_files = [f for f in files if os.path.basename(f) not in ignore]
    
    if not valid_files:
        print("No eligible markdown files found.")
        return None
        
    latest_file = max(valid_files, key=os.path.getmtime)
    print(f"Targeting newest file: {latest_file}")
    return latest_file

def parse_markdown(filepath):
    """Parses frontmatter metadata from markdown."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def extract_val(pattern, default=""):
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else default

    title = extract_val(r'title:\s*"(.*?)"', "New Post Alert!")
    description = extract_val(r'description:\s*"(.*?)"', "")
    slug = extract_val(r'slug:\s*"(.*?)"', "")
    image = extract_val(r'image:\s*"(.*?)"', DEFAULT_IMAGE)
    
    # Extract tags
    tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.*\n?)+)', content)
    tags = []
    if tags_match:
        tags = re.findall(r'-\s*(.*)', tags_match.group(1))

    # Fallback URL if slug isn't explicitly set
    if not slug:
        slug = os.path.splitext(os.path.basename(filepath))[0]
        
    full_url = f"{SITE_BASE_URL}/{slug}"
    return {
        "title": title,
        "description": description,
        "url": full_url,
        "image": image if image.startswith("http") else f"{SITE_BASE_URL}/{image.lstrip('/')}",
        "tags": [t.strip() for t in tags]
    }

def post_to_facebook(data):
    """Posts formatted update + link to Facebook Page."""
    message = f"{data['title']}\n\n{data['description']}\n\nRead the full article:\n{data['url']}"
    endpoint = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "link": data['url'],
        "access_token": META_ACCESS_TOKEN
    }
    response = requests.post(endpoint, data=payload).json()
    print("Facebook API Response:", response)

def post_to_instagram(data):
    """Posts image + caption with hashtags to Instagram Business Profile."""
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
        print("Failed to create Instagram media container:", res)
        return

    # Step 2: Publish Container
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
        print(f"Parsed post data:\n - Title: {post_data['title']}\n - URL: {post_data['url']}")
        
        post_to_facebook(post_data)
        post_to_instagram(post_data)
