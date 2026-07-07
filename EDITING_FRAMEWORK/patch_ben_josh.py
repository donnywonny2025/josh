import json
import os
from datetime import datetime
from PIL import Image, ExifTags

BASE_DIR = "/Volumes/Extreme SSD/JOSH"
DATA_DIR = f"{BASE_DIR}/EDITING_FRAMEWORK/face_data"
SEQ_FILE = f"{BASE_DIR}/EDITING_FRAMEWORK/sequences/master_timeline.json"

# Load facial recognition data
with open(f"{DATA_DIR}/face_labels.json", 'r') as f:
    labels = json.load(f)

with open(f"{DATA_DIR}/face_clusters.json", 'r') as f:
    clusters_data = json.load(f)

# Collect all IDs that are strictly Ben and strictly Josh
ben_ids = set()
josh_ids = set()

for cid, name in labels.items():
    name = name.lower()
    # Ensure it only refers to Ben
    if "ben" in name and "josh" not in name:
        ben_ids.add(cid)
    # Ensure it only refers to Josh
    if "josh" in name and "ben" not in name and "linsey" not in name and "natalie" not in name and "lisa" not in name and "dad" not in name and "grandparents" not in name and "buddies" not in name and "dance" not in name:
        josh_ids.add(cid)

# Map (folder, file) -> set of cluster IDs
photo_to_ids = {}
for cluster in clusters_data['clusters']:
    cid = str(cluster['person_id'])
    for photo in cluster['photos']:
        key = (photo['folder'], photo['file'])
        if key not in photo_to_ids:
            photo_to_ids[key] = set()
        photo_to_ids[key].add(cid)

# Find all photos that contain BOTH Ben and Josh strictly
valid_ben_josh_photos = []

# To ensure we don't grab garbage, we require at least one strict Ben ID and one strict Josh ID
for key, cids in photo_to_ids.items():
    has_ben = any(cid in ben_ids for cid in cids)
    has_josh = any(cid in josh_ids for cid in cids)
    
    # Ban specific photos the user disliked
    if key[1] == "img_2502_Original.jpg":
        continue
        
    if has_ben and has_josh:
        # Default fallback timestamp
        folder, file = key
        full_path = os.path.join(BASE_DIR, "Photos", "RAW_IMPORTS", folder, file)
        
        # 1. Check for folder overrides
        folder_lower = folder.lower()
        forced_year = None
        if "baby & toddler" in folder_lower:
            forced_year = 1985
        elif "early pictures" in folder_lower:
            forced_year = 1990
        elif "school years" in folder_lower:
            forced_year = 1995
            
        # 2. Extract year from filename if present (e.g. 1994_... or 2004_...)
        import re
        match = re.search(r'^(19\d{2}|20[0-2]\d)', file)
        if match and not forced_year:
            forced_year = int(match.group(1))
            
        is_scan = False
        exif_year = None
        exif_ts = None
        
        try:
            img = Image.open(full_path)
            exif = img._getexif()
            if exif:
                for k, v in exif.items():
                    if ExifTags.TAGS.get(k) == "DateTimeOriginal":
                        try:
                            dt = datetime.strptime(v, '%Y:%m:%d %H:%M:%S')
                            exif_ts = dt.timestamp()
                            exif_year = dt.year
                        except: pass
                        break
        except: pass
        
        # 3. Detect Scans
        if exif_year in [2017, 2018, 2026] or "IMG_2017" in file or "20180203" in file:
            is_scan = True
            
        # Calculate final sorting timestamp
        if forced_year:
            # Randomize slightly within the year so multiple photos don't stack perfectly
            final_ts = datetime(forced_year, 1, 1).timestamp() + hash(file) % 31536000
        elif is_scan:
            # If it's a scan without a forced year, throw it to ~1999 (before the 2007 digital era)
            final_ts = datetime(1999, 1, 1).timestamp() + hash(file) % 31536000
        elif exif_ts:
            # True digital era photo
            final_ts = exif_ts
        else:
            # Fallback to mtime, but artificially push it old if it lacks EXIF
            final_ts = datetime(2000, 1, 1).timestamp() + hash(file) % 31536000
            
        valid_ben_josh_photos.append({
            'folder': folder,
            'file': file,
            'timestamp': final_ts
        })

# Sort chronologically
valid_ben_josh_photos.sort(key=lambda x: x['timestamp'])

print(f"Found {len(valid_ben_josh_photos)} valid Ben & Josh photos across the entire project.")

# Sample exactly 45 photos evenly across the chronological timeline
if len(valid_ben_josh_photos) > 45:
    sampled_photos = []
    step = len(valid_ben_josh_photos) / 45
    for i in range(45):
        idx = int(i * step)
        sampled_photos.append(valid_ben_josh_photos[idx])
    # Guarantee the absolute most modern photo is the final photo
    sampled_photos[-1] = valid_ben_josh_photos[-1]
else:
    sampled_photos = valid_ben_josh_photos

print(f"Sampled {len(sampled_photos)} photos for the timeline.")

# Load the master timeline
with open(SEQ_FILE, 'r') as f:
    master_timeline = json.load(f)

# Find the Ben and Josh section boundaries
new_slides = []
ben_josh_index_start = -1
for i, slide in enumerate(master_timeline['slides']):
    if slide.get('sectionName') == 'Ben and Josh':
        if ben_josh_index_start == -1:
            ben_josh_index_start = i
            
        # We drop the old slide (we'll replace them all)
    else:
        new_slides.append(slide)

if ben_josh_index_start == -1:
    print("Could not find 'Ben and Josh' section in the timeline.")
    exit(1)

# Generate the new slide objects
duration_frames = int(2232 / len(sampled_photos))
remainder_frames = 2232 % len(sampled_photos)

injected_slides = []
for i, photo in enumerate(sampled_photos):
    # Give the first 'remainder' slides an extra frame to balance the math exactly
    dur = duration_frames + (1 if i < remainder_frames else 0)
    injected_slides.append({
        "folder": photo['folder'],
        "file": photo['file'],
        "duration_sec": dur / 24.0,
        "transition": "crossfade",
        "sectionName": "Ben and Josh",
        "duration_frames": dur,
        "isPlaceholder": False,
        "focus": [50.0, 50.0]  # Default center focus, can be refined by user
    })

# Re-insert the injected slides at the exact same point in the timeline
final_slides = new_slides[:ben_josh_index_start] + injected_slides + new_slides[ben_josh_index_start:]

master_timeline['slides'] = final_slides

with open(SEQ_FILE, 'w') as f:
    json.dump(master_timeline, f, indent=2)
    
print("Successfully patched master_timeline.json!")
