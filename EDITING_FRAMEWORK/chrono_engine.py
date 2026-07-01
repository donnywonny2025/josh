import os
import json
import re
from PIL import Image, ExifTags

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

JOSH_BIRTH_YEAR = 1982

# Configuration
PHOTOS_DIR = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'
FACE_DATA_DIR = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/face_data'
OUTPUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_timeline.json'

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

def assign_bucket(folder):
    if folder == "Ben and Josh":
        return "Ben_and_Josh"
    elif folder == "Josh - Military":
        return "Military"
    elif folder == "save a place for me":
        return "Passed_Loved_Ones"
    elif folder in ["Josh’s places and travel", "Josh and Friends"]:
        return "Travel_Fun"
    else:
        # Fallback to General for all other folders
        return "General"

def main():
    print("Loading face clusters...")
    with open(os.path.join(FACE_DATA_DIR, 'face_clusters.json'), 'r') as f:
        cluster_data = json.load(f)
        
    # Map photos to their crop if they are in cluster 1 (Josh)
    josh_crops = {}
    for c in cluster_data['clusters']:
        if c['person_id'] == 1:
            for p in c.get('photos', []):
                # We can't map perfectly from photo to crop in this structure, 
                # so we will run DeepFace on the original photo directly if needed.
                pass
                
    SECTIONS = {
        "Ben_and_Josh": [],
        "Military": [],
        "Passed_Loved_Ones": [],
        "Travel_Fun": [],
        "General": []
    }    
    total = 0
    estimated = 0
    
    for root, dirs, files in os.walk(PHOTOS_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                total += 1
                path = os.path.join(root, file)
                folder = os.path.basename(root)
                
                year = get_filename_year(path) or get_exif_year(path)
                age = None
                
                if not year:
                    # DeepFace has been removed. We rely on filename, EXIF year, or bucket fallback.
                    pass
                
                section = assign_bucket(folder)
                
                # Calculate absolute age for sorting
                absolute_age = 999  # Default high value if unknown
                if year:
                    absolute_age = year - JOSH_BIRTH_YEAR
                elif age:
                    absolute_age = age

                SECTIONS[section].append({
                    "file": file,
                    "path": path,
                    "folder": folder,
                    "year": year,
                    "estimated_age": age,
                    "absolute_age": absolute_age
                })
                
    # Sort each section chronologically by absolute_age
    for section in SECTIONS:
        SECTIONS[section] = sorted(SECTIONS[section], key=lambda x: x["absolute_age"])
                
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(SECTIONS, f, indent=2)
        
    print(f"\nTimeline successfully rebuilt using JOSH_BIRTH_YEAR=1982")
    print(f"DeepFace estimated age for {estimated} orphaned photos.")
    for s, photos in SECTIONS.items():
        print(f"{s}: {len(photos)} photos")

if __name__ == '__main__':
    main()
