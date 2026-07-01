import json
from deepface import DeepFace
import os
import sys

# Suppress tf warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/face_data/face_clusters.json', 'r') as f:
    data = json.load(f)

# Find Don Kerr's crop
don_crop = None
for c in data['clusters']:
    if c['person_id'] == 80:
        don_crop = c['representative_crop']
        break

if not don_crop:
    print("Don Kerr cluster not found.")
    sys.exit(1)

don_img = f"/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/face_data/crops/{don_crop}"

results = []
for c in data['clusters']:
    if c['person_id'] == 80: continue
    
    other_img = f"/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/face_data/crops/{c['representative_crop']}"
    if not os.path.exists(other_img): continue
    
    try:
        # Use Facenet512 for good accuracy
        res = DeepFace.verify(don_img, other_img, model_name="Facenet512", enforce_detection=False, align=False)
        dist = res['distance']
        results.append((c['person_id'], c['photo_count'], c['label'], dist))
    except Exception as e:
        pass

# Sort by distance (lower is more similar)
results.sort(key=lambda x: x[3])

print("Most similar clusters to Don Kerr (Cluster 80):")
for r in results[:10]:
    print(f"Cluster {r[0]:<4} | Photos: {r[1]:<3} | Dist: {r[3]:.4f} | Label: {r[2]}")
