import os
import sys
import time
import subprocess
import re
import glob
import requests

def main():
    post_text = "New update live now. Check out full details at pabsmophobia.com #paranormal #investigation #pabsmophobia"
    latest_md = None

    try:
        git_cmd = ['git', 'log', '-n', '1', '--name-only', '--pretty=format:', '--', 'newsletter/*.md']
        output = subprocess.check_output(git_cmd).decode('utf-8').strip()
        files = [f.strip() for f in output.split('\n') if f.strip() and os.path.exists(f.strip())]
        if files:
            latest_md = files[0]
    except Exception as e:
        print(f"Git log lookup failed: {e}")

    if not latest_md:
        md_files = glob.glob('newsletter/*.md')
        if md_files:
            latest_md = max(md_files, key=os.path.getmtime)

    if latest_md:
        print(f"Selected newsletter file: {latest_md}")
        with open(latest_md, 'r', encoding='utf-8') as f:
            content = f.read()

        title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
        if title_match:
            headline = title_match.group(1).strip()
        else:
            clean_content = re.sub(r'^---[\s\S]*?---\s*', '', content).strip()
            lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
            headline = lines[0].replace('#', '').strip() if lines else 'New Field Log'

        post_text = f"{headline}\n\nRead full report at pabsmophobia.com #paranormal #investigation #pabsmophobia"

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
    if not res.ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
