import re
from pathlib import Path

# 1. Restore generate_proxies.py with a flawless edge-to-edge grid
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
    bg = Image.new('RGB', (W, H), (0, 0, 0))
    
    # We will make a 5x4 grid to ensure dense coverage and small squares
    cols, rows = 5, 4
    cell_w, cell_h = int(W / cols), int(H / rows)
    
    selected = slides.copy()
    random.shuffle(selected)
    
    idx = 0
    for y in range(rows):
        for x in range(cols):
            if idx >= len(selected):
                idx = 0 # loop
            
            slide = selected[idx]
            img_path = PHOTOS_DIR / slide["folder"] / slide["file"]
            if img_path.exists():
                try:
                    with Image.open(img_path) as img:
                        # crop to cell aspect ratio perfectly
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
                            
                        # Resize to exactly the cell dimensions
                        img = img.resize((cell_w, cell_h), Image.LANCZOS)
                        bg.paste(img, (x * cell_w, y * cell_h))
                except Exception as e:
                    pass
            idx += 1
            
    # Apply a heavy blur so it becomes a beautiful ambient wash, but still has photographic color variation
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    
    # Darken it slightly so foreground pops
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.4)
    
    out_path = PROXY_DIR / f"{seq_name}_bg.jpg"
    bg.save(out_path, quality=85)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence")
    args = parser.parse_args()
    generate_proxy(args.sequence)
"""
Path("generate_proxies.py").write_text(proxy_code)


# 2. Update advanced.html to use the single proxy again, but keep particles and cinematic easing
adv = Path("advanced.html")
html = adv.read_text()

# We need to replace the showSlide logic that injects DOM nodes
# with the single proxy loading logic.
js_old = """
  // Trigger Light Leak transition
  triggerLightLeak();

  // Dynamic Background Generation (True Parallax)
  const bgLayer = document.getElementById(`bg${nextDiv}`);
  bgLayer.innerHTML = ''; // Clear old
  
  const numBgPhotos = Math.min(16, seq.slides.length);
  // Pick random slides for background
  const bgSlides = [...seq.slides].sort(() => 0.5 - Math.random()).slice(0, numBgPhotos);
  
  const dynamicBgImgs = [];
  bgSlides.forEach(s => {
      const img = document.createElement('img');
      img.src = `/photos/${encodeURIComponent(s.folder)}/${encodeURIComponent(s.file)}`;
      
      // Randomize layout properties
      const widthPct = 20 + Math.random() * 25; 
      img.style.width = widthPct + '%';
      
      // Keep them roughly within bounds
      img.style.left = (5 + Math.random() * 70) + '%';
      img.style.top = (5 + Math.random() * 70) + '%';
      
      // Rotation
      const rot = -25 + Math.random() * 50;
      img.style.transform = `rotate(${rot}deg)`;
      
      // Store parallax depth multiplier
      img.dataset.parallaxSpeed = 0.5 + Math.random() * 1.5;
      img.dataset.rotStart = rot;
      
      bgLayer.appendChild(img);
      dynamicBgImgs.push(img);
  });
"""

js_new = """
  // Trigger Light Leak transition
  triggerLightLeak();

  // Load single seamless ambient proxy background
  const bgLayer = document.getElementById(`bg${nextDiv}`);
  bgLayer.innerHTML = ''; // Clear any dynamic nodes just in case
  const proxyUrl = `/proxies/${seq.id}_bg.jpg`;
  bgLayer.style.backgroundImage = `url('${proxyUrl}')`;
"""
html = html.replace(js_old.strip(), js_new.strip())


# Fix GSAP timeline to move the single bgLayer again
js_gsap_old = """
      // Background individual parallax
      dynamicBgImgs.forEach(img => {
          const speed = parseFloat(img.dataset.parallaxSpeed);
          const rotStart = parseFloat(img.dataset.rotStart);
          const dirX = Math.random() > 0.5 ? 1 : -1;
          const dirY = Math.random() > 0.5 ? 1 : -1;
          const rotDrift = Math.random() > 0.5 ? 2 : -2;
          
          currentGsapTl.fromTo(img, 
              { scale: 1.0, x: 0, y: 0, rotation: rotStart },
              { scale: 1.0 + (0.05 * speed), x: 30 * speed * dirX, y: 20 * speed * dirY, rotation: rotStart + rotDrift, duration: dur + transDur, ease: "sine.inOut" },
              0
          );
      });
"""

js_gsap_new = """
      // Background seamless ambient drift
      const dirX = Math.random() > 0.5 ? 1 : -1;
      const dirY = Math.random() > 0.5 ? 1 : -1;
      currentGsapTl.fromTo(bgLayer, 
          { scale: 1.0, x: 0, y: 0 },
          { scale: 1.15, x: 20 * dirX, y: 15 * dirY, duration: dur + transDur, ease: "sine.inOut" },
          0
      );
"""
html = html.replace(js_gsap_old.strip(), js_gsap_new.strip())

adv.write_text(html)
