import json
from pathlib import Path

BASE_DIR = Path('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK')
DATA_DIR = BASE_DIR / 'face_data'
SEQ_FILE = BASE_DIR / 'sequences/ben-josh.json'

with open(DATA_DIR / 'face_labels.json', 'r') as f:
    labels = json.load(f)

with open(DATA_DIR / 'face_clusters.json', 'r') as f:
    clusters_data = json.load(f)

# Build a map of (folder, file) -> set of people
photo_people = {}

for cluster in clusters_data['clusters']:
    cid = str(cluster['person_id'])
    if cid in labels and labels[cid].strip():
        name = labels[cid].strip().lower()
        for photo in cluster['photos']:
            key = (photo['folder'], photo['file'])
            if key not in photo_people:
                photo_people[key] = set()
            photo_people[key].add(name)

with open(SEQ_FILE, 'r') as f:
    seq_data = json.load(f)

valid_slides = []
removed_slides = []

for slide in seq_data['slides']:
    key = (slide['folder'], slide['file'])
    people = photo_people.get(key, set())
    
    has_ben = False
    has_josh = False
    
    for p in people:
        if 'ben' in p:
            has_ben = True
        if 'josh' in p:
            has_josh = True
            
    print(f"Slide: {slide['folder']}/{slide['file']} -> Faces: {people}, has_ben: {has_ben}, has_josh: {has_josh}")
            
    # We enforce that the photo has to have BOTH Ben and Josh.
    # Exception: if the folder is literally "Ben and Josh", we assume it's manually curated to have both.
    if (has_ben and has_josh):
        valid_slides.append(slide)
    else:
        removed_slides.append((slide, list(people)))

print(f"Total original slides: {len(seq_data['slides'])}")
print(f"Valid slides kept: {len(valid_slides)}")
print(f"Removed slides: {len(removed_slides)}")
for r, p in removed_slides:
    print(f"  - {r['folder']}/{r['file']} (Faces: {p})")

seq_data['slides'] = valid_slides

with open(SEQ_FILE, 'w') as f:
    json.dump(seq_data, f, indent=2)

print("\nSaved updated sequence back to ben-josh.json.")
