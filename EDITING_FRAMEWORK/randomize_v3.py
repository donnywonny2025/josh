import json
import os
import random
import xml.etree.ElementTree as ET
from urllib.parse import unquote

XML_PATH = "/Volumes/Extreme SSD/JOSH/Exports/Josh Master  Final Edit For Gemini.xml"
JSON_PATH = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline_v3.json"

def get_xml_photos():
    images = set()
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        for pathurl in root.iter('pathurl'):
            if pathurl.text:
                filepath = unquote(pathurl.text.replace('file://localhost', ''))
                filename = os.path.basename(filepath)
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.add(filename)
    except Exception as e:
        print(f"Error parsing XML: {e}")
    return images

def main():
    print("Extracting 176 photos from XML...")
    xml_images = get_xml_photos()
    print(f"Found {len(xml_images)} unique images in XML.")

    print(f"Loading {JSON_PATH}...")
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
        
    slides = data.get("slides", [])
    
    # 1. Filter down to ONLY the used photos, and keep their framing data
    filtered_slides = []
    
    for slide in slides:
        if slide.get("isCard"):
            continue # Remove title cards
        
        file_name = slide.get("file")
        if file_name and file_name in xml_images:
            # We want to remove sectionNames so it's a clean loop
            if "sectionName" in slide:
                del slide["sectionName"]
                
            # Overwrite duration to exactly 6 seconds
            # In V3 JSON, duration_frames is usually based on a 30fps timebase
            # So 6 seconds * 30 fps = 180 frames.
            # But the player also checks duration_sec.
            slide["duration_sec"] = 6.0
            slide["duration_frames"] = 180
            
            filtered_slides.append(slide)

    print(f"Filtered to {len(filtered_slides)} slides that matched the XML.")
    
    # Due to duplicates across folders or multiple uses, there might be slightly more than 176 slide items.
    # We will just shuffle them all.
    print("Shuffling slides...")
    random.shuffle(filtered_slides)
    
    data["slides"] = filtered_slides
    
    # Strip out sections from the root object if they exist
    if "sections" in data:
        data["sections"] = []
        
    print(f"Saving to {JSON_PATH}...")
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=4)
        
    print("Done! Sequence randomized.")

if __name__ == "__main__":
    main()
