import json
import shutil
import os
from pathlib import Path

db_path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/master_photo_db.json"
dest_dir = Path("/Volumes/Extreme SSD/JOSH/Best Picks")

# Clear out any bad picks first
if dest_dir.exists():
    shutil.rmtree(dest_dir)
dest_dir.mkdir(parents=True, exist_ok=True)

with open(db_path, 'r') as f:
    db = json.load(f)

candidates = []

positive_keywords = ["portrait", "close-up", "smiling", "looking at the camera", "solo", "posing", "handsome"]
negative_keywords = ["another", "group", "woman", "standing with", "next to", "crowd", "people", "holding a child", "baby", "children", "others", "couple", "family", "two individuals", "two people", "three", "four", "wife", "girlfriend"]

for photo_path, data in db.items():
    desc = data.get("description", "").lower()
    
    # Must explicitly rule out multiple people
    has_negative = any(neg in desc for neg in negative_keywords)
    if has_negative:
        continue
        
    score = sum(3 for pos in positive_keywords if pos in desc)
    
    if "sunlight" in desc or "golden hour" in desc or "bright" in desc:
        score += 2
    if "happy" in desc or "laughing" in desc or "man" in desc:
        score += 2
        
    # We really want a solo shot, preferably a young man / man
    if "man" in desc and "boy" not in desc:
        score += 1
        
    if score > 0:
        candidates.append((score, photo_path, desc))

# Sort by highest score first
candidates.sort(key=lambda x: x[0], reverse=True)

print(f"Found {len(candidates)} solo candidates.")

# Take the top 5
top_5 = candidates[:5]
for i, (score, photo_path, desc) in enumerate(top_5, 1):
    print(f"{i}. {photo_path} (Score: {score})")
    print(f"   Desc: {desc}")
    
    if not photo_path.startswith("/Volumes"):
        abs_path = os.path.join("/Volumes/Extreme SSD/JOSH/Photos", photo_path)
    else:
        abs_path = photo_path
        
    if os.path.exists(abs_path):
        filename = os.path.basename(abs_path)
        dest_path = dest_dir / filename
        shutil.copy2(abs_path, dest_path)
    else:
        print(f"   ERROR: Could not find {abs_path}")
