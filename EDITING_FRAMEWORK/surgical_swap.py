import json
import os

with open("EDITING_FRAMEWORK/sequences/master_timeline.json") as f:
    data = json.load(f)

# The photo to replace
bad_folder = "Josh with Kerrs"
bad_file = "Photo Sep 15 2017, 8 58 00 PM.jpg"

# Let's find an unused photo from valid_ben_josh_photos
# First, get all currently used photos
used_files = {s["file"] for s in data["slides"] if "file" in s}

# Let's run a quick query to find a valid photo that is NOT used
import sys
sys.path.append(os.path.abspath("EDITING_FRAMEWORK"))
# We can just parse face_clusters again
with open("EDITING_FRAMEWORK/face_data/face_clusters.json") as f:
    clusters = json.load(f)["clusters"]
with open("EDITING_FRAMEWORK/face_data/face_labels.json") as f:
    labels = json.load(f)

ben_ids = {cid for cid, name in labels.items() if "ben" in name.lower() and "josh" not in name.lower()}
josh_ids = {cid for cid, name in labels.items() if "josh" in name.lower() and "ben" not in name.lower() and "linsey" not in name.lower() and "natalie" not in name.lower() and "lisa" not in name.lower() and "dad" not in name.lower() and "grandparents" not in name.lower() and "buddies" not in name.lower() and "dance" not in name.lower()}

photo_to_ids = {}
for c in clusters:
    cid = str(c["person_id"])
    for p in c["photos"]:
        key = (p["folder"], p["file"])
        if key not in photo_to_ids: photo_to_ids[key] = set()
        photo_to_ids[key].add(cid)

valid_options = []
for (folder, file), cids in photo_to_ids.items():
    if any(cid in ben_ids for cid in cids) and any(cid in josh_ids for cid in cids):
        if file not in used_files and file != "img_2502_Original.jpg":
            valid_options.append((folder, file))

if not valid_options:
    print("No unused photos available to swap!")
    sys.exit(1)

new_folder, new_file = valid_options[0]

# Now perform the swap
swapped = False
for s in data["slides"]:
    if s.get("sectionName") == "Ben and Josh" and s.get("file") == bad_file and s.get("folder") == bad_folder:
        s["folder"] = new_folder
        s["file"] = new_file
        swapped = True
        print(f"Swapped {bad_file} -> {new_file}")
        
        # We should NOT erase pan/tilt/zoom because the user explicitly said not to ruin alignment!
        # But we do need to reset focus if it's a completely different photo
        # Actually, let's leave focus as is, the user can tweak it.
        break

if swapped:
    # Let's also add the bad photo to Celebrate Life
    bad_photo_slide = {
        "folder": bad_folder,
        "file": bad_file,
        "sectionName": "CELEBRATE LIFE",
        "duration_frames": 150,
        "duration_sec": 5.0
    }
    # Find where CELEBRATE LIFE starts or just append it at the very end of CELEBRATE LIFE
    # Let's just find the last slide of CELEBRATE LIFE and insert it after
    last_idx = -1
    for i, s in enumerate(data["slides"]):
        if s.get("sectionName") == "CELEBRATE LIFE":
            last_idx = i
            
    if last_idx != -1:
        data["slides"].insert(last_idx + 1, bad_photo_slide)
        print("Appended bad photo to CELEBRATE LIFE")
        
    with open("EDITING_FRAMEWORK/sequences/master_timeline.json", "w") as f:
        json.dump(data, f, indent=2)

