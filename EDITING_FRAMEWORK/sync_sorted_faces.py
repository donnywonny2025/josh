import os
import json
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path('/Volumes/Extreme SSD/JOSH')
RAW_DIR = BASE_DIR / 'Photos' / 'RAW_IMPORTS'
SORTED_DIR = BASE_DIR / 'Photos' / 'SORTED_BY_PERSON'
FRAMEWORK_DIR = BASE_DIR / 'EDITING_FRAMEWORK'
DATA_DIR = FRAMEWORK_DIR / 'face_data'

CLUSTERS_FILE = DATA_DIR / 'face_clusters.json'
LABELS_FILE = DATA_DIR / 'face_labels.json'

def main():
    if not CLUSTERS_FILE.exists() or not LABELS_FILE.exists():
        print("Missing face data or labels.")
        return

    # Load labels (cluster_id -> Person Name)
    with open(LABELS_FILE, 'r') as f:
        labels = json.load(f)

    # Load clusters
    with open(CLUSTERS_FILE, 'r') as f:
        data = json.load(f)

    count = 0
    
    # Process each cluster
    for cluster in data['clusters']:
        cluster_id = str(cluster['person_id'])
        
        # If this cluster has been labeled by the user
        if cluster_id in labels and labels[cluster_id].strip():
            person_name = labels[cluster_id].strip().replace("/", "_")
            person_dir = SORTED_DIR / person_name
            
            # For every photo containing this person's face
            for photo in cluster['photos']:
                folder = photo['folder']
                filename = photo['file']
                
                source_path = RAW_DIR / folder / filename
                if not source_path.exists():
                    continue
                    
                # We replicate the original folder structure inside their name folder
                # e.g. SORTED_BY_PERSON/Josh/Baby Pictures/img.jpg
                target_folder = person_dir / folder
                target_folder.mkdir(parents=True, exist_ok=True)
                
                target_path = target_folder / filename
                
                # Copy the file if it doesn't already exist (we use copy2 to preserve metadata/dates)
                if not target_path.exists():
                    shutil.copy2(source_path, target_path)
                    count += 1

    print(f"Sync complete! Copied {count} new photos into {SORTED_DIR}")

if __name__ == '__main__':
    main()
