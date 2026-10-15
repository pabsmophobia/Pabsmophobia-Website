import os
import re
import glob
import textwrap
import subprocess
import markdown
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Brand Color Palette
BG_COLOR = "#0b0114"
CARD_BG = "#18032c"
CARD_BORDER = "#a855f7"
TEXT_TITLE = "#ffffff"
TEXT_BODY = "#f3e8ff"
ACCENT_GREEN = "#39ff14"
ACCENT_RED = "#ff3333"

def get_latest_blog_file(target_dir):
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
    title = title_match.group(1).strip() if title_match else "Pabsmophobia Update"
    
    clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
    html = markdown.markdown(clean_text, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')
    
    content_items = []
    
    # Process tables cleanly if present (e.g. equipment or comparative matrices)
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols_text = [c.text.strip() for c in cols if c.text.strip()]
            if cols_text and not any(':---' in c for c in cols_text):
                content_items.append(" | ".join(cols_text))

    # Pull standard paragraphs, lists, and headings for universal compatibility
    raw_nodes = soup.find_all(['h3', 'h4', 'li', 'p'])
    for node in raw_nodes:
        txt = node.text.strip()
        if not txt or len(txt) < 10 or ':---' in txt or txt.startswith('>'):
            continue
        txt = re.sub(r'\s+', ' ', txt)
        # Keep item length readable for mobile cards
        if len(txt) > 130:
            txt = txt[:127] + "..."
        if txt not in content_items:
            content_items.append(txt)
        
    if not content_items:
        content_items = ["Explore full investigation logs and insights live at pabsmophobia.com."]
        
    return title, content_items

def create_hook_slide(title_text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_title = ImageFont.truetype(font_path_bold, 58) if os.path.exists(font_path_bold) else ImageFont.load_default()
    font_brand = ImageFont.truetype(font_path_bold, 30) if os.path.exists(font_path_bold) else ImageFont.load_default()

    # Outer Container Card
    draw.rectangle([40, 40, 1040, 1880], fill=CARD_BG, outline=CARD_BORDER, width=6)
    
    # Top Tag
    draw.rounded_rectangle([90, 120, 500, 190], radius=8, fill="#2e0854", outline=ACCENT_GREEN, width=3)
    draw.text((120, 137), "PABSMOPHOBIA INSIGHTS", fill=ACCENT_GREEN, font=font_brand)

    # Giant Hook Headline
    y_offset = 380
    wrapped_title = textwrap.wrap(title_text.upper(), width=16)
    for line in wrapped_title:
        draw.text((90, y_offset), line, fill=TEXT_TITLE, font=font_title)
        y_offset += 75

    y_offset += 30
    draw.line([90, y_offset, 990, y_offset], fill=ACCENT_GREEN, width=4)
    y_offset += 50

    draw.text((90, y_offset), ">> SWIPE FOR KEY TAKEAWAYS", fill=ACCENT_GREEN, font=font_brand)
    draw.text((90, 1780), "PABSMOPHOBIA.COM", fill=TEXT_BODY, font=font_brand)
    
    img.save(output_path)

def create_content_slide(header_text, body_items, output_path, slide_num):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    font_header = ImageFont.truetype(font_path_bold, 40) if os.path.exists(font_path_bold) else ImageFont.load_default()
    font_body = ImageFont.truetype(font_path_reg, 26) if os.path.exists(font_path_reg) else ImageFont.load_default()
    font_brand = ImageFont.truetype(font_path_bold, 30) if os.path.exists(font_path_bold) else ImageFont.load_default()

    draw.rectangle([40, 40, 1040, 1880], fill=CARD_BG, outline=CARD_BORDER, width=6)
    draw.rectangle([90, 100, 990, 106], fill=ACCENT_GREEN)

    draw.text((90, 140), header_text.upper(), fill=ACCENT_GREEN, font=font_header)
    draw.line([90, 210, 990, 210], fill="#4c1d95", width=3)

    y_offset = 260
    # Limit to 3 items per slide for optimal readability on mobile screens
    for item in body_items[:3]:
        wrapped_item = textwrap.wrap(item, width=40)
        if wrapped_item:
            draw.ellipse([90, y_offset + 6, 104, y_offset + 20], fill=ACCENT_GREEN)
            for line in wrapped_item:
                draw.text((130, y_offset), line, fill=TEXT_BODY, font=font_body)
                y_offset += 36
            y_offset += 24

    draw.text((90, 1720), f"SLIDE {slide_num} / 3", fill=ACCENT_RED, font=font_brand)
    draw.text((580, 1780), "pabsmophobia.com", fill=TEXT_TITLE, font=font_brand)
    
    img.save(output_path)

if __name__ == "__main__":
    target_dir = "_posts"  # Adjust directory path to your markdown files (e.g., "newsletter" or "_posts")
    latest_file = get_latest_blog_file(target_dir)
    
    if not latest_file:
        title = "Pabsmophobia Investigation Log"
        content = ["Read full investigative reports and insights live at pabsmophobia.com."]
    else:
        title, content = parse_markdown(latest_file)

    mid = (len(content) + 1) // 2 if len(content) > 1 else 1
    slide_1_items = content[:mid]
    slide_2_items = content[mid:] if len(content) > 1 else ["Explore the full article and field findings on our site."]

    create_hook_slide(title, "images/tiktok/slide_1.png")
    create_content_slide("FIELD INSIGHTS", slide_1_items, "images/tiktok/slide_2.png", 2)
    create_content_slide("KEY TAKEAWAYS", slide_2_items, "images/tiktok/slide_3.png", 3)
    
    print("TikTok slides generated successfully with universal Option 2 headings!")
