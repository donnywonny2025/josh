import json

SEQ_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/ben-josh.json'

def main():
    # This was the order I applied in the previous script.
    # Therefore, current_slides[i] corresponds to original_index = previous_applied_order[i]
    previous_applied_order = [
        8, 9, 11, 13, 15, 22, 23, 
        4, 20, 5, 12, 10, 14, 21, 6, 17, 18, 19, 24, 26, 16, 
        72, 73, 74, 75, 76, 77, 78, 55, 48, 49, 50, 51, 52, 53, 54, 
        33, 56, 62, 65, 
        25, 27, 29, 35, 57, 58, 59, 60, 61, 63, 64, 66, 67, 69, 70, 71, 
        0, 1, 2, 3, 7, 28, 30, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 68
    ]
    
    # This is the new, highly refined order based on my deep analysis of Josh's age
    new_refined_order = [
        9, 8, 13, 22, 11, 15, 23, # Stage 1: Infant
        21, 19, 26, 18, 17, 24,   # Stage 2: Toddler
        5, 12, 4, 20, 16, 6, 14,  # Stage 3: Young Kids
        55, 72, 74, 75, 49, 10,   # Stage 4: Older Kids
        51, 54, 73, 76, 77, 78, 48, 50, 52, 53, # Stage 5: Pre-Teens
        33, 62, 56, 65,           # Stage 6: Teens
        29, 64, 25, 66, 67, 70, 71, 69, 35, 59, 63, 61, 27, 57, 58, 60, # Stage 7: Young Adults
        28, 30, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 68, 7, 0, 1, 2, 3 # Stage 8: Adults
    ]
    
    with open(SEQ_FILE, 'r') as f:
        seq = json.load(f)
        
    current_slides = seq.get('slides', [])
    
    if len(current_slides) != len(previous_applied_order):
        print(f"Error: length mismatch! Expected {len(previous_applied_order)}, got {len(current_slides)}")
        return
        
    # Reconstruct a dictionary of original_index -> slide_data
    original_slides_map = {}
    for i, slide in enumerate(current_slides):
        orig_idx = previous_applied_order[i]
        original_slides_map[orig_idx] = slide
        
    # Build the final array using the new refined order
    sorted_slides = []
    for orig_idx in new_refined_order:
        sorted_slides.append(original_slides_map[orig_idx])
        
    seq['slides'] = sorted_slides
    
    with open(SEQ_FILE, 'w') as f:
        json.dump(seq, f, indent=2)
        
    print(f"Successfully applied refined sort to {len(sorted_slides)} slides in ben-josh.json")

if __name__ == '__main__':
    main()
