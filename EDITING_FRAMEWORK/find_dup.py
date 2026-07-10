import json

path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline_v3.json"
with open(path, "r") as f:
    data = json.load(f)

current_sec = 0.0
for i, slide in enumerate(data.get("slides", [])):
    dur = slide.get("duration_frames", 150) / 30.0 if "duration_frames" in slide else slide.get("duration_sec", 5)
    
    if current_sec <= 633 < current_sec + dur:
        print(f"Slide {i} covers 10:33")
        break
    current_sec += dur

print("Surrounding slides:")
c_sec = 0.0
for i, slide in enumerate(data.get("slides", [])):
    dur = slide.get("duration_frames", 150) / 30.0 if "duration_frames" in slide else slide.get("duration_sec", 5)
    if abs(c_sec - 633) < 30:
        print(f"[{i}] ({int(c_sec//60)}:{int(c_sec%60):02d}) File: {slide.get('file', 'Card')}")
    c_sec += dur

