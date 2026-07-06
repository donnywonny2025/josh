import json
import os

with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json') as f:
    tl = json.load(f)

# Collect all photos
photos = []
for sl in tl.get('slides', []):
    if sl.get('isCard') or sl.get('isPlaceholder'): continue
    photos.append(sl)

# Group by section
sections = {}
for p in photos:
    sec = p.get('sectionName', 'Unknown')
    if sec not in sections: sections[sec] = []
    sections[sec].append(p)

out_path = '/Users/jeffkerr/.gemini/antigravity-ide/brain/e05efdc0-ee5c-4503-bbb2-79ae7db0a034/photo_tracker.md'
with open(out_path, 'w') as out:
    out.write('# Master Photo Tracker\n\n')
    out.write('This document tracks every single photo currently slotted in the timeline. It ensures we do not use the same photo twice, and serves as our workspace for building out descriptions of each photo as we dial in the pacing.\n\n')
    
    # Check for duplicates
    filenames = [p.get('file') for p in photos]
    duplicates = set([x for x in filenames if filenames.count(x) > 1])
    if duplicates:
        out.write('> [!WARNING]\n')
        out.write(f'> **Duplicates Detected:** {len(duplicates)} photos are currently used more than once! We will need to swap these out.\n\n')
    else:
        out.write('> [!TIP]\n')
        out.write('> **No Duplicates:** Currently, every photo in the timeline is unique.\n\n')
    
    out.write('---\n\n')
    
    for sec_name, sec_photos in sections.items():
        out.write(f'## {sec_name.upper()}\n\n')
        out.write('| Status | Photo File | Source Folder | Visual Description (To Be Written) |\n')
        out.write('|---|---|---|---|\n')
        for p in sec_photos:
            file_name = p.get('file', 'Unknown')
            folder_name = p.get('folder', 'Unknown')
            # Check if it's a duplicate
            is_dup = file_name in duplicates
            status = '⚠️ DUP' if is_dup else '✅ Unique'
            out.write(f'| {status} | `{file_name}` | {folder_name} | *Pending Visual Scan* |\n')
        out.write('\n')
print('Tracker generated.')
