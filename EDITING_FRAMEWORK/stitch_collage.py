import json
import os
from PIL import Image, ImageDraw, ImageFont
import math

# Configuration
SEQUENCE_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/ben-josh.json'
PHOTOS_DIR = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'
OUTPUT_COLLAGE = '/Users/jeffkerr/.gemini/antigravity-ide/brain/f002bd20-4353-47ed-8512-054f143098f8/age_collage.jpg'

def main():
    print("Loading sequence...")
    with open(SEQUENCE_FILE, 'r') as f:
        seq = json.load(f)
        
    slides = seq.get('slides', [])
    total = len(slides)
    print(f"Found {total} photos.")
    
    if total == 0:
        return

    # Collage settings
    cols = 8
    rows = math.ceil(total / cols)
    thumb_size = 400
    padding = 20
    
    width = cols * thumb_size + (cols + 1) * padding
    height = rows * thumb_size + (rows + 1) * padding
    
    collage = Image.new('RGB', (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(collage)
    
    # Try to load a font, otherwise use default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()
        
    for i, slide in enumerate(slides):
        r = i // cols
        c = i % cols
        
        x = padding + c * (thumb_size + padding)
        y = padding + r * (thumb_size + padding)
        
        # Find the image
        img_path = None
        for root, dirs, files in os.walk(PHOTOS_DIR):
            if slide['file'] in files:
                img_path = os.path.join(root, slide['file'])
                break
                
        if img_path:
            try:
                img = Image.open(img_path)
                img.thumbnail((thumb_size, thumb_size))
                
                # Center it in the thumbnail box
                offset_x = x + (thumb_size - img.width) // 2
                offset_y = y + (thumb_size - img.height) // 2
                collage.paste(img, (offset_x, offset_y))
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                
        # Draw the index number in bright yellow with black stroke
        idx_text = str(i)
        
        # Draw stroke
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            draw.text((x + 10 + dx, y + 10 + dy), idx_text, fill="black", font=font)
        # Draw text
        draw.text((x + 10, y + 10), idx_text, fill="yellow", font=font)
        
    print(f"Saving collage to {OUTPUT_COLLAGE}...")
    collage.save(OUTPUT_COLLAGE, quality=85)
    print("Done!")

if __name__ == '__main__':
    main()
