from PIL import Image
import os

IMG_PATH = '/Users/jeffkerr/.gemini/antigravity-ide/brain/f002bd20-4353-47ed-8512-054f143098f8/media__1782952894212.png'
EXPORT_DIR = '/Volumes/Extreme SSD/JOSH/exports'
EXPORT_PATH = os.path.join(EXPORT_DIR, 'impeach_sign_edited.png')

def main():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        
    try:
        img = Image.open(IMG_PATH)
        width, height = img.size
        print(f"Original size: {width}x{height}")
        
        # The watermark is a dark bar at the bottom.
        # Let's crop the bottom 30% of the image to cleanly remove it.
        # But we'll try to keep as much of the sign as possible.
        crop_height = int(height * 0.70)
        
        cropped_img = img.crop((0, 0, width, crop_height))
        cropped_img.save(EXPORT_PATH)
        print(f"Successfully saved cropped image to {EXPORT_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
