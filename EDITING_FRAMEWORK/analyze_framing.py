import os
import json
import cv2
from deepface import DeepFace

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

TIMELINE_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_timeline.json'
OUTPUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_framing_map.json'

def get_image_dimensions(filepath):
    # Use cv2 just to quickly grab width and height
    img = cv2.imread(filepath)
    if img is not None:
        return img.shape[1], img.shape[0] # width, height
    return 0, 0

def analyze_photo(path):
    print(f"Analyzing {os.path.basename(path)}...")
    width, height = get_image_dimensions(path)
    
    result = {
        "width": width,
        "height": height,
        "faces_found": 0,
        "center_of_mass": None, # [x, y] in pixels
        "raw_faces": []
    }
    
    if width == 0:
        return result
        
    try:
        # Enforce detection = False so it doesn't throw an exception if no face is found
        faces = DeepFace.extract_faces(img_path=path, enforce_detection=False, align=False)
        
        # If DeepFace returns a single dict (sometimes it does for single faces depending on version)
        if isinstance(faces, dict):
            faces = [faces]
            
        valid_faces = []
        for face_obj in faces:
            # Check if it actually found a face (confidence > 0)
            if face_obj.get('confidence', 0) > 0.5:
                region = face_obj.get('facial_area', {})
                if region:
                    x = region.get('x', 0)
                    y = region.get('y', 0)
                    w = region.get('w', 0)
                    h = region.get('h', 0)
                    valid_faces.append([x, y, w, h])
                    
        result["faces_found"] = len(valid_faces)
        result["raw_faces"] = valid_faces
        
        if valid_faces:
            total_x = 0
            total_y = 0
            for box in valid_faces:
                center_x = box[0] + (box[2] / 2)
                center_y = box[1] + (box[3] / 2)
                total_x += center_x
                total_y += center_y
                
            result["center_of_mass"] = [
                round(total_x / len(valid_faces)),
                round(total_y / len(valid_faces))
            ]
            
    except Exception as e:
        print(f"Error analyzing {os.path.basename(path)}: {e}")
        
    return result

def main():
    if not os.path.exists(TIMELINE_FILE):
        print("Timeline file not found!")
        return
        
    with open(TIMELINE_FILE, 'r') as f:
        timeline = json.load(f)
        
    framing_map = {}
    
    # Check if we are resuming
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            framing_map = json.load(f)
            
    total_photos = sum(len(photos) for photos in timeline.values())
    processed = 0
    
    for section, photos in timeline.items():
        for p in photos:
            path = p['path']
            filename = p['file']
            
            if filename not in framing_map:
                framing_map[filename] = analyze_photo(path)
                
                # Save frequently in case of crash
                with open(OUTPUT_FILE, 'w') as f:
                    json.dump(framing_map, f, indent=2)
            
            processed += 1
            if processed % 10 == 0:
                print(f"Progress: {processed}/{total_photos}")
                
    print(f"Finished analyzing {total_photos} photos for framing coordinates!")

if __name__ == '__main__':
    main()
