import os
import json
import re
from PIL import Image, ExifTags

PHOTOS_DIR = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'
OUTPUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_timeline.json'

SECTIONS = {
    "1_Baby_Toddler": [],
    "2_Early_School": [],
    "3_High_School": [],
    "4_Military_College": [],
    "5_Brothers_And_Family": [],
    "6_Marriage_Linsey": [],
    "7_Recent_Mix": []
}

def get_exif_year(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        if not exif: return None
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return int(value.split(':')[0])
    except:
        pass
    return None

def get_filename_year(filepath):
    basename = os.path.basename(filepath)
    match = re.match(r'^(19[89]\d|20[0-2]\d)', basename)
    if match: return int(match.group(1))
    match = re.search(r'(?:^|[^0-9])(19[89]\d|20[0-2]\d)(?:[^0-9]|$)', basename)
    if match: return int(match.group(1))
    return None

def assign_photo(filepath, folder_name, faces_in_photo):
    year = get_filename_year(filepath) or get_exif_year(filepath)
    
    # 1. Rule-based by folder
    if "Military" in folder_name:
        return "4_Military_College"
        
    # 2. Rule-based by faces (if Linsey is in it, it's marriage or later)
    # We will assume face_labels are mapped in another file, but for now we just use folder names and dates
    
    # 3. Rule-based by Year (assuming birth ~1990 for estimation)
    if year:
        age = year - 1990
        if age <= 5: return "1_Baby_Toddler"
        if age <= 13: return "2_Early_School"
        if age <= 18: return "3_High_School"
        if age <= 23: return "4_Military_College"
        if age <= 28: return "5_Brothers_And_Family"
        if age <= 34: return "6_Marriage_Linsey"
        return "7_Recent_Mix"
        
    # 4. Fallback based on folders
    if "Family" in folder_name:
        return "5_Brothers_And_Family"
    if "Friends" in folder_name:
        return "3_High_School" # Guessing friends are high school
        
    return "7_Recent_Mix"

def main():
    for root, dirs, files in os.walk(PHOTOS_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(root, file)
                folder = os.path.basename(root)
                section = assign_photo(path, folder, [])
                SECTIONS[section].append({
                    "file": file,
                    "path": path,
                    "folder": folder
                })
                
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(SECTIONS, f, indent=2)
        
    print("Timeline breakdown generated!")
    for s, photos in SECTIONS.items():
        print(f"{s}: {len(photos)} photos")

if __name__ == '__main__':
    main()
