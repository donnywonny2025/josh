import os
import xml.etree.ElementTree as ET
from urllib.parse import quote
import copy

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
TEMPLATE_XML = "/Volumes/Extreme SSD/Parker Hannifin/XML_Exports/Parker_Hannifin_v47_20260618_210923.xml"
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Josh_Memorial_v16_FIXED.xml")

def s2f(sec):
    return round(sec * 24000.0 / 1001.0)

def build_full_dom():
    print(f"Parsing template: {TEMPLATE_XML}")
    tree = ET.parse(TEMPLATE_XML)
    root = tree.getroot()
    
    main_bin = root.find("bin")
    main_bin.find("name").text = "Josh Memorial v16 (Fixed)"
    main_bin_children = main_bin.find("children")
    
    footage_bin = None
    seq_template = None
    
    for child in main_bin_children:
        if child.tag == "bin" and child.find("name").text == "Footage":
            footage_bin = child
        elif child.tag == "sequence":
            if seq_template is None:
                seq_template = copy.deepcopy(child)
            main_bin_children.remove(child)
            
    footage_children = footage_bin.find("children")
    clips = footage_children.findall("clip")
    clip_template = copy.deepcopy(clips[0])
    for c in clips:
        footage_children.remove(c)
        
    media = seq_template.find("media")
    video = media.find("video")
    audio = media.find("audio")
    
    v_track_template = copy.deepcopy(video.findall("track")[0])
    a_track_template = copy.deepcopy(audio.findall("track")[0])
    
    v_clipitem_template = copy.deepcopy(v_track_template.find("clipitem"))
    a_clipitem_template = copy.deepcopy(a_track_template.find("clipitem"))
    
    for track in video.findall("track"): video.remove(track)
    for track in audio.findall("track"): audio.remove(track)
        
    # --- ADD FILES TO FOOTAGE BIN ---
    
    # 1. Video
    vid_clip = copy.deepcopy(clip_template)
    vid_clip.set("id", "masterclip-vid")
    vid_clip.find("name").text = "video1.mp4"
    
    # Master clip's file is in video track
    vid_file = vid_clip.find("media").find("video").find("track").find("clipitem").find("file")
    vid_file.set("id", "file-vid")
    vid_file.find("name").text = "video1.mp4"
    vid_file.find("pathurl").text = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/video1.mp4')}"
    
    # Fix master clip's audio track reference
    vid_clip_audio_file = vid_clip.find("media").find("audio").find("track").find("clipitem").find("file")
    if vid_clip_audio_file is not None:
        vid_clip_audio_file.set("id", "file-vid")
        
    footage_children.append(vid_clip)
    
    # 2. Image
    img_clip = copy.deepcopy(clip_template)
    img_clip.set("id", "masterclip-img")
    img_clip.find("name").text = "image1.jpg"
    
    ET.SubElement(img_clip, "stillframe").text = "TRUE"
    ET.SubElement(img_clip, "duration").text = "86400"
    
    img_file = img_clip.find("media").find("video").find("track").find("clipitem").find("file")
    img_file.set("id", "file-img")
    img_file.find("name").text = "image1.jpg"
    img_file.find("pathurl").text = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/image1.jpg')}"
    ET.SubElement(img_file, "duration").text = "86400"
    
    # Remove audio from file's media characteristics
    if img_file.find("media") is not None and img_file.find("media").find("audio") is not None:
        img_file.find("media").remove(img_file.find("media").find("audio"))
        
    # Remove audio from master clip's media (since it's a photo)
    if img_clip.find("media").find("audio") is not None:
        img_clip.find("media").remove(img_clip.find("media").find("audio"))
        
    footage_children.append(img_clip)
    
    # 3. Audio
    aud_clip = copy.deepcopy(clip_template)
    aud_clip.set("id", "masterclip-aud")
    aud_clip.find("name").text = "audio1.mp3"
    
    # Move the file from the video track to the audio track
    aud_file = aud_clip.find("media").find("video").find("track").find("clipitem").find("file")
    aud_file.set("id", "file-aud")
    aud_file.find("name").text = "audio1.mp3"
    aud_file.find("pathurl").text = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/audio1.mp3')}"
    
    # Inject file into audio track clipitem
    aud_clip_audio_ci = aud_clip.find("media").find("audio").find("track").find("clipitem")
    for f in aud_clip_audio_ci.findall("file"): aud_clip_audio_ci.remove(f)
    aud_clip_audio_ci.append(aud_file)
    
    # Remove video from file's media characteristics
    if aud_file.find("media") is not None and aud_file.find("media").find("video") is not None:
        aud_file.find("media").remove(aud_file.find("media").find("video"))
        
    # Remove video from master clip
    if aud_clip.find("media").find("video") is not None:
        aud_clip.find("media").remove(aud_clip.find("media").find("video"))
        
    footage_children.append(aud_clip)
    
    # --- BUILD TIMELINE ---
    
    vid_dur = 360
    img_dur = s2f(6.0) # 144
    seq_dur = vid_dur + img_dur # 504
    
    seq_template.find("name").text = "Test V16 (Fixed IDs)"
    seq_template.find("duration").text = str(seq_dur)
    
    # V1: Video
    v1 = copy.deepcopy(v_track_template)
    for ci in v1.findall("clipitem"): v1.remove(ci)
    
    c_vid = copy.deepcopy(v_clipitem_template)
    c_vid.set("id", "clip-v1-vid")
    c_vid.find("name").text = "video1.mp4"
    c_vid.find("duration").text = str(vid_dur)
    c_vid.find("start").text = "0"
    c_vid.find("end").text = str(vid_dur)
    c_vid.find("in").text = "0"
    c_vid.find("out").text = str(vid_dur)
    c_vid.find("file").set("id", "file-vid")
    v1.append(c_vid)
    
    # V1: Image
    c_img = copy.deepcopy(v_clipitem_template)
    c_img.set("id", "clip-v1-img")
    c_img.find("name").text = "image1.jpg"
    c_img.find("duration").text = "86400"
    c_img.find("start").text = str(vid_dur)
    c_img.find("end").text = str(seq_dur)
    c_img.find("in").text = "0"
    c_img.find("out").text = str(img_dur)
    ET.SubElement(c_img, "stillframe").text = "TRUE"
    c_img.find("file").set("id", "file-img")
    v1.append(c_img)
    video.append(v1)
    
    # A1: Video Audio (L)
    a1 = copy.deepcopy(a_track_template)
    for ci in a1.findall("clipitem"): a1.remove(ci)
    ca1 = copy.deepcopy(a_clipitem_template)
    ca1.set("id", "clip-a1-vid")
    ca1.find("name").text = "video1.mp4"
    ca1.find("duration").text = str(vid_dur)
    ca1.find("start").text = "0"
    ca1.find("end").text = str(vid_dur)
    ca1.find("in").text = "0"
    ca1.find("out").text = str(vid_dur)
    ca1.find("file").set("id", "file-vid")
    a1.append(ca1)
    audio.append(a1)
    
    # A2: Video Audio (R)
    a2 = copy.deepcopy(a_track_template)
    for ci in a2.findall("clipitem"): a2.remove(ci)
    ca2 = copy.deepcopy(a_clipitem_template)
    ca2.set("id", "clip-a2-vid")
    ca2.find("name").text = "video1.mp4"
    ca2.find("duration").text = str(vid_dur)
    ca2.find("start").text = "0"
    ca2.find("end").text = str(vid_dur)
    ca2.find("in").text = "0"
    ca2.find("out").text = str(vid_dur)
    ca2.find("file").set("id", "file-vid")
    a2.append(ca2)
    audio.append(a2)
    
    # A3: Music (L)
    a3 = copy.deepcopy(a_track_template)
    for ci in a3.findall("clipitem"): a3.remove(ci)
    ca3 = copy.deepcopy(a_clipitem_template)
    ca3.set("id", "clip-a3-aud")
    ca3.find("name").text = "audio1.mp3"
    ca3.find("duration").text = str(seq_dur)
    ca3.find("start").text = "0"
    ca3.find("end").text = str(seq_dur)
    ca3.find("in").text = "0"
    ca3.find("out").text = str(seq_dur)
    ca3.find("file").set("id", "file-aud")
    a3.append(ca3)
    audio.append(a3)
    
    # A4: Music (R)
    a4 = copy.deepcopy(a_track_template)
    for ci in a4.findall("clipitem"): a4.remove(ci)
    ca4 = copy.deepcopy(a_clipitem_template)
    ca4.set("id", "clip-a4-aud")
    ca4.find("name").text = "audio1.mp3"
    ca4.find("duration").text = str(seq_dur)
    ca4.find("start").text = "0"
    ca4.find("end").text = str(seq_dur)
    ca4.find("in").text = "0"
    ca4.find("out").text = str(seq_dur)
    ca4.find("file").set("id", "file-aud")
    a4.append(ca4)
    audio.append(a4)
    
    main_bin_children.append(seq_template)
    
    os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(root, encoding="unicode")
    
    with open(OUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"Success! Built DOM XML: {OUT_XML}")

if __name__ == "__main__":
    build_full_dom()
