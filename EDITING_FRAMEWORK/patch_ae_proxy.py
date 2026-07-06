import re
from pathlib import Path

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
    # Start with a base dark color
    bg = Image.new('RGB', (W, H), (15, 15, 20))
    
    # We need to guarantee NO BLACK GAPS.
    # Step 1: Base layer grid (tightly packed to cover 100% of the canvas)
    cols, rows = 4, 3
    cell_w, cell_h = int(W / cols), int(H / rows)
    
    selected = slides.copy()
    random.shuffle(selected)
    
    idx = 0
    for y in range(rows):
        for x in range(cols):
            if idx >= len(selected): idx = 0
            img_path = PHOTOS_DIR / selected[idx]["folder"] / selected[idx]["file"]
            if img_path.exists():
                try:
                    with Image.open(img_path) as img:
                        img_ratio = img.width / img.height
                        target_ratio = cell_w / cell_h
                        if img_ratio > target_ratio:
                            new_w = int(img.height * target_ratio)
                            left = (img.width - new_w) // 2
                            img = img.crop((left, 0, left + new_w, img.height))
                        else:
                            new_h = int(img.width / target_ratio)
                            top = (img.height - new_h) // 2
                            img = img.crop((0, top, img.width, top + new_h))
                        img = img.resize((cell_w, cell_h), Image.LANCZOS)
                        bg.paste(img, (x * cell_w, y * cell_h))
                except Exception:
                    pass
            idx += 1

    # Step 2: Overlay the scattered, rotated photos to match the AE Template
    num_scatter = min(25, len(slides))
    scatter_slides = random.sample(slides, num_scatter)
    
    for slide in scatter_slides:
        img_path = PHOTOS_DIR / slide["folder"] / slide["file"]
        if img_path.exists():
            try:
                with Image.open(img_path).convert("RGBA") as img:
                    scale = random.uniform(0.4, 0.7)
                    new_w = int(img.width * scale)
                    new_h = int(img.height * scale)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    
                    angle = random.uniform(-30, 30)
                    img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
                    
                    # Random position, allowing them to bleed off the edges
                    x = random.randint(-int(new_w*0.5), W - int(new_w*0.5))
                    y = random.randint(-int(new_h*0.5), H - int(new_h*0.5))
                    
                    bg.paste(img, (x, y), img)
            except Exception:
                pass
                
    # Step 3: Apply the exact blur and darkening from the AE Template
    # We use a 6px blur so you can still distinctly see the photos
    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
    
    # Darken it so the foreground pops perfectly
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.55)
    
    out_path = PROXY_DIR / f"{seq_name}_bg.jpg"
    bg.save(out_path, quality=85)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence")
    args = parser.parse_args()
    generate_proxy(args.sequence)
"""
Path("generate_proxies.py").write_text(proxy_code)
