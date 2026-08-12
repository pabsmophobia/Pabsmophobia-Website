import os
import re
import glob
import textwrap
import subprocess
import markdown
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Brand Color Palette (Deep Purple & Neon Accents)
BG_COLOR = "#120024"       # Deep purple background
CARD_BG = "#1e0038"        # Dark purple card overlay
TEXT_MAIN = "#ffffff"      # Crisp white text
TEXT_MUTED = "#e2d1f9"     # Soft lavender text
ACCENT_PURPLE = "#9d4edd"  # Vibrant brand purple
ACCENT_GREEN = "#39ff14"   # Neon green highlight

def get_latest_newsletter_file(target_dir):
    """Finds the most recently updated markdown file via Git history or mtime."""
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
    
    # Extract title from frontmatter or fall back to first header/default
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Strip frontmatter if present
        clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
        lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
        title = lines[0].replace('#', '').strip() if lines else "New Pabsmophobia Update"
    
    # Convert body to HTML to parse bullets easily
    clean_text = re.sub(r'^---[\s\S]*?---\s*', '', text).strip()
    html = markdown.markdown(clean_text)
    soup = BeautifulSoup(html, 'html.parser')
    bullets = [li.text.strip() for li in soup.find_all('li')[:4]]
    
    if not bullets:
        # Fall back to first non-header paragraph lines
        paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]
        bullets = paragraphs[:3] if paragraphs else ["Read the latest investigation notes live on our website."]
        
    return title, bullets

def create_slide(header_text, body_items, output_path, is_cover=False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 9:16 Vertical Canvas
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    try:
        font_header = ImageFont.truetype(font_path_bold, 58 if is_cover else 48)
        font_body = ImageFont.truetype(font_path_reg, 38)
        font_brand = ImageFont.truetype(font_path_bold, 34)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Draw Brand Container Card
    draw.rectangle([60, 160, 1020, 1760], fill=CARD_BG, outline=ACCENT_PURPLE, width=4)

    # Top Header Accent Banner
    draw.rectangle([100, 220, 980, 226], fill=ACCENT_GREEN)
    
    # Draw Header Text
    y_offset = 280
    header_lines = textwrap.wrap(header_text, width=26 if is_cover else 32)
    for line in header_lines:
        draw.text((100, y_offset), line, fill=ACCENT_PURPLE if is_cover else ACCENT_GREEN, font=font_header)
        y_offset += 70

    y_offset += 40

    # Draw Body Content / Bullet Points
    for item in body_items:
        wrapped_item = textwrap.wrap(item, width=36)
        if wrapped_item:
            # Bullet point indicator
            draw.ellipse([100, y_offset + 12, 116, y_offset + 28], fill=ACCENT_GREEN)
            for i, line in enumerate(wrapped_item):
                draw.text((135, y_offset), line, fill=TEXT_MAIN if is_cover else TEXT_MUTED, font=font_body)
                y_offset += 52
            y_offset += 25  # Space between bullets

    # Footer Branding (Fixed position inside container)
    draw.line([100, 1660, 980, 1660], fill=ACCENT_PURPLE, width=2)
    draw.text((100, 1685), "PABSMOPHOBIA", fill=ACCENT_GREEN, font=font_brand)
    draw.text((680, 1685), "pabsmophobia.com", fill=TEXT_MAIN, font=font_brand)
    
    img.save(output_path)

if __name__ == "__main__":
    target_dir = "newsletter"
    latest_file = get_latest_newsletter_file(target_dir)
    
    if not latest_file:
        print(f"No .md files found in '{target_dir}'. Generating fallback slides.")
        title = "Pabsmophobia Field Log"
        bullets = ["New investigation telemetry and updates live now at pabsmophobia.com"]
    else:
        print(f"Processing latest newsletter file: {latest_file}")
        title, bullets = parse_markdown(latest_file)

    # Slide 1: Cover Title & Teaser
    create_slide(title.upper(), bullets[:1], "images/tiktok/slide_1.png", is_cover=True)
    
    # Slide 2: Key Findings
    create_slide("KEY FINDINGS", bullets, "images/tiktok/slide_2.png", is_cover=False)
    
    print("TikTok purple-themed slides successfully generated!")
