import json

SEQ_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/ben-josh.json'

def main():
    with open(SEQ_FILE, 'r') as f:
        seq = json.load(f)
        
    slides = seq.get('slides', [])
    
    new_order = [
        8, 9, 11, 13, 15, 22, 23, 
        4, 20, 5, 12, 10, 14, 21, 6, 17, 18, 19, 24, 26, 16, 
        72, 73, 74, 75, 76, 77, 78, 55, 48, 49, 50, 51, 52, 53, 54, 
        33, 56, 62, 65, 
        25, 27, 29, 35, 57, 58, 59, 60, 61, 63, 64, 66, 67, 69, 70, 71, 
        0, 1, 2, 3, 7, 28, 30, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 68
    ]
    
    if len(new_order) != len(slides):
        print(f"Error: length mismatch! Expected {len(slides)}, got {len(new_order)}")
        return
        
    sorted_slides = []
    for idx in new_order:
        sorted_slides.append(slides[idx])
        
    seq['slides'] = sorted_slides
    
    with open(SEQ_FILE, 'w') as f:
        json.dump(seq, f, indent=2)
        
    print(f"Successfully reordered {len(sorted_slides)} slides in ben-josh.json")

if __name__ == '__main__':
    main()
