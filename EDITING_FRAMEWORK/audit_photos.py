import json

with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json') as f:
    tl = json.load(f)

sections = {}
for sl in tl.get('slides', []):
    if sl.get('isCard') or sl.get('isPlaceholder'): continue
    sec = sl.get('sectionName', 'Unknown')
    if sec not in sections: sections[sec] = []
    sections[sec].append(sl)

with open('/Users/jeffkerr/.gemini/antigravity-ide/brain/e05efdc0-ee5c-4503-bbb2-79ae7db0a034/timeline_photo_audit.md', 'w') as out:
    out.write("# Timeline Photo Audit\n\n")
    out.write("This document contains a full scan of every photo currently slotted into the master timeline, organized by section.\n\n")
    out.write("## 1. How Photos Were Assigned\n")
    out.write("The current assignment logic (from `assign_sections.py`) uses a fallback hierarchy:\n")
    out.write("1. **Metadata/Filename Year**: It scans the EXIF data or the filename for a 4-digit year (e.g., 1990, 2012). It calculates Josh's estimated age (assuming birth year ~1990) and maps the age to a life phase (e.g. 0-5 = Baby/Toddler).\n")
    out.write("2. **Folder Context**: If no date is found, it uses keyword rules on the folder name (e.g., 'Military' -> Military section, 'Friends' -> High School).\n")
    out.write("3. **Fallback**: If all else fails, it drops it in 'Recent Mix'.\n\n")
    out.write("---\n\n")
    out.write("## 2. Photo Inventory\n\n")
    
    for sec_name, photos in sections.items():
        out.write(f"### Section: {sec_name.upper()} ({len(photos)} photos)\n")
        for p in photos:
            out.write(f"- `{p.get('file')}` (Source folder: *{p.get('folder')}*)\n")
        out.write("\n")

print("Audit generated.")
