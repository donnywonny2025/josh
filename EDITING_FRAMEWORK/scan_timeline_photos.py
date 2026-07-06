import json
import os
import time
import sys
import google.generativeai as genai
from PIL import Image

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    # Use Gemini 1.5 Flash as it is fast and excellent for multimodal tasks
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    tl_path = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json'
    out_path = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_descriptions.json'
    
    with open(tl_path, 'r') as f:
        tl = json.load(f)
        
    # Load existing descriptions so we don't start from scratch if interrupted
    descriptions = {}
    if os.path.exists(out_path):
        with open(out_path, 'r') as f:
            descriptions = json.load(f)
            
    photos = []
    for sl in tl.get('slides', []):
        if sl.get('isCard') or sl.get('isPlaceholder'): continue
        photos.append(sl)
        
    print(f"Scanning {len(photos)} photos...")
    
    for i, p in enumerate(photos):
        filename = p.get('file')
        filepath = p.get('path')
        
        if not filename or not filepath:
            continue
            
        if filename in descriptions:
            print(f"[{i+1}/{len(photos)}] Skipping {filename} (already scanned)")
            continue
            
        if not os.path.exists(filepath):
            print(f"[{i+1}/{len(photos)}] ERROR: File not found: {filepath}")
            continue
            
        print(f"[{i+1}/{len(photos)}] Analyzing {filename}...")
        
        try:
            img = Image.open(filepath)
            
            # Compress image to speed up upload if it's very large
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024))
                
            prompt = "Describe what is happening in this photo concisely. Focus on the people, the setting, and the mood. Keep it to 1-2 brief sentences."
            
            response = model.generate_content([prompt, img])
            desc = response.text.strip()
            
            descriptions[filename] = {
                "folder": p.get('folder'),
                "description": desc
            }
            
            # Save incrementally
            with open(out_path, 'w') as f:
                json.dump(descriptions, f, indent=2)
                
            time.sleep(1) # Simple rate limiting
            
        except Exception as e:
            print(f"ERROR on {filename}: {str(e)}")
            time.sleep(5)
            
    print("\n✅ Vision scan complete!")
    print(f"Descriptions saved to {out_path}")

if __name__ == '__main__':
    main()
