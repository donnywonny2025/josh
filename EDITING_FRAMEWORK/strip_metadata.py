import os
from PIL import Image
import numpy as np

EXPORT_DIR = '/Volumes/Extreme SSD/JOSH/exports'
IMG1 = os.path.join(EXPORT_DIR, 'hope_today_composite.jpg')
IMG2 = os.path.join(EXPORT_DIR, 'hope_today_clean.jpg')

def completely_strip_metadata(filepath):
    try:
        print(f"Stripping metadata from {filepath}...")
        
        # Open the image
        img = Image.open(filepath)
        
        # The most bulletproof way to destroy ALL embedded metadata (EXIF, IPTC, XMP, C2PA, AI watermarks):
        # Convert the image to a raw numpy pixel array. This strips everything except the actual colored pixels.
        raw_pixels = np.array(img)
        
        # Reconstruct a brand new, clean PIL image from those raw pixels
        clean_img = Image.fromarray(raw_pixels)
        
        # Save it back over the original file. 
        # By not passing the 'exif' or 'icc_profile' arguments, it saves as a completely virgin JPEG.
        clean_img.save(filepath, format='JPEG', quality=95)
        
        print("Success! Image is now 100% clean of all metadata.")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    completely_strip_metadata(IMG1)
    completely_strip_metadata(IMG2)
