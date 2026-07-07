import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess

import datetime

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
TIMELINE_FILE = os.path.join(PROJECT_ROOT, "EDITING_FRAMEWORK", "sequences", "master_timeline.json")
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")

TIMEBASE = 24
NTSC = "FALSE"
WIDTH, HEIGHT = 1920, 1080

def get_image_dimensions(filepath):
    # Try PIL first to catch EXIF orientation
    try:
        from PIL import Image, ExifTags
        img = Image.open(filepath)
        w, h = img.size
        exif = img._getexif()
        if exif:
            for k, v in exif.items():
                if ExifTags.TAGS.get(k) == "Orientation":
                    if v in [5, 6, 7, 8]:
                        w, h = h, w
                    break
        return w, h
    except Exception:
        pass
        
    # Fallback to ffprobe
    cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", filepath]
    try:
        output = subprocess.check_output(cmd, text=True).strip()
        if output:
            parts = output.split(",")
            return int(parts[0]), int(parts[1])
    except: pass
    return 1920, 1080

def encode_path(p):
    # CRITICAL: Ampersands must be &amp; not %26 in Premiere XML!
    return p.replace(" ", "%20").replace("&", "&amp;")

def build_xml():
    with open(TIMELINE_FILE, 'r') as f:
        timeline = json.load(f)
        
    xmeml = ET.Element("xmeml", version="4")
    project = ET.SubElement(xmeml, "project")
    ET.SubElement(project, "name").text = "Josh_Master_Sequence"
    children = ET.SubElement(project, "children")
    
    bin_el = ET.SubElement(children, "bin")
    ET.SubElement(bin_el, "name").text = "Photos"
    bin_children = ET.SubElement(bin_el, "children")
    
    sequence = ET.SubElement(children, "sequence", id="master_sequence")
    ET.SubElement(sequence, "name").text = "Josh Master Beat Mapped"
    
    rate = ET.SubElement(sequence, "rate")
    ET.SubElement(rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(rate, "ntsc").text = NTSC
    
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    format_el = ET.SubElement(video, "format")
    sc = ET.SubElement(format_el, "samplecharacteristics")
    sc_rate = ET.SubElement(sc, "rate")
    ET.SubElement(sc_rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(sc_rate, "ntsc").text = NTSC
    ET.SubElement(sc, "width").text = str(WIDTH)
    ET.SubElement(sc, "height").text = str(HEIGHT)
    ET.SubElement(sc, "pixelaspectratio").text = "square"
    
    v_track = ET.SubElement(video, "track")
    
    current_frame = 0
    cumulative_seconds = 0.0
    photo_idx = 0
    
    for slide in timeline['slides']:
        if slide.get('isPlaceholder'):
            continue
            
        dur_30 = int(slide.get("duration_frames", 150))
        
        # Calculate anti-drift Native 24fps duration
        dur_sec = dur_30 / 30.0
        cumulative_seconds += dur_sec
        target_frame = round(cumulative_seconds * TIMEBASE)
        dur = target_frame - current_frame
        
        if slide.get('isCard'):
            filename = "black_slug.png"
            filepath = os.path.join(PROJECT_ROOT, "EDITING_FRAMEWORK", filename)
        else:
            filename = slide['file']
            folder = slide['folder']
            filepath = os.path.join(PROJECT_ROOT, "Photos", "RAW_IMPORTS", folder, filename)
            
        photo_idx += 1
        fid = f"photo_{photo_idx}"
        url = "file://localhost" + encode_path(filepath)
        
        # Dimensions
        w, h = get_image_dimensions(filepath)
        scale_x = WIDTH / float(w)
        scale_y = HEIGHT / float(h)
        scale_factor = max(scale_x, scale_y)
        target_scale = scale_factor * 100.0
        
        # Ken Burns push: 5% zoom
        end_scale = target_scale * 1.05
        
        # Position
        fx = slide.get("focus", [50, 50])[0]
        fy = slide.get("focus", [50, 50])[1]
        
        dx_pixels = (0.5 - fx/100.0) * w * scale_factor
        dy_pixels = (0.5 - fy/100.0) * h * scale_factor
        max_dx = max(0, (w * scale_factor - WIDTH) / 2.0)
        max_dy = max(0, (h * scale_factor - HEIGHT) / 2.0)
        
        dx_pixels = max(-max_dx, min(max_dx, dx_pixels))
        dy_pixels = max(-max_dy, min(max_dy, dy_pixels))
        
        horiz = dx_pixels / float(WIDTH)
        vert = dy_pixels / float(HEIGHT)
        
        # 1. Add Master Clip
        clip_el = ET.SubElement(bin_children, "clip", id=f"masterclip-{fid}")
        ET.SubElement(clip_el, "masterclipid").text = f"masterclip-{fid}"
        ET.SubElement(clip_el, "ismasterclip").text = "TRUE"
        ET.SubElement(clip_el, "duration").text = str(86400) # Duration MUST be here, NOT in file
        
        clip_rate = ET.SubElement(clip_el, "rate")
        ET.SubElement(clip_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(clip_rate, "ntsc").text = NTSC
        
        ET.SubElement(clip_el, "in").text = "0"
        ET.SubElement(clip_el, "out").text = str(86400 - 1)
        ET.SubElement(clip_el, "name").text = filename
        
        clip_media = ET.SubElement(clip_el, "media")
        clip_video = ET.SubElement(clip_media, "video")
        clip_track = ET.SubElement(clip_video, "track")
        
        clipitem = ET.SubElement(clip_track, "clipitem", id=f"clipitem-master-{fid}")
        ET.SubElement(clipitem, "masterclipid").text = f"masterclip-{fid}"
        ET.SubElement(clipitem, "name").text = filename
        
        # CRITICAL: Additional formatting parameters
        ET.SubElement(clipitem, "alphatype").text = "none"
        ET.SubElement(clipitem, "pixelaspectratio").text = "square"
        ET.SubElement(clipitem, "anamorphic").text = "FALSE"
        
        ci_rate = ET.SubElement(clipitem, "rate")
        ET.SubElement(ci_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(ci_rate, "ntsc").text = NTSC
        
        file_el = ET.SubElement(clipitem, "file", id=f"file-{fid}")
        ET.SubElement(file_el, "name").text = filename
        ET.SubElement(file_el, "pathurl").text = url
        
        file_rate = ET.SubElement(file_el, "rate")
        ET.SubElement(file_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(file_rate, "ntsc").text = NTSC
        
        # CRITICAL: Mandatory Timecode block
        timecode = ET.SubElement(file_el, "timecode")
        tc_rate = ET.SubElement(timecode, "rate")
        ET.SubElement(tc_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(tc_rate, "ntsc").text = NTSC
        ET.SubElement(timecode, "string").text = "00:00:00:00"
        ET.SubElement(timecode, "frame").text = "0"
        ET.SubElement(timecode, "displayformat").text = "NDF"
        
        file_media = ET.SubElement(file_el, "media")
        file_video = ET.SubElement(file_media, "video")
        sc_file = ET.SubElement(file_video, "samplecharacteristics")
        sc_file_rate = ET.SubElement(sc_file, "rate")
        ET.SubElement(sc_file_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(sc_file_rate, "ntsc").text = NTSC
        ET.SubElement(sc_file, "width").text = str(w)
        ET.SubElement(sc_file, "height").text = str(h)
        ET.SubElement(sc_file, "pixelaspectratio").text = "square"

        # 2. Add to Sequence Track
        seq_clip = ET.SubElement(v_track, "clipitem", id=f"seq-clip-{fid}")
        ET.SubElement(seq_clip, "name").text = filename
        ET.SubElement(seq_clip, "duration").text = str(86400)
        seq_clip_rate = ET.SubElement(seq_clip, "rate")
        ET.SubElement(seq_clip_rate, "timebase").text = str(TIMEBASE)
        ET.SubElement(seq_clip_rate, "ntsc").text = NTSC
        
        ET.SubElement(seq_clip, "start").text = str(current_frame)
        ET.SubElement(seq_clip, "end").text = str(current_frame + dur)
        ET.SubElement(seq_clip, "enabled").text = "TRUE"
        ET.SubElement(seq_clip, "in").text = "0"
        ET.SubElement(seq_clip, "out").text = str(dur)
        ET.SubElement(seq_clip, "file").set("id", f"file-{fid}")
        
        # 3. Add Basic Motion Filter
        filter_el = ET.SubElement(seq_clip, "filter")
        effect_el = ET.SubElement(filter_el, "effect")
        ET.SubElement(effect_el, "name").text = "Basic Motion"
        ET.SubElement(effect_el, "effectid").text = "basic"
        ET.SubElement(effect_el, "effectcategory").text = "motion"
        ET.SubElement(effect_el, "effecttype").text = "motion"
        ET.SubElement(effect_el, "mediatype").text = "video"
        
        param_scale = ET.SubElement(effect_el, "parameter")
        ET.SubElement(param_scale, "parameterid").text = "scale"
        ET.SubElement(param_scale, "name").text = "Scale"
        kf_scale_1 = ET.SubElement(param_scale, "keyframe")
        ET.SubElement(kf_scale_1, "when").text = "0"
        ET.SubElement(kf_scale_1, "value").text = f"{target_scale:.2f}"
        kf_scale_2 = ET.SubElement(param_scale, "keyframe")
        ET.SubElement(kf_scale_2, "when").text = str(dur)
        ET.SubElement(kf_scale_2, "value").text = f"{end_scale:.2f}"
        
        param_center = ET.SubElement(effect_el, "parameter")
        ET.SubElement(param_center, "parameterid").text = "center"
        ET.SubElement(param_center, "name").text = "Center"
        val_center = ET.SubElement(param_center, "value")
        ET.SubElement(val_center, "horiz").text = f"{horiz:.6f}"
        ET.SubElement(val_center, "vert").text = f"{vert:.6f}"
        
        current_frame += dur

    ET.SubElement(sequence, "duration").text = str(current_frame)

    # --- Add Audio Track (Master.mp3) ---
    audio_filename = "Master.mp3"
    audio_filepath = os.path.join(PROJECT_ROOT, "Music", audio_filename)
    audio_url = "file://localhost" + encode_path(audio_filepath)
    
    # 1. Add Audio Master Clip to bin
    a_fid = "master_audio"
    a_clip_el = ET.SubElement(bin_children, "clip", id=f"masterclip-{a_fid}")
    ET.SubElement(a_clip_el, "masterclipid").text = f"masterclip-{a_fid}"
    ET.SubElement(a_clip_el, "ismasterclip").text = "TRUE"
    ET.SubElement(a_clip_el, "duration").text = str(current_frame)
    
    a_clip_rate = ET.SubElement(a_clip_el, "rate")
    ET.SubElement(a_clip_rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(a_clip_rate, "ntsc").text = NTSC
    
    ET.SubElement(a_clip_el, "in").text = "0"
    ET.SubElement(a_clip_el, "out").text = str(current_frame)
    ET.SubElement(a_clip_el, "name").text = audio_filename
    
    a_clip_media = ET.SubElement(a_clip_el, "media")
    a_clip_audio = ET.SubElement(a_clip_media, "audio")
    a_clip_track = ET.SubElement(a_clip_audio, "track")
    
    a_clipitem = ET.SubElement(a_clip_track, "clipitem", id=f"clipitem-master-{a_fid}")
    ET.SubElement(a_clipitem, "masterclipid").text = f"masterclip-{a_fid}"
    ET.SubElement(a_clipitem, "name").text = audio_filename
    
    a_ci_rate = ET.SubElement(a_clipitem, "rate")
    ET.SubElement(a_ci_rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(a_ci_rate, "ntsc").text = NTSC
    
    a_file_el = ET.SubElement(a_clipitem, "file", id=f"file-{a_fid}")
    ET.SubElement(a_file_el, "name").text = audio_filename
    ET.SubElement(a_file_el, "pathurl").text = audio_url
    
    a_file_rate = ET.SubElement(a_file_el, "rate")
    ET.SubElement(a_file_rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(a_file_rate, "ntsc").text = NTSC
    
    ET.SubElement(a_file_el, "duration").text = str(current_frame)
    a_timecode = ET.SubElement(a_file_el, "timecode")
    a_tc_rate = ET.SubElement(a_timecode, "rate")
    ET.SubElement(a_tc_rate, "timebase").text = str(TIMEBASE)
    ET.SubElement(a_tc_rate, "ntsc").text = NTSC
    ET.SubElement(a_timecode, "string").text = "00:00:00:00"
    ET.SubElement(a_timecode, "frame").text = "0"
    ET.SubElement(a_timecode, "displayformat").text = "NDF"
    
    a_file_media = ET.SubElement(a_file_el, "media")
    a_file_audio = ET.SubElement(a_file_media, "audio")
    a_f_sc = ET.SubElement(a_file_audio, "samplecharacteristics")
    ET.SubElement(a_f_sc, "depth").text = "16"
    ET.SubElement(a_f_sc, "samplerate").text = "48000"
    ET.SubElement(a_file_audio, "channelcount").text = "2"
    
    # 2. Add Audio Tracks to Sequence
    audio = ET.SubElement(media, "audio")
    ET.SubElement(audio, "numOutputChannels").text = "2"
    audio_format = ET.SubElement(audio, "format")
    audio_sc = ET.SubElement(audio_format, "samplecharacteristics")
    ET.SubElement(audio_sc, "depth").text = "16"
    ET.SubElement(audio_sc, "samplerate").text = "48000"
    
    a_track1 = ET.SubElement(audio, "track")
    a_track2 = ET.SubElement(audio, "track")
    
    for t_idx, a_track in enumerate([a_track1, a_track2]):
        clipitem = ET.SubElement(a_track, "clipitem", id=f"seq_audio_clip_{t_idx}")
        ET.SubElement(clipitem, "name").text = audio_filename
        ET.SubElement(clipitem, "duration").text = str(current_frame)
        
        rate_el = ET.SubElement(clipitem, "rate")
        ET.SubElement(rate_el, "timebase").text = str(TIMEBASE)
        ET.SubElement(rate_el, "ntsc").text = NTSC
        
        ET.SubElement(clipitem, "start").text = "0"
        ET.SubElement(clipitem, "end").text = str(current_frame)
        ET.SubElement(clipitem, "in").text = "0"
        ET.SubElement(clipitem, "out").text = str(current_frame)
        
        ET.SubElement(clipitem, "file").set("id", f"file-{a_fid}")
            
        sourcetrack = ET.SubElement(clipitem, "sourcetrack")
        ET.SubElement(sourcetrack, "mediatype").text = "audio"
        ET.SubElement(sourcetrack, "trackindex").text = str(t_idx + 1)

    
    xmlstr = minidom.parseString(ET.tostring(xmeml)).toprettyxml(indent="  ")
    xmlstr = xmlstr.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>')
    
    # We must post-process the string because minidom replaces our literal &amp; with &amp;amp;
    xmlstr = xmlstr.replace("&amp;amp;", "&amp;")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_xml_path = os.path.join(XML_DIR, f"Josh_Master_v{timestamp}.xml")
    
    with open(out_xml_path, "w", encoding="utf-8") as f:
        f.write(xmlstr)
        
    print(f"Successfully generated {out_xml_path} with {photo_idx} photos.")

if __name__ == "__main__":
    build_xml()
