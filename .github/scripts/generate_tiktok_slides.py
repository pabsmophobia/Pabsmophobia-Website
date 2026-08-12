import os
import re
import markdown
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    title_match = re.search(r'title:\s*"(.*?)"', text)
    title = title_match.group(1) if title_match else "New Pabsmophobia Field Log"
    
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, 'html.parser')
    bullets = [li.text for li in soup.find_all('li')[:4]]
    if not bullets:
        bullets = ["Read the latest investigation log on our website."]
        
    return title, bullets

def create_slide(text, output_path, is_cover=False):
    img = Image.new('RGB', (1080, 1920), color='#0a0a0c')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 55 if not is_cover else 75)
    except:
        font = ImageFont.load_default()
        
    draw.text((100, 700), text, fill='#ffffff' if is_cover else '#d1d5db', font=font)
    draw.text((100, 1700), "PABSMOPHOBIA | pabsmophobia.com", fill='#8b5cf6', font=font)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)

if __name__ == "__main__":
    # Finds the newest file in newsletter/ or blog/
    target_dir = "newsletter"
    files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endsWith('.md')]
    latest_file = max(files, key=os.path.getmtime) if files else None

    if latest_file:
        title, bullets = parse_markdown(latest_file)
        create_slide(f"NEW INVESTIGATION:\n\n{title}", "images/tiktok/slide_1.png", is_cover=True)
        
        takeaways_text = "KEY FINDINGS:\n\n" + "\n\n".join([f"• {b}" for b in bullets])
        create_slide(takeaways_text, "images/tiktok/slide_2.png")
        print(f"Generated slides for {latest_file}")
