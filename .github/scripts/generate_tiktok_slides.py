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
    html = markdown.markdown(clean_text, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')
    
    content_items = []
    
    # Process tables cleanly so columns read as structured labels
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols_text = [c.text.strip() for c in cols if c.text.strip()]
            # Skip pure alignment or empty rows
            if cols_text and not any(':---' in c for c in cols_text):
                content_items.append(" • ".join(cols_text))

    # Pull standard paragraphs and list items, stripping out HTML table markup noise
    raw_nodes = soup.find_all(['li', 'p'])
    for node in raw_nodes:
        txt = node.text.strip()
        if not txt or len(txt) < 10 or ':---' in txt:
            continue
        txt = re.sub(r'\s+', ' ', txt)
        if txt not in content_items:
            content_items.append(txt)
        
    if not content_items:
        content_items = ["Read the latest field log live on our website at pabsmophobia.com."]
        
    return title, content_items

def create_slide(header_text, body_items, output_path, is_cover=False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    try:
        font_header = ImageFont.truetype(font_path_bold, 36 if is_cover else 32)
        font_body = ImageFont.truetype(font_path_reg, 24)
        font_brand = ImageFont.truetype(font_path_bold, 26)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Container Card Bounds
    draw.rectangle([50, 60, 1030, 1860], fill=CARD_BG, outline=CARD_BORDER, width=4)

    # Top Accent Line
    draw.rectangle([90, 110, 990, 116], fill=ACCENT_GREEN)
    
    # Prominent Logo Watermark Loader (110x110)
    workspace_root = os.getcwd()
    logo_paths = [
        os.path.join(workspace_root, "images/library/Pabsmo.jpg"),
        os.path.join(workspace_root, "Pabsmophobia-Website/images/library/Pabsmo.jpg"),
        "images/library/Pabsmo.jpg",
        "Pabsmophobia-Website/images/library/Pabsmo.jpg"
    ]
    
    logo_pasted = False
    for l_path in logo_paths:
        if os.path.exists(l_path):
            try:
                logo = Image.open(l_path).convert("RGBA")
                logo = logo.resize((110, 110), Image.Resampling.LANCZOS)
                img.paste(logo, (880, 125))
                logo_pasted = True
                break
            except Exception:
                pass
                
    if not logo_pasted:
        draw.rounded_rectangle([850, 125, 990, 215], radius=6, fill="#0f021a", outline=ACCENT_GREEN, width=2)
        font_fallback = ImageFont.truetype(font_path_bold, 18) if os.path.exists(font_path_bold) else font_brand
        draw.text((875, 160), "PABSMO", fill=ACCENT_GREEN, font=font_fallback)

    # Header Text Block (Width restricted so it never clips the larger logo)
    y_offset = 140
    header_lines = textwrap.wrap(header_text, width=22)
    for line in header_lines:
        draw.text((90, y_offset), line, fill=TEXT_TITLE if is_cover else ACCENT_GREEN, font=font_header)
        y_offset += 40

    y_offset += 15
    draw.line([90, y_offset, 990, y_offset], fill="#4c1d95", width=2)
    y_offset += 20

    # Body Items / Structured Data Blocks
    for item in body_items[:4]:
        wrapped_item = textwrap.wrap(item, width=46)
        if wrapped_item:
            draw.ellipse([90, y_offset + 4, 100, y_offset + 14], fill=ACCENT_GREEN)
            for line in wrapped_item:
                draw.text((120, y_offset), line, fill=TEXT_BODY, font=font_body)
                y_offset += 30
            y_offset += 12

    # Footer Branding & Domain
    draw.line([90, 1760, 990, 1760], fill=CARD_BORDER, width=2)
    draw.text((90, 1790), "PABSMOPHOBIA", fill=ACCENT_GREEN, font=font_brand)
    draw.text((580, 1790), "pabsmophobia.com", fill=TEXT_TITLE, font=font_brand)
    
    img.save(output_path)

if __name__ == "__main__":
    target_dir = "newsletter"
    latest_file = get_latest_newsletter_file(target_dir)
    
    if not latest_file:
        title = "Pabsmophobia Field Log"
        content = ["New investigation telemetry and updates live now at pabsmophobia.com."]
    else:
        title, content = parse_markdown(latest_file)

    total_items = len(content)
    if total_items <= 1:
        slide_1 = content
        slide_2 = ["Read the full breakdown and field logs at pabsmophobia.com."]
    else:
        mid = (total_items + 1) // 2
        slide_1 = content[:mid]
        slide_2 = content[mid:]
        if not slide_2:
            slide_2 = ["Check out full investigation findings on our site."]

    create_slide(title.upper(), slide_1, "images/tiktok/slide_1.png", is_cover=True)
    create_slide("KEY FINDINGS", slide_2, "images/tiktok/slide_2.png", is_cover=False)
    
    print("TikTok slides generated with clean table parsing and prominent logo!")
