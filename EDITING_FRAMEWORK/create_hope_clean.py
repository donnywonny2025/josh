import os
import random
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFilter

EXPORT_DIR = '/Volumes/Extreme SSD/JOSH/exports'
IMPEACH_IMG = os.path.join(EXPORT_DIR, 'impeach_sign_ai_edited.png')
SKYSCRAPER_IMG = os.path.join(EXPORT_DIR, 'power_of_love_banner.jpg')
OUTPUT_CLEAN_IMG = os.path.join(EXPORT_DIR, 'hope_today_clean.jpg')
OUTPUT_IMG = os.path.join(EXPORT_DIR, 'hope_today_composite.jpg')

def add_noise(image, noise_factor=0.08):
    img_array = np.array(image, dtype=np.float32)
    noise = np.random.normal(0, 255 * noise_factor, img_array.shape)
    noisy_img = img_array + noise
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)

def add_scratches(image, num_scratches=10):
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    for _ in range(num_scratches):
        x = random.randint(0, width)
        y_start = random.randint(0, height // 2)
        y_end = y_start + random.randint(50, height)
        thickness = random.randint(1, 2)
        opacity = random.randint(80, 180)
        draw.line([(x, y_start), (x, y_end)], fill=(255, 255, 255, opacity), width=thickness)
    return image

def main():
    try:
        img_impeach = Image.open(IMPEACH_IMG).convert('RGB')
        img_sky = Image.open(SKYSCRAPER_IMG).convert('RGB')
        
        print(f"Original Impeach Size: {img_impeach.size}")
        print(f"Original Skyscraper Size: {img_sky.size}")
        
        img_impeach = ImageOps.grayscale(img_impeach).convert('RGB') 
        img_impeach = ImageEnhance.Contrast(img_impeach).enhance(1.4)
        img_impeach = ImageEnhance.Brightness(img_impeach).enhance(1.1)
        img_impeach = add_noise(img_impeach, noise_factor=0.15)
        img_impeach = add_scratches(img_impeach, num_scratches=8)
        
        target_height = 800
        
        w_percent_sky = (target_height / float(img_sky.size[1]))
        w_size_sky = int((float(img_sky.size[0]) * float(w_percent_sky)))
        img_sky = img_sky.resize((w_size_sky, target_height), Image.Resampling.LANCZOS)
        
        w_percent_imp = (target_height / float(img_impeach.size[1]))
        w_size_imp = int((float(img_impeach.size[0]) * float(w_percent_imp)))
        img_impeach = img_impeach.resize((w_size_imp, target_height), Image.Resampling.LANCZOS)
        
        total_width = img_sky.size[0] + img_impeach.size[0]
        total_height = target_height 
        
        # Clean Canvas without the text bar
        clean_canvas = Image.new('RGB', (total_width, total_height), (0, 0, 0))
        clean_canvas.paste(img_sky, (0, 0))
        clean_canvas.paste(img_impeach, (img_sky.size[0], 0))
        
        clean_canvas.save(OUTPUT_CLEAN_IMG, quality=95)
        print(f"Clean version size (WxH): {total_width}x{total_height} pixels")
        print(f"Successfully generated clean composite at {OUTPUT_CLEAN_IMG}")
        
    except Exception as e:
        print(f"Error generating composite: {e}")

if __name__ == '__main__':
    main()
