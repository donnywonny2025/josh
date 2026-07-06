import re
from pathlib import Path

# 1. Update the proxy generator to make a structured grid with less blur
proxy_code = """#!/usr/bin/env python3
import json
import random
import argparse
from pathlib import Path
try:
    from PIL import Image, ImageFilter
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
    
    cols, rows = 4, 3
    thumb_w, thumb_h = int(W / cols), int(H / rows)
    
    selected = slides.copy()
    random.shuffle(selected)
    
    idx = 0
    for y in range(rows):
        for x in range(cols):
            if idx >= len(selected):
                idx = 0 # loop if we run out
            img_path = PHOTOS_DIR / selected[idx]["folder"] / selected[idx]["file"]
            if img_path.exists():
                try:
                    with Image.open(img_path) as img:
                        # crop to aspect ratio then resize
                        img_ratio = img.width / img.height
                        target_ratio = thumb_w / thumb_h
                        if img_ratio > target_ratio:
                            new_w = int(img.height * target_ratio)
                            left = (img.width - new_w) // 2
                            img = img.crop((left, 0, left + new_w, img.height))
                        else:
                            new_h = int(img.width / target_ratio)
                            top = (img.height - new_h) // 2
                            img = img.crop((0, top, img.width, top + new_h))
                            
                        img = img.resize((thumb_w, thumb_h), Image.LANCZOS)
                        bg.paste(img, (x * thumb_w, y * thumb_h))
                except Exception:
                    pass
            idx += 1
            
    # Use a much lighter blur so you can still tell they are distinct photos
    bg = bg.filter(ImageFilter.GaussianBlur(radius=15))
    out_path = PROXY_DIR / f"{seq_name}_bg.jpg"
    bg.save(out_path, quality=80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence")
    args = parser.parse_args()
    generate_proxy(args.sequence)
"""
Path("generate_proxies.py").write_text(proxy_code)

# 2. Update CSS in advanced.html to give the foreground photo a white polaroid border
adv = Path("advanced.html")
html = adv.read_text()

css_old = ".slide .fg-layer img { width:100%; height:100%; object-fit:contain; object-position:center; filter: drop-shadow(0 0 60px rgba(0,0,0,0.9)); }"
css_new = ".slide .fg-layer img { width:auto; height:auto; max-width:85%; max-height:85%; object-fit:contain; border: 12px solid #fff; box-shadow: 0 20px 60px rgba(0,0,0,0.8); }"
html = html.replace(css_old, css_new)

# Also ensure the background blur in CSS isn't overriding the proxy blur
html = html.replace("filter: blur(10px) brightness(0.6);", "filter: brightness(0.5);")

adv.write_text(html)
