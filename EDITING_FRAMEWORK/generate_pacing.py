import json
import os

TIMELINE_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_timeline.json'
OUTPUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/timeline_pacing_map.json'

PHOTO_DURATION_SECONDS = 2.5
TRANSITION_OVERLAP_SECONDS = 0.5  # Time for crossdissolves

def main():
    if not os.path.exists(TIMELINE_FILE):
        print("Timeline file not found!")
        return
        
    with open(TIMELINE_FILE, 'r') as f:
        timeline = json.load(f)
        
    pacing_map = {
        "global_settings": {
            "fps": 23.976,
            "duration_per_photo": PHOTO_DURATION_SECONDS,
            "transition_overlap": TRANSITION_OVERLAP_SECONDS
        },
        "sequence": []
    }
    
    current_time = 0.0
    
    # Order of sections based on thematic arc
    sections = [
        "Military",
        "Travel_Fun",
        "Ben_and_Josh",
        "Passed_Loved_Ones",
        "General"
    ]
    
    total_photos = 0
    for section in sections:
        photos = timeline.get(section, [])
        for p in photos:
            # We want each photo to display for PHOTO_DURATION_SECONDS
            # But the actual clip needs to be longer to account for transition overlaps
            # Timeline IN point
            start_time = current_time
            # Timeline OUT point
            end_time = current_time + PHOTO_DURATION_SECONDS
            
            pacing_map["sequence"].append({
                "file": p["file"],
                "path": p["path"],
                "section": section,
                "timeline_in_s": round(start_time, 3),
                "timeline_out_s": round(end_time, 3),
                "source_duration_s": round(PHOTO_DURATION_SECONDS + TRANSITION_OVERLAP_SECONDS, 3)
            })
            
            # Advance the global clock. We subtract overlap so the next photo starts during the fade
            current_time = end_time - TRANSITION_OVERLAP_SECONDS
            total_photos += 1
            
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(pacing_map, f, indent=2)
        
    total_minutes = current_time / 60.0
    print(f"Pacing generated for {total_photos} photos.")
    print(f"Total Sequence Duration: {round(total_minutes, 2)} minutes.")

if __name__ == '__main__':
    main()
