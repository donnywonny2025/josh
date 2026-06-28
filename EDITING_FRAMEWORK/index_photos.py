#!/usr/bin/env python3
"""
Josh Memorial — Full Photo Inventory & Metadata Indexer
Scans all files in RAW_IMPORTS, extracts EXIF metadata, and writes:
  1. master_inventory.json — machine-readable full index
  2. PHOTO_INVENTORY.md — human-readable summary
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Try Pillow for EXIF
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

PHOTOS_DIR = Path("/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS")
OUTPUT_JSON = Path("/Volumes/Extreme SSD/JOSH/KNOWLEDGE_BASE/master_inventory.json")
OUTPUT_MD = Path("/Volumes/Extreme SSD/JOSH/KNOWLEDGE_BASE/PHOTO_INVENTORY.md")

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
VIDEO_EXTS = {'.mov', '.mp4', '.m4v'}
HEIC_EXTS = {'.heic'}

def get_exif_data(filepath):
    """Extract EXIF metadata from an image file."""
    exif_dict = {}
    if not HAS_PIL:
        return exif_dict
    try:
        img = Image.open(filepath)
        exif_raw = img._getexif()
        if exif_raw:
            for tag_id, value in exif_raw.items():
                tag = TAGS.get(tag_id, str(tag_id))
                # Skip binary/thumbnail data
                if tag in ('MakerNote', 'UserComment', 'PrintImageMatching', 
                           'ComponentsConfiguration', 'FileSource', 'SceneType',
                           'CFAPattern', 'XMLPacket', 'InterColorProfile',
                           'ThumbnailImage', 'JPEGThumbnail'):
                    continue
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore')
                    except:
                        value = str(value)[:100]
                elif isinstance(value, (tuple, list)):
                    value = str(value)
                exif_dict[tag] = value
        
        # Get dimensions
        exif_dict['_width'] = img.width
        exif_dict['_height'] = img.height
        exif_dict['_mode'] = img.mode
        img.close()
    except Exception as e:
        exif_dict['_error'] = str(e)
    return exif_dict

def parse_date_from_exif(exif):
    """Try to extract a usable date from EXIF data."""
    for key in ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime'):
        val = exif.get(key)
        if val:
            try:
                # EXIF dates: "2018:02:21 14:30:00"
                dt = datetime.strptime(str(val).strip(), "%Y:%m:%d %H:%M:%S")
                return dt.isoformat()
            except:
                return str(val)
    return None

def parse_date_from_filename(filename):
    """Try to extract date info from filename patterns."""
    import re
    name = filename
    
    # Pattern: "Photo Jun 06 2026, 9 54 06 AM"
    m = re.search(r'Photo (\w+ \d+ \d{4})', name)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%b %d %Y")
            return dt.strftime("%Y-%m-%d"), "filename"
        except:
            pass
    
    # Pattern: "Video Feb 25 2021, 2 35 17 PM"
    m = re.search(r'Video (\w+ \d+ \d{4})', name)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%b %d %Y")
            return dt.strftime("%Y-%m-%d"), "filename"
        except:
            pass
    
    # Pattern: IMG_20171212_0261
    m = re.search(r'(\d{4})(\d{2})(\d{2})_', name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "filename"
    
    # Pattern: "1994 Photos" or "1991 photos" or "2010_"
    m = re.search(r'(19\d{2}|20[0-2]\d)', name)
    if m:
        return m.group(1), "filename_year"
    
    # Pattern: "Phyllis Old Photos_20180221_0007"
    m = re.search(r'_(\d{8})_', name)
    if m:
        d = m.group(1)
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}", "filename"
    
    return None, None

def get_gps_coords(exif):
    """Extract GPS coordinates if present."""
    gps_info = exif.get('GPSInfo')
    if not gps_info or not isinstance(gps_info, dict):
        return None
    try:
        def convert_to_degrees(value):
            d, m, s = value
            return float(d) + float(m)/60 + float(s)/3600
        
        lat = convert_to_degrees(gps_info.get(2, (0,0,0)))
        if gps_info.get(1) == 'S':
            lat = -lat
        lon = convert_to_degrees(gps_info.get(4, (0,0,0)))
        if gps_info.get(3) == 'W':
            lon = -lon
        return {"lat": round(lat, 6), "lon": round(lon, 6)}
    except:
        return None

def scan_all():
    """Scan all files and build the full inventory."""
    inventory = {
        "generated": datetime.now().isoformat(),
        "source": str(PHOTOS_DIR),
        "summary": {},
        "folders": {}
    }
    
    total_files = 0
    total_photos = 0
    total_videos = 0
    total_heic = 0
    total_other = 0
    total_size = 0
    all_dates = []
    all_cameras = set()
    has_gps_count = 0
    
    folders = sorted([d for d in PHOTOS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')])
    
    for folder in folders:
        folder_name = folder.name
        folder_data = {"files": [], "stats": {}}
        folder_photos = 0
        folder_videos = 0
        folder_size = 0
        
        files = sorted([f for f in folder.iterdir() if f.is_file() and not f.name.startswith('.')])
        
        for f in files:
            total_files += 1
            ext = f.suffix.lower()
            size = f.stat().st_size
            total_size += size
            folder_size += size
            
            file_entry = {
                "name": f.name,
                "ext": ext,
                "size_bytes": size,
                "size_mb": round(size / (1024*1024), 2),
            }
            
            # Determine type
            if ext in IMAGE_EXTS:
                file_entry["type"] = "photo"
                folder_photos += 1
                total_photos += 1
                
                # Get EXIF
                exif = get_exif_data(f)
                
                # Dimensions
                if '_width' in exif:
                    file_entry["width"] = exif['_width']
                    file_entry["height"] = exif['_height']
                    file_entry["orientation"] = "landscape" if exif['_width'] > exif['_height'] else "portrait" if exif['_height'] > exif['_width'] else "square"
                
                # Date
                exif_date = parse_date_from_exif(exif)
                fn_date, fn_source = parse_date_from_filename(f.name)
                if exif_date:
                    file_entry["date"] = exif_date
                    file_entry["date_source"] = "exif"
                elif fn_date:
                    file_entry["date"] = fn_date
                    file_entry["date_source"] = fn_source
                
                if file_entry.get("date"):
                    all_dates.append(file_entry["date"][:4])  # Just year
                
                # Camera
                camera = exif.get('Model', exif.get('Make', ''))
                if camera:
                    file_entry["camera"] = str(camera).strip()
                    all_cameras.add(file_entry["camera"])
                
                # GPS
                gps = get_gps_coords(exif)
                if gps:
                    file_entry["gps"] = gps
                    has_gps_count += 1
                
                # Key EXIF fields
                for key in ('Make', 'Model', 'Software', 'Orientation', 'Flash',
                            'FocalLength', 'ExposureTime', 'FNumber', 'ISOSpeedRatings'):
                    if key in exif:
                        file_entry[f"exif_{key}"] = str(exif[key])
                
            elif ext in VIDEO_EXTS:
                file_entry["type"] = "video"
                folder_videos += 1
                total_videos += 1
                fn_date, fn_source = parse_date_from_filename(f.name)
                if fn_date:
                    file_entry["date"] = fn_date
                    file_entry["date_source"] = fn_source
                
            elif ext in HEIC_EXTS:
                file_entry["type"] = "heic"
                total_heic += 1
                fn_date, fn_source = parse_date_from_filename(f.name)
                if fn_date:
                    file_entry["date"] = fn_date
                    file_entry["date_source"] = fn_source
                    
            else:
                file_entry["type"] = "other"
                total_other += 1
            
            folder_data["files"].append(file_entry)
            
            # Progress
            if total_files % 25 == 0:
                print(f"  Scanned {total_files} files...", flush=True)
        
        folder_data["stats"] = {
            "total": len(files),
            "photos": folder_photos,
            "videos": folder_videos,
            "size_mb": round(folder_size / (1024*1024), 1)
        }
        inventory["folders"][folder_name] = folder_data
        print(f"✓ {folder_name}: {len(files)} files ({round(folder_size/(1024*1024),1)}MB)", flush=True)
    
    # Year distribution
    from collections import Counter
    year_counts = Counter(all_dates)
    
    inventory["summary"] = {
        "total_files": total_files,
        "total_photos": total_photos,
        "total_videos": total_videos,
        "total_heic": total_heic,
        "total_other": total_other,
        "total_size_mb": round(total_size / (1024*1024), 1),
        "total_size_gb": round(total_size / (1024*1024*1024), 2),
        "folders_count": len(folders),
        "cameras": sorted(all_cameras),
        "has_gps": has_gps_count,
        "years": dict(sorted(year_counts.items())),
        "date_range": f"{min(all_dates) if all_dates else '?'} — {max(all_dates) if all_dates else '?'}"
    }
    
    return inventory

def write_markdown(inv):
    """Write human-readable inventory to markdown."""
    s = inv["summary"]
    lines = []
    lines.append("# Josh Memorial — Complete Photo Inventory")
    lines.append(f"\n*Generated: {inv['generated'][:19]}*\n")
    
    lines.append("## Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Files | **{s['total_files']}** |")
    lines.append(f"| Photos (JPG/PNG/GIF) | {s['total_photos']} |")
    lines.append(f"| HEIC Files | {s['total_heic']} |")
    lines.append(f"| Videos (MOV/MP4) | {s['total_videos']} |")
    lines.append(f"| Other Files | {s['total_other']} |")
    lines.append(f"| Total Size | {s['total_size_gb']} GB |")
    lines.append(f"| Folders | {s['folders_count']} |")
    lines.append(f"| Photos with GPS | {s['has_gps']} |")
    lines.append(f"| Date Range (years) | {s['date_range']} |")
    
    if s['cameras']:
        lines.append(f"\n### Cameras Detected\n")
        for cam in s['cameras']:
            lines.append(f"- {cam}")
    
    if s['years']:
        lines.append(f"\n### Photos by Year\n")
        lines.append("| Year | Count |")
        lines.append("|------|-------|")
        for year, count in sorted(s['years'].items()):
            lines.append(f"| {year} | {count} |")
    
    lines.append("\n---\n")
    lines.append("## Folders Detail\n")
    
    for folder_name, fdata in inv["folders"].items():
        stats = fdata["stats"]
        lines.append(f"### 📁 {folder_name}")
        lines.append(f"*{stats['total']} files — {stats['photos']} photos, {stats['videos']} videos — {stats['size_mb']}MB*\n")
        
        lines.append("| # | Filename | Type | Size | Dimensions | Date | Camera |")
        lines.append("|---|----------|------|------|------------|------|--------|")
        
        for i, f in enumerate(fdata["files"], 1):
            dims = f"{f.get('width','?')}×{f.get('height','?')}" if 'width' in f else "—"
            date = f.get('date', '—')
            if len(date) > 10:
                date = date[:10]
            camera = f.get('camera', '—')
            if len(camera) > 20:
                camera = camera[:20]
            gps = " 📍" if f.get('gps') else ""
            size = f"{f['size_mb']}MB"
            lines.append(f"| {i} | {f['name'][:45]} | {f['type']} | {size} | {dims} | {date}{gps} | {camera} |")
        
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    print("=" * 60)
    print("Josh Memorial — Full Metadata Scan")
    print("=" * 60)
    print(f"Source: {PHOTOS_DIR}")
    print(f"Start: {datetime.now().isoformat()[:19]}")
    print()
    
    inventory = scan_all()
    
    # Write JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(inventory, f, indent=2, default=str)
    print(f"\n✓ JSON written to: {OUTPUT_JSON}")
    
    # Write Markdown
    md = write_markdown(inventory)
    with open(OUTPUT_MD, 'w') as f:
        f.write(md)
    print(f"✓ Markdown written to: {OUTPUT_MD}")
    
    # Print summary
    s = inventory["summary"]
    print(f"\n{'='*60}")
    print(f"DONE — {s['total_files']} files scanned")
    print(f"  Photos: {s['total_photos']} | HEIC: {s['total_heic']} | Videos: {s['total_videos']}")
    print(f"  Size: {s['total_size_gb']} GB")
    print(f"  GPS tagged: {s['has_gps']}")
    print(f"  Date range: {s['date_range']}")
    print(f"  Cameras: {', '.join(s['cameras'][:10])}")
    print(f"  Years: {s['years']}")
