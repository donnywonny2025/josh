import re
from pathlib import Path

# 1. Update the proxy generator to make a SCATTERED collage with rotations
proxy_code = """#!/usr/bin/env python3
import json
import random
import argparse
from pathlib import Path
try:
    from PIL import Image, ImageFilter, ImageEnhance
except ImportError:
    exit(1)

PROJECT = Path("/Volumes/Extreme SSD/JOSH")
PHOTOS_DIR = PROJECT / "Photos" / "RAW_IMPORTS"
SEQ_DIR = PROJECT / "EDITING_FRAMEWORK" / "sequences"
PROXY_DIR = PROJECT / "EDITING_FRAMEWORK" / "proxies"
PROXY_DIR.mkdir(exist_ok=True)

def generate_proxy(seq_name):
    seq_file = SEQ_DIR / f"{seq_name}.json"
    if not seq_file.exists(): return
    data = json.loads(seq_file.read_text())
    slides = data.get("slides", [])
    if not slides: return
    
    W, H = 1920, 1080
    bg = Image.new('RGB', (W, H), (10, 10, 15))
    
    # We want ~15 photos scattered around
    num_photos = min(20, len(slides))
    selected = random.sample(slides, num_photos)
    
    for slide in selected:
        img_path = PHOTOS_DIR / slide["folder"] / slide["file"]
        if img_path.exists():
            try:
                with Image.open(img_path) as img:
                    # Randomize size to simulate depth
                    scale = random.uniform(0.3, 0.6)
                    new_w = int(img.width * scale)
                    new_h = int(img.height * scale)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    
                    # Add a slight white border to the background photos for contrast
                    # (very common in these AE templates, or just rounded corners)
                    
                    # Random rotation between -20 and +20 degrees
                    angle = random.uniform(-25, 25)
                    # Expand=True so the corners aren't cut off when rotated
                    img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(10,10,15))
                    
                    # Random position
                    x = random.randint(-new_w//2, W - new_w//2)
                    y = random.randint(-new_h//2, H - new_h//2)
                    
                    # Paste using the image itself as a mask to handle rotation transparency
                    # Since we filled with a specific color, we can just paste (simplest approach)
                    # Better: rotate with RGBA
                    with Image.open(img_path).convert("RGBA") as img_rgba:
                        img_rgba = img_rgba.resize((new_w, new_h), Image.LANCZOS)
                        img_rgba = img_rgba.rotate(angle, resample=Image.BICUBIC, expand=True)
                        bg.paste(img_rgba, (x, y), img_rgba)
                        
            except Exception as e:
                print(e)
            
    # Use a much lighter blur (like 5px) to match the reference
    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
    
    # Darken it slightly so the foreground pops
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.5)
    
    out_path = PROXY_DIR / f"{seq_name}_bg.jpg"
    # Convert back to RGB for JPEG save
    bg.convert("RGB").save(out_path, quality=85)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence")
    args = parser.parse_args()
    generate_proxy(args.sequence)
"""
Path("generate_proxies.py").write_text(proxy_code)

# 2. Update CSS in advanced.html to match the reference (rounded corners, no thick white border)
adv = Path("advanced.html")
html = adv.read_text()

# Remove the white border, add border-radius to match the AE template exactly
css_old = "border: 12px solid #fff;"
css_new = "border-radius: 20px; box-shadow: 0 40px 80px rgba(0,0,0,0.9);"
if css_old in html:
    html = html.replace(css_old, css_new)
else:
    # Fallback if it was changed
    html = re.sub(r"border:.*?;", css_new, html)
    
# Remove any extra box-shadow that might conflict
html = html.replace("box-shadow: 0 20px 60px rgba(0,0,0,0.8);", "")

# Ensure the size is closer to 70-80% to match the framing in the reference image
html = html.replace("max-width:85%; max-height:85%;", "max-width:75%; max-height:75%;")

# Ensure CSS blur on the bg-layer is removed entirely since the python script handles it
html = re.sub(r"filter: .*?;", "", html)

adv.write_text(html)
