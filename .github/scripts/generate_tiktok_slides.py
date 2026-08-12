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
    
    # Extract clean text chunks from list items or paragraphs
    raw_nodes = soup.find_all(['li', 'p'])
    clean_sentences = []
    
    for node in raw_nodes:
        txt = node.text.strip()
        if not txt or len(txt) < 15: # Skip tiny headings or structural noise
            continue
        # Clean up weird spacing or mid-sentence line breaks from markdown parsing
        txt = re.sub(r'\s+', ' ', txt)
        clean_sentences.append(txt)
        
    if not clean_sentences:
        clean_sentences = ["Read the latest field log live on our website."]
        
    return title, clean_sentences

def create_slide(header_text, body_items, output_path, is_cover=False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new('RGB', (1080, 1920), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_path_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    try:
        font_header = ImageFont.truetype(font_path_bold, 38 if is_cover else 34)
        font_body = ImageFont.truetype(font_path_reg, 26)
        font_brand = ImageFont.truetype(font_path_bold, 26)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Container Card Bounds
    draw.rectangle([50, 60, 1030, 1860], fill=CARD_BG, outline=CARD_BORDER, width=4)

    # Top Accent Line
    draw.rectangle([90, 110, 990, 116], fill=ACCENT_GREEN)
    
    # Embed Logo Watermark using the exact requested path `images/library/Pabsmo.jpg`
    logo_paths_to_try = [
        "images/library/Pabsmo.jpg",
        "Pabsmophobia-Website/images/library/Pabsmo.jpg",
        "images/library/pabsmo.jpg"
    ]
    logo_pasted = False
    for l_path in logo_paths_to_try:
        if os.path.exists(l_path):
            try:
                logo = Image.open(l_path).convert("RGBA")
                logo = logo.resize((75, 75), Image.Resampling.LANCZOS)
                img.paste(logo, (915, 135))
                logo_pasted = True
                break
            except Exception:
                pass
                
    if not logo_pasted:
        draw.rounded_rectangle([880, 135, 990, 200], radius=6, fill="#0f021a", outline=ACCENT_GREEN, width=2)
        font_fallback = ImageFont.truetype(font_path_bold, 18) if os.path.exists(font_path_bold) else font_brand
        draw.text((895, 153), "PABSMO", fill=ACCENT_GREEN, font=font_fallback)

    # Header Text Block
    y_offset = 140
    header_lines = textwrap.wrap(header_text, width=26)
    for line in header_lines:
        draw.text((90, y_offset), line, fill=TEXT_TITLE if is_cover else ACCENT_GREEN, font=font_header)
        y_offset += 44

    y_offset += 25
    draw.line([90, y_offset, 990, y_offset], outline="#4c1d95", width=2)
    y_offset += 25

    # Flow-Optimized Body Items (Up to 3 coherent items per slide with clean wrapping)
    for item in body_items[:3]:
        wrapped_item = textwrap.wrap(item, width=44)
        if wrapped_item:
            draw.ellipse([90, y_offset + 5, 100, y_offset + 15], fill=ACCENT_GREEN)
            for line in wrapped_item:
                draw.text((120, y_offset), line, fill=TEXT_BODY, font=font_body)
                y_offset += 34
            y_offset += 16

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
        sentences = ["New investigation telemetry and updates live now at pabsmophobia.com"]
    else:
        title, sentences = parse_markdown(latest_file)

    # Split coherent sentences smoothly across Slide 1 and Slide 2
    midpoint = max(1, len(sentences) // 2)
    slide_1_sentences = sentences[:midpoint]
    slide_2_sentences = sentences[midpoint:] if len(sentences) > midpoint else ["Check out full breakdown on our site."]

    create_slide(title.upper(), slide_1_sentences, "images/tiktok/slide_1.png", is_cover=True)
    create_slide("KEY FINDINGS", slide_2_sentences, "images/tiktok/slide_2.png", is_cover=False)
    
    print("TikTok slides generated with smooth, non-choppy paragraph flow and active logo path!")
