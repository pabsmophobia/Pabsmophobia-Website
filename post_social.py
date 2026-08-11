import os
import requests

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
IG_USER_ID = os.environ.get("IG_USER_ID")

def post_to_facebook(message, image_url=None):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": META_ACCESS_TOKEN
    }
    if image_url:
        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
        payload["url"] = image_url

    response = requests.post(url, data=payload)
    print("Facebook Response:", response.json())

def post_to_instagram(caption, image_url):
    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    container_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
    res = requests.post(container_url, data=container_payload).json()
    container_id = res.get("id")

    if container_id:
        # Step 2: Publish Container
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_res = requests.post(publish_url, data=publish_payload)
        print("Instagram Response:", pub_res.json())

if __name__ == "__main__":
    # Test post
    print("Testing social connection...")
