#!/usr/bin/env python3
"""Josh Memorial — Face Discovery Scan
Finds all faces across all photos, clusters them by similarity,
and extracts face crops for identification.
"""
import face_recognition
import json
import os
import sys
import time
from pathlib import Path
from PIL import Image
import numpy as np

PHOTOS = Path("/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS")
OUTPUT = Path("/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/face_data")
OUTPUT.mkdir(exist_ok=True)
CROPS_DIR = OUTPUT / "crops"
CROPS_DIR.mkdir(exist_ok=True)

PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

def scan_all_photos():
    """Detect faces in all photos and collect encodings."""
    all_faces = []  # list of {folder, file, encoding, location, face_id}
    errors = []
    
    # Collect all photo files
    photo_files = []
    for folder in sorted(PHOTOS.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix.lower() in PHOTO_EXTS:
                photo_files.append((folder.name, f))
    
    total = len(photo_files)
    print(f"Scanning {total} photos for faces...")
    print("=" * 60)
    
    for i, (folder_name, filepath) in enumerate(photo_files):
        try:
            # Load image
            img = face_recognition.load_image_file(str(filepath))
            
            # Detect faces - use 'cnn' model for better accuracy if available, else 'hog'
            locations = face_recognition.face_locations(img, model='hog')
            
            if locations:
                encodings = face_recognition.face_encodings(img, locations)
                
                for j, (loc, enc) in enumerate(zip(locations, encodings)):
                    face_id = f"face_{len(all_faces):04d}"
                    top, right, bottom, left = loc
                    
                    # Save face crop
                    pil_img = Image.fromarray(img)
                    # Add padding around face
                    h, w = img.shape[:2]
                    pad_h = int((bottom - top) * 0.4)
                    pad_w = int((right - left) * 0.4)
                    crop_top = max(0, top - pad_h)
                    crop_bottom = min(h, bottom + pad_h)
                    crop_left = max(0, left - pad_w)
                    crop_right = min(w, right + pad_w)
                    
                    face_crop = pil_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                    face_crop = face_crop.resize((200, 200), Image.LANCZOS)
                    crop_path = CROPS_DIR / f"{face_id}.jpg"
                    face_crop.save(str(crop_path), quality=85)
                    
                    all_faces.append({
                        'face_id': face_id,
                        'folder': folder_name,
                        'file': filepath.name,
                        'encoding': enc.tolist(),
                        'location': list(loc),
                        'crop': str(crop_path)
                    })
                
                print(f"  [{i+1}/{total}] {folder_name}/{filepath.name} — {len(locations)} face(s)")
            else:
                if (i+1) % 20 == 0:
                    print(f"  [{i+1}/{total}] scanning... ({len(all_faces)} faces so far)")
                    
        except Exception as e:
            errors.append(f"{folder_name}/{filepath.name}: {str(e)[:80]}")
            if (i+1) % 20 == 0:
                print(f"  [{i+1}/{total}] scanning... ({len(all_faces)} faces so far)")
    
    print(f"\nScan complete: {len(all_faces)} faces found in {total} photos")
    if errors:
        print(f"  {len(errors)} files had errors")
    
    return all_faces, errors


def cluster_faces(all_faces, tolerance=0.55):
    """Cluster faces by similarity."""
    if not all_faces:
        return []
    
    print(f"\nClustering {len(all_faces)} faces (tolerance={tolerance})...")
    
    encodings = [np.array(f['encoding']) for f in all_faces]
    clusters = []  # list of lists of face indices
    assigned = set()
    
    for i, face in enumerate(all_faces):
        if i in assigned:
            continue
        
        # Start new cluster with this face
        cluster = [i]
        assigned.add(i)
        
        # Find all matching faces
        enc_i = encodings[i]
        for j in range(i + 1, len(all_faces)):
            if j in assigned:
                continue
            distance = np.linalg.norm(enc_i - encodings[j])
            if distance < tolerance:
                cluster.append(j)
                assigned.add(j)
        
        clusters.append(cluster)
    
    # Sort clusters by size (most frequent person first)
    clusters.sort(key=len, reverse=True)
    
    print(f"Found {len(clusters)} unique faces")
    for i, cluster in enumerate(clusters[:20]):
        sample = all_faces[cluster[0]]
        print(f"  Person {i+1}: {len(cluster)} photos (e.g. {sample['folder']}/{sample['file']})")
    if len(clusters) > 20:
        print(f"  ... and {len(clusters) - 20} more (appearing in fewer photos)")
    
    return clusters


def save_results(all_faces, clusters, errors):
    """Save scan results."""
    # Build cluster data
    cluster_data = []
    for i, cluster_indices in enumerate(clusters):
        faces_in_cluster = [all_faces[idx] for idx in cluster_indices]
        # Get best crop (first one found)
        representative = faces_in_cluster[0]
        
        photos = [{'folder': f['folder'], 'file': f['file']} for f in faces_in_cluster]
        # Deduplicate photos (same person can appear multiple times in same photo via different detections)
        unique_photos = list({f"{p['folder']}/{p['file']}": p for p in photos}.values())
        
        cluster_data.append({
            'person_id': i + 1,
            'label': f'Unknown Person {i + 1}',
            'photo_count': len(unique_photos),
            'face_count': len(cluster_indices),
            'representative_crop': representative['face_id'] + '.jpg',
            'photos': unique_photos,
            'face_ids': [all_faces[idx]['face_id'] for idx in cluster_indices]
        })
    
    results = {
        'scan_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_faces_detected': len(all_faces),
        'unique_persons': len(clusters),
        'clusters': cluster_data,
        'errors': errors
    }
    
    out_file = OUTPUT / 'face_clusters.json'
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_file}")
    
    # Also save raw encodings for later matching
    enc_file = OUTPUT / 'face_encodings.json'
    enc_data = []
    for face in all_faces:
        enc_data.append({
            'face_id': face['face_id'],
            'folder': face['folder'],
            'file': face['file'],
            'encoding': face['encoding'],
            'location': face['location']
        })
    with open(enc_file, 'w') as f:
        json.dump(enc_data, f)
    print(f"Encodings saved to {enc_file}")
    
    return results


if __name__ == '__main__':
    start = time.time()
    all_faces, errors = scan_all_photos()
    clusters = cluster_faces(all_faces)
    results = save_results(all_faces, clusters, errors)
    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
