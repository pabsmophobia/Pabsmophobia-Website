import os
import sys
import time
import datetime
import subprocess
import glob
import re
import requests
import markdown
from bs4 import BeautifulSoup

TIMESTAMP_FILE = ".last_tiktok_post"
MAX_POSTS_PER_MONTH = 8  # Adjust based on your Postproxy plan limit (e.g., 2 times/week * 4 weeks)

def get_recent_articles(target_dir="_posts", days_back=4):
    """Finds all markdown articles added or modified recently since the last run."""
    last_run_time = 0
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            try:
                last_run_time = float(f.read().strip())
            except ValueError:
                pass

    # Fallback: if no timestamp file, default to looking back ~4 days (twice a week window)
    if last_run_time == 0:
        last_run_time = time.time() - (days_back * 86400)

    all_posts = glob.glob(os.path.join(target_dir, "*.md"))
    recent_posts = []

    for post in all_posts:
        mtime = os.path.getmtime(post)
        if mtime >= last_run_time:
            recent_posts.append((mtime, post))

    # Sort by newest first
    recent_posts.sort(key=lambda x: x[0], reverse=True)
    return [p[1] for p in recent_posts]

def parse_multiple_articles(file_paths):
    """Pools titles and key points from multiple articles into a single summary."""
    headlines = []
    pooled_insights = []

    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Pabsmophobia Update"
        headlines.append(title)

        clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
        html = markdown.markdown(clean_text, extensions=['tables'])
        soup = BeautifulSoup(html, 'html.parser')

        # Extract top bullet or paragraph from each article
        for p in soup.find_all(['p', 'li']):
            txt = p.text.strip()
            if len(txt) > 15 and not txt.startswith('>'):
                pooled_insights.append(f"{title[:25]}...: {txt}")
                break

    main_headline = " | ".join(headlines[:2]) if len(headlines) > 1 else headlines[0]
    return main_headline, pooled_insights[:6]  # Pool top takeaways

def main():
    # Rate Limiting Check: Ensure at least 3.5 days (approx twice a week) have passed
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            last_run = float(f.read().strip())
        elapsed_days = (time.time() - last_run) / 86400
        if elapsed_days < 3.2:
            print(f"Rate limit active: Last TikTok post was {elapsed_days:.1f} days ago. Skipping to save monthly quota.")
            sys.exit(0)

    target_dir = "_posts"  # Update to your markdown directory
    recent_files = get_recent_articles(target_dir)

    if not recent_files:
        print("No new articles found since the last run. Skipping TikTok post.")
        sys.exit(0)

    print(f"Found {len(recent_files)} new/recent article(s) to pool together.")
    headline, insights = parse_multiple_articles(recent_files)

    post_text = f"{headline}\n\nRead full reports at pabsmophobia.com #paranormal #investigation #pabsmophobia"

    commit_sha = os.environ.get('COMMIT_SHA', 'latest')
    video_url = f"https://pabsmophobia.com/images/tiktok/slideshow.mp4?v={commit_sha}"

    print(f"Waiting for video accessibility at {video_url}...")
    for attempt in range(15):
        try:
            check = requests.get(video_url, timeout=10)
            if check.status_code == 200 and len(check.content) > 1000:
                print("Video verified on live server.")
                break
        except Exception:
            pass
        print(f"Attempt {attempt+1}/15: Waiting for deployment...")
        time.sleep(12)

    url = "https://api.postproxy.dev/api/posts"
    headers = {
        "Authorization": f"Bearer {os.environ['TIKTOK_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "profiles": [os.environ['TIKTOK_PROFILE_ID']],
        "media": [video_url],
        "post": {
            "body": post_text
        }
    }

    res = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Postproxy Response: {res.text}")
    
    if res.ok:
        # Record successful timestamp to enforce the twice-a-week spacing
        with open(TIMESTAMP_FILE, 'w') as f:
            f.write(str(time.time()))
        print("TikTok post successful. Timestamp updated.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
