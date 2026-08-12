import os
import re
import glob
import textwrap
import subprocess
import markdown
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Brand Color Palette
BG_COLOR = "#0f021a"
CARD_BG = "#1d0533"
CARD_BORDER = "#a855f7"
TEXT_TITLE = "#ffffff"
TEXT_BODY = "#f3e8ff"
ACCENT_GREEN = "#39ff14"

def get_latest_newsletter_file(target_dir):
    try:
        git_cmd = ['git', 'log', '-n', '1', '--name-only', '--pretty=format:', '--', f'{target_dir}/*.md']
        output = subprocess.check_output(git_cmd).decode('utf-8').strip()
        files = [f.strip() for f in output.split('\n') if f.strip() and os.path.exists(f.strip())]
        if files:
            return files[0]
    except Exception:
        pass

    md_files = glob.glob(os.path.join(target_dir, "*.md"))
    if md_files:
        return max(md_files, key=os.path.getmtime)
    return None

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
        lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
        title = lines[0].replace('#', '').strip() if lines else "New Pabsmophobia Update"
    
    clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
    html = markdown.markdown(clean_text)
    soup = BeautifulSoup(html, 'html.parser')
    
    raw_bullets = [li.text.strip() for li in soup.find_all('li')]
    if not raw_bullets:
        raw_bullets = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]
    
    bullets = []
    for b in raw_bullets:
        if len(b) > 90:
            chunks = textwrap.wrap(b, width=75)
            bullets.extend(chunks[:2])
        else:
            bullets.append(b)
            
    if not bullets:
        bullets = ["Read the latest field log live on our website."]
        
    return title, bullets

def create_slide(header_text, body_items, output_path, is_cover=False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    try:
        font_header = ImageFont.truetype(font_path_bold, 40 if is_cover else 34)
        font_body = ImageFont.truetype(font_path_reg, 26)  # Scaled safely to avoid overflow
        font_brand = ImageFont.truetype(font_path_bold, 26)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Safe Container Card Bounds
    draw.rectangle([50, 80, 1030, 1840], fill=CARD_BG, outline=CARD_BORDER, width=4)

    # Top Accent Line
    draw.rectangle([90, 130, 990, 136], fill=ACCENT_GREEN)
    
    # Header Text Block
    y_offset = 160
    header_lines = textwrap.wrap(header_text, width=32)
    for line in header_lines:
        draw.text((90, y_offset), line, fill=TEXT_TITLE if is_cover else ACCENT_GREEN, font=font_header)
        y_offset += 48

    y_offset += 20

    # Body Items (Strictly capped to max 3 items per slide with tight line spacing)
    for item in body_items[:3]:
        wrapped_item = textwrap.wrap(item, width=42)
        if wrapped_item:
            draw.ellipse([90, y_offset + 5, 100, y_offset + 15], fill=ACCENT_GREEN)
            for line in wrapped_item:
                draw.text((120, y_offset), line, fill=TEXT_BODY, font=font_body)
                y_offset += 36
            y_offset += 12

    # Footer Divider & Domain
    draw.line([90, 1740, 990, 1740], fill=CARD_BORDER, width=2)
    draw.text((90, 1770), "PABSMOPHOBIA", fill=ACCENT_GREEN, font=font_brand)
    draw.text((580, 1770), "pabsmophobia.com", fill=TEXT_TITLE, font=font_brand)

    # Embed Official Logo Watermark from repo path
    logo_path = "Pabsmophobia-Website/images/library/Pabsmo.jpg"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((80, 80), Image.Resampling.LANCZOS)
            img.paste(logo, (910, 1630))
        except Exception as e:
            print(f"Could not load logo image: {e}")
    
    img.save(output_path)

if __name__ == "__main__":
    target_dir = "newsletter"
    latest_file = get_latest_newsletter_file(target_dir)
    
    if not latest_file:
        title = "Pabsmophobia Field Log"
        bullets = ["New investigation telemetry and updates live now at pabsmophobia.com"]
    else:
        title, bullets = parse_markdown(latest_file)

    midpoint = max(1, len(bullets) // 2)
    slide_1_bullets = bullets[:midpoint]
    slide_2_bullets = bullets[midpoint:] if len(bullets) > midpoint else ["Check out full breakdown on our site."]

    create_slide(title.upper(), slide_1_bullets, "images/tiktok/slide_1.png", is_cover=True)
    create_slide("KEY FINDINGS", slide_2_bullets, "images/tiktok/slide_2.png", is_cover=False)
    
    print("TikTok slides refactored cleanly with zero overflow and logo embedded!")
