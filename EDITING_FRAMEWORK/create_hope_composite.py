import os
import random
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont, ImageFilter

EXPORT_DIR = '/Volumes/Extreme SSD/JOSH/exports'
IMPEACH_IMG = os.path.join(EXPORT_DIR, 'impeach_sign_ai_edited.png')
SKYSCRAPER_IMG = os.path.join(EXPORT_DIR, 'power_of_love_banner.jpg')
OUTPUT_IMG = os.path.join(EXPORT_DIR, 'hope_today_composite.jpg')

def add_noise(image, noise_factor=0.08):
    # Convert image to numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Generate Gaussian noise
    noise = np.random.normal(0, 255 * noise_factor, img_array.shape)
    
    # Add noise to image
    noisy_img = img_array + noise
    
    # Clip values to be between 0 and 255
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    
    return Image.fromarray(noisy_img)

def add_scratches(image, num_scratches=10):
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    
    for _ in range(num_scratches):
        x = random.randint(0, width)
        y_start = random.randint(0, height // 2)
        y_end = y_start + random.randint(50, height)
        
        # Random thickness and opacity
        thickness = random.randint(1, 2)
        opacity = random.randint(80, 180)
        
        # Draw a slightly wavy or straight line
        draw.line([(x, y_start), (x, y_end)], fill=(255, 255, 255, opacity), width=thickness)
        
    return image

def main():
    try:
        # 1. Load the images
        img_impeach = Image.open(IMPEACH_IMG).convert('RGB')
        img_sky = Image.open(SKYSCRAPER_IMG).convert('RGB')
        
        # 2. Make the impeach image black and white/vintage to match
        # Convert to grayscale
        img_impeach = ImageOps.grayscale(img_impeach)
        img_impeach = img_impeach.convert('RGB') 
        
        # Adjust contrast to match
        enhancer = ImageEnhance.Contrast(img_impeach)
        img_impeach = enhancer.enhance(1.4)
        
        # Adjust brightness slightly up so it's not too dark
        bright_enhancer = ImageEnhance.Brightness(img_impeach)
        img_impeach = bright_enhancer.enhance(1.1)
        
        # Add film grain
        img_impeach = add_noise(img_impeach, noise_factor=0.15)
        
        # Add some vertical scratches to match the left photo
        img_impeach = add_scratches(img_impeach, num_scratches=8)
        
        # 3. Resize to match heights
        target_height = 800
        
        # Resize Skyscraper
        w_percent = (target_height / float(img_sky.size[1]))
        w_size = int((float(img_sky.size[0]) * float(w_percent)))
        img_sky = img_sky.resize((w_size, target_height), Image.Resampling.LANCZOS)
        
        # Resize Impeach
        w_percent = (target_height / float(img_impeach.size[1]))
        w_size = int((float(img_impeach.size[0]) * float(w_percent)))
        img_impeach = img_impeach.resize((w_size, target_height), Image.Resampling.LANCZOS)
        
        # 4. Create the composite canvas
        total_width = img_sky.size[0] + img_impeach.size[0]
        text_bar_height = 120
        total_height = target_height + text_bar_height
        
        canvas = Image.new('RGB', (total_width, total_height), (0, 0, 0))
        
        # 5. Paste the images side by side
        canvas.paste(img_sky, (0, 0))
        canvas.paste(img_impeach, (img_sky.size[0], 0))
        
        # 6. Add the text 
        draw = ImageDraw.Draw(canvas)
        
        # Try to use a bolder, more professional font (Impact or Arial Black)
        fonts_to_try = [
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/Library/Fonts/Impact.ttf",
            "/Library/Fonts/Arial Black.ttf"
        ]
        
        font = None
        for fpath in fonts_to_try:
            try:
                font = ImageFont.truetype(fpath, 75)
                break
            except IOError:
                continue
                
        if font is None:
            font = ImageFont.load_default()
        
        text = "THERE WAS HOPE TODAY"
        
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
            
        text_x = (total_width - text_width) // 2
        text_y = target_height + ((text_bar_height - text_height) // 2) - 15
        
        draw.text((text_x, text_y), text, fill="white", font=font)
        
        # 7. Save the final image
        canvas.save(OUTPUT_IMG, quality=95)
        print(f"Successfully generated composite at {OUTPUT_IMG}")
        
    except Exception as e:
        print(f"Error generating composite: {e}")

if __name__ == '__main__':
    main()
