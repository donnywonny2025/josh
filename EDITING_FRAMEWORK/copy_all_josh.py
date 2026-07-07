import json
import shutil
import os
from pathlib import Path

db_path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/master_photo_db.json"
dest_dir = Path("/Volumes/Extreme SSD/JOSH/Best Picks")

dest_dir.mkdir(parents=True, exist_ok=True)

with open(db_path, 'r') as f:
    db = json.load(f)

candidates = []

positive_keywords = ["portrait", "close-up", "smiling", "looking at the camera", "solo", "posing", "handsome"]
negative_keywords = ["another", "group", "woman", "standing with", "next to", "crowd", "people", "holding a child", "baby", "children", "others", "couple", "family", "two individuals", "two people", "three", "four", "wife", "girlfriend", "together"]

for photo_path, data in db.items():
    desc = data.get("description", "").lower()
    
    # Exclude obvious non-solo photos
    has_negative = any(neg in desc for neg in negative_keywords)
    if has_negative:
        continue
        
    score = sum(3 for pos in positive_keywords if pos in desc)
    
    if "sunlight" in desc or "golden hour" in desc or "bright" in desc:
        score += 2
    if "happy" in desc or "laughing" in desc or "man" in desc:
        score += 2
        
    # We want solo shots of him
    if "man" in desc and "boy" not in desc:
        score += 1
        
    if score > 0:
        candidates.append((score, photo_path, desc))

candidates.sort(key=lambda x: x[0], reverse=True)

print(f"Found {len(candidates)} total solo candidates.")

# Copy ALL candidates (or top 100) to give him a big batch
batch = candidates[:100]

copied = 0
for score, photo_path, desc in batch:
    if not photo_path.startswith("/Volumes"):
        abs_path = os.path.join("/Volumes/Extreme SSD/JOSH/Photos", photo_path)
    else:
        abs_path = photo_path
        
    if os.path.exists(abs_path):
        filename = os.path.basename(abs_path)
        dest_path = dest_dir / filename
        
        # Add a prefix to ensure no filename collisions and sort by rank
        dest_path = dest_dir / f"Solo_{copied:03d}_{filename}"
        
        try:
            shutil.copy2(abs_path, dest_path)
            copied += 1
        except Exception as e:
            pass

print(f"Successfully copied {copied} solo photos to the folder.")
