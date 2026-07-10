import json

path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline_v3.json"
with open(path, "r") as f:
    data = json.load(f)

seen_files = set()
unique_slides = []
duplicates_removed = 0

for slide in data.get("slides", []):
    if "isCard" in slide and slide["isCard"]:
        unique_slides.append(slide)
        continue
    if "isPlaceholder" in slide and slide["isPlaceholder"]:
        unique_slides.append(slide)
        continue
        
    filename = slide.get("file")
    if filename in seen_files:
        duplicates_removed += 1
        print(f"Removed duplicate: {filename}")
    else:
        seen_files.add(filename)
        unique_slides.append(slide)

data["slides"] = unique_slides
print(f"\nTotal duplicates removed: {duplicates_removed}")
print(f"New timeline length: {len(unique_slides)} slides")

with open(path, "w") as f:
    json.dump(data, f, indent=2)
