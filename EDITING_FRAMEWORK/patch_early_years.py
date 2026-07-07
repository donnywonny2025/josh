import json
import os
import shutil

ROOT = "/Volumes/Extreme SSD/JOSH"
TIMELINE_FILE = os.path.join(ROOT, "EDITING_FRAMEWORK", "sequences", "master_timeline.json")
BACKUP_FILE = os.path.join(ROOT, "EDITING_FRAMEWORK", "sequences", "master_timeline_before_early.json")
DB_FILE = os.path.join(ROOT, "EDITING_FRAMEWORK", "master_photo_db.json")
BEAT_FILE = os.path.join(ROOT, "EDITING_FRAMEWORK", "true_beats.json")

shutil.copy2(BACKUP_FILE, TIMELINE_FILE)

# 1. Recreate the "Organic" Pool the user liked
with open(DB_FILE, "r") as f:
    db = json.load(f)

early_folders = ["Baby & toddler Josh", "Josh school years", "Josh - Family", "Just Josh"]
folder_order = {f: i for i, f in enumerate(early_folders)}

organic_pool = []
for p, meta in db.items():
    folder = os.path.basename(os.path.dirname(p))
    if folder in early_folders:
        age = meta.get("estimated_age", 0)
        if age == 0:
            # If the AI failed to detect an age, use a fallback based on the folder 
            # so adult photos don't get sorted into the baby section
            if folder == "Josh school years": age = 10
            elif folder == "Josh - Family": age = 99
            elif folder == "Just Josh": age = 99
            
        organic_pool.append({
            "path": p, 
            "folder": folder, 
            "file": os.path.basename(p), 
            "folder_idx": folder_order[folder],
            "age": age
        })

# Original flawed sort that the user actually liked
organic_pool.sort(key=lambda x: x["age"])

# 2. Get beats
with open(BEAT_FILE, "r") as f:
    beats_data = json.load(f)
beats = beats_data["beats"]

# 3. Load timeline
with open(TIMELINE_FILE, "r") as f:
    timeline = json.load(f)

intro_slides = []
middle_slides = []
sum_early = 0
found_military = False
seen_files = set()

for s in timeline["slides"]:
    if s.get("sectionName") == "Military Picts":
        found_military = True
    if not found_military:
        sum_early += s.get("duration_frames", 150)
        if s.get("sectionName") == "Intro":
            intro_slides.append(s)
            if "file" in s: seen_files.add(s["file"])
    else:
        middle_slides.append(s)
        if "file" in s: seen_files.add(s["file"])

# Align the intro card perfectly to the user's exact waveform transient: 5 seconds and 4 frames (154 frames at 30fps)
intro_slides[0]["duration_frames"] = 154

TARGET_FRAMES = 5037
INTRO_FRAMES = sum([s.get("duration_frames", 150) for s in intro_slides])
FRAMES_TO_FILL = TARGET_FRAMES - INTRO_FRAMES
intro_duration_sec = INTRO_FRAMES / 30.0

current_time = intro_duration_sec
target_end_time = TARGET_FRAMES / 30.0

seen_files.add("IMG_1357.jpeg")

new_slides = []
photo_idx = 0

while current_time < target_end_time and photo_idx < len(organic_pool):
    # Find a unique photo
    while photo_idx < len(organic_pool):
        p = organic_pool[photo_idx]
        if p["file"] not in seen_files:
            break
        photo_idx += 1
        
    if photo_idx >= len(organic_pool):
        break
        
    p = organic_pool[photo_idx]
    seen_files.add(p["file"])
    
    # STRICT 100 BPM MATH: 100 beats per minute = 1.666 beats per second.
    # 4 beats = 2.4 seconds. At 30 FPS, 2.4 seconds is exactly 72 frames.
    dur_frames = 72
    
    # Check if this photo would overshoot the military section
    if current_time + (dur_frames / 30.0) > target_end_time:
        dur_frames = round((target_end_time - current_time) * 30.0)
    
    if dur_frames < 5: 
        break
        
    sec_name = "Early Pictures" if p["folder_idx"] < 2 else "Family, High School"
    
    slide = {
        "folder": p["folder"],
        "file": p["file"],
        "sectionName": sec_name,
        "duration_frames": dur_frames
    }
    new_slides.append(slide)
    
    current_time += (dur_frames / 30.0)
    photo_idx += 1

celebrate_idx = -1
for i, s in enumerate(middle_slides):
    if s.get("sectionName") == "Celebrate Life":
        celebrate_idx = i
        break

if celebrate_idx != -1:
    middle_slides.insert(celebrate_idx, {
        "folder": "Josh - Family",
        "file": "IMG_1357.jpeg",
        "sectionName": "Celebrate Life",
        "duration_frames": 56
    })
    middle_slides.insert(celebrate_idx, {
        "folder": "Josh - Family",
        "file": "IMG_5301.JPG",
        "sectionName": "Celebrate Life",
        "duration_frames": 56
    })

timeline["slides"] = intro_slides + new_slides + middle_slides

with open(TIMELINE_FILE, "w") as f:
    json.dump(timeline, f, indent=4)
print(f"Restored {len(new_slides)} curated photos, deduplicated, and chronologically sorted!")
