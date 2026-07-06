import os
import xml.etree.ElementTree as ET
from urllib.parse import quote
import copy

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
TEMPLATE_XML = "/Volumes/Extreme SSD/Parker Hannifin/EDITING_FRAMEWORK/Parker_Hannifin_Open_House.xml"
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Josh_Memorial_v13_DOM.xml")

def build_from_template():
    # 1. Parse the template
    print(f"Parsing template: {TEMPLATE_XML}")
    tree = ET.parse(TEMPLATE_XML)
    root = tree.getroot()
    
    # 2. Find the Footage bin and Sequences bin
    project = root.find("project")
    project.find("name").text = "Josh Memorial V13 DOM"
    
    project_children = project.find("children")
    
    footage_bin = None
    sequences_bin = None
    
    for bin_elem in project_children.findall("bin"):
        name = bin_elem.find("name").text
        if name == "Footage":
            footage_bin = bin_elem
        elif name == "Sequences":
            sequences_bin = bin_elem
            
    if not footage_bin or not sequences_bin:
        print("Error: Could not find Footage or Sequences bin")
        return
        
    # 3. Extract a master clip template and clear the bin
    footage_children = footage_bin.find("children")
    clips = footage_children.findall("clip")
    
    # Clone the first clip (C0003.MP4)
    clip_template = copy.deepcopy(clips[0])
    
    # Clear all clips from the footage bin
    for c in clips:
        footage_children.remove(c)
        
    # 4. Extract a master sequence template and clear the bin
    seq_children = sequences_bin.find("children")
    sequences = seq_children.findall("sequence")
    
    # Clone the first sequence (B-Roll Stringout)
    seq_template = copy.deepcopy(sequences[0])
    
    # Clear all sequences from the sequences bin
    for s in sequences:
        seq_children.remove(s)
        
    # 5. Extract a video and audio track template from the sequence
    media = seq_template.find("media")
    video = media.find("video")
    audio = media.find("audio")
    
    v_track = video.find("track")
    a_track = audio.find("track") # It has one track in sequence 1
    
    # Clone clipitems
    v_clipitem_template = copy.deepcopy(v_track.find("clipitem"))
    a_clipitem_template = copy.deepcopy(a_track.find("clipitem"))
    
    # Clear tracks
    for track in video.findall("track"):
        for ci in track.findall("clipitem"):
            track.remove(ci)
            
    for track in audio.findall("track"):
        for ci in track.findall("clipitem"):
            track.remove(ci)
            
    # Modify Sequence Metadata
    seq_template.find("name").text = "Test V13 DOM Sequence"
    seq_template.find("duration").text = "360" # We will use exactly 15 seconds
    
    # 6. Inject our specific video
    # Build Master Clip
    my_clip = copy.deepcopy(clip_template)
    my_clip.set("id", "masterclip-file-1")
    my_clip.find("name").text = "video1.mp4"
    my_file = my_clip.find("file")
    my_file.set("id", "file-1")
    my_file.find("name").text = "video1.mp4"
    # IMPORTANT: The Parker Hannifin XML didn't have a <duration> on this file block. We'll leave it as is.
    video_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/video1.mp4')}"
    my_file.find("pathurl").text = video_path
    footage_children.append(my_clip)
    
    # Build Video Clipitem
    my_vclip = copy.deepcopy(v_clipitem_template)
    my_vclip.set("id", "clip-1")
    my_vclip.find("name").text = "video1.mp4"
    my_vclip.find("duration").text = "360"
    my_vclip.find("start").text = "0"
    my_vclip.find("end").text = "360"
    my_vclip.find("in").text = "0"
    my_vclip.find("out").text = "360"
    my_vclip.find("file").set("id", "file-1")
    v_track.append(my_vclip)
    
    # Build Audio Clipitem
    my_aclip = copy.deepcopy(a_clipitem_template)
    my_aclip.set("id", "clip-2")
    my_aclip.find("name").text = "video1.mp4"
    my_aclip.find("duration").text = "360"
    my_aclip.find("start").text = "0"
    my_aclip.find("end").text = "360"
    my_aclip.find("in").text = "0"
    my_aclip.find("out").text = "360"
    my_aclip.find("file").set("id", "file-1")
    a_track.append(my_aclip)
    
    # Re-attach sequence
    seq_children.append(seq_template)
    
    # 7. Write output
    os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
    
    # Write the XML declaration and DOCTYPE manually since ElementTree strips DOCTYPE
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n'
    xml_str += ET.tostring(root, encoding="unicode")
    
    with open(OUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"Success! Built DOM XML: {OUT_XML}")

if __name__ == "__main__":
    build_from_template()
