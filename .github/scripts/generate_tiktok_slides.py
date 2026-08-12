import os
import re
import glob
import textwrap
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new('RGB', (1080, 1920), color='#0a0a0c')
    draw = ImageDraw.Draw(img)
    
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 65 if is_cover else 45
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    wrapped_lines = []
    for line in text.split('\n'):
        if line.strip():
            wrapped_lines.extend(textwrap.wrap(line, width=28 if is_cover else 35))
        else:
            wrapped_lines.append('')
    
    formatted_text = '\n'.join(wrapped_lines)
    
    draw.text((80, 600), formatted_text, fill='#ffffff' if is_cover else '#d1d5db', font=font, spacing=15)
    draw.text((80, 1750), "PABSMOPHOBIA | pabsmophobia.com", fill='#8b5cf6', font=font)
    
    img.save(output_path)

if __name__ == "__main__":
    target_dir = "newsletter"
    md_files = glob.glob(os.path.join(target_dir, "*.md"))
    
    if not md_files:
        print(f"No .md files found in '{target_dir}'. Generating fallback slides.")
        title = "Pabsmophobia Field Report"
        bullets = ["New sensor telemetry and evidence analysis live on pabsmophobia.com"]
    else:
        latest_file = max(md_files, key=os.path.getmtime)
        print(f"Processing latest file: {latest_file}")
        title, bullets = parse_markdown(latest_file)

    create_slide(f"NEW INVESTIGATION:\n\n{title}", "images/tiktok/slide_1.png", is_cover=True)
    
    takeaways = "KEY FINDINGS:\n\n" + "\n\n".join([f"• {b}" for b in bullets])
    create_slide(takeaways, "images/tiktok/slide_2.png")
    
    print("TikTok slides successfully created!")
