import json

path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline_v3.json"
with open(path, "r") as f:
    data = json.load(f)

current_sec = 0.0
for i, slide in enumerate(data.get("slides", [])):
    dur = slide.get("duration_frames", 150) / 30.0 if "duration_frames" in slide else slide.get("duration_sec", 5)
    
    # Check if this slide covers 633 seconds (10:33)
    if current_sec <= 633 < current_sec + dur:
        print(f"Deleting slide {i}: {slide.get('file', 'Card')} which covers 10:33")
        del data["slides"][i]
        break
    current_sec += dur

with open(path, "w") as f:
    json.dump(data, f, indent=2)

