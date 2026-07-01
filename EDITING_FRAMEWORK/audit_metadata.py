import os
from PIL import Image, ExifTags
import re

PHOTOS_DIR = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'

total = 0
has_exif = 0
has_filename_date = 0
missing_both = 0

for root, dirs, files in os.walk(PHOTOS_DIR):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            total += 1
            path = os.path.join(root, file)
            
            # Check filename
            filename_has_date = False
            match = re.match(r'^(19[89]\d|20[0-2]\d)', file)
            if not match:
                match = re.search(r'(?:^|[^0-9])(19[89]\d|20[0-2]\d)(?:[^0-9]|$)', file)
            if match:
                filename_has_date = True
                has_filename_date += 1
                
            # Check EXIF
            exif_has_date = False
            try:
                img = Image.open(path)
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            exif_has_date = True
                            has_exif += 1
                            break
            except:
                pass
                
            if not filename_has_date and not exif_has_date:
                missing_both += 1

print(f"Total Photos: {total}")
print(f"Photos with valid EXIF Dates: {has_exif}")
print(f"Photos with Filename Dates: {has_filename_date}")
print(f"Photos missing BOTH (Requires AI Age Estimation or Manual rules): {missing_both}")
