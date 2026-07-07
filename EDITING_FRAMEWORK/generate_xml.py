import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_xml():
    with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json') as f:
        tl = json.load(f)
        
    xmeml = ET.Element('xmeml', version='4')
    project = ET.SubElement(xmeml, 'project')
    project_name = ET.SubElement(project, 'name')
    project_name.text = 'Josh Memorial'
    
    children = ET.SubElement(project, 'children')
    
    # Sequence
    sequence = ET.SubElement(children, 'sequence', id='sequence-1')
    seq_name = ET.SubElement(sequence, 'name')
    seq_name.text = 'Beat Mapped Timeline'
    
    duration = ET.SubElement(sequence, 'duration')
    rate = ET.SubElement(sequence, 'rate')
    ET.SubElement(rate, 'timebase').text = '30'
    ET.SubElement(rate, 'ntsc').text = 'TRUE'
    
    media = ET.SubElement(sequence, 'media')
    video = ET.SubElement(media, 'video')
    
    format = ET.SubElement(video, 'format')
    samplecharacteristics = ET.SubElement(format, 'samplecharacteristics')
    rate_fmt = ET.SubElement(samplecharacteristics, 'rate')
    ET.SubElement(rate_fmt, 'timebase').text = '30'
    ET.SubElement(rate_fmt, 'ntsc').text = 'TRUE'
    ET.SubElement(samplecharacteristics, 'width').text = '1920'
    ET.SubElement(samplecharacteristics, 'height').text = '1080'
    ET.SubElement(samplecharacteristics, 'pixelaspectratio').text = 'square'
    
    track = ET.SubElement(video, 'track')
    
    file_registry = {}
    files_defined = []
    
    total_frames = 0
    current_frame = 0
    
    clip_idx = 1
    file_idx = 1
    
    for slide in tl['slides']:
        if slide.get('isPlaceholder'):
            continue
            
        dur_frames = slide.get('duration_frames', 30)
        
        start = current_frame
        end = start + dur_frames
        
        if slide.get('isCard'):
            # Just create a placeholder or title clip
            # For simplicity we'll just skip cards or make them offline
            current_frame = end
            continue
            
        filename = slide.get('file', 'UNKNOWN.JPG')
        file_path = f"file://localhost/Volumes/Extreme%20SSD/JOSH/Photos/{filename.replace(' ', '%20')}"
        
        # Has this file been registered?
        if filename not in file_registry:
            file_registry[filename] = file_idx
            file_idx += 1
            
        fid = f"file-{file_registry[filename]}"
        
        clipitem = ET.SubElement(track, 'clipitem', id=f"clip-{clip_idx}")
        clip_idx += 1
        
        ET.SubElement(clipitem, 'name').text = filename
        ET.SubElement(clipitem, 'enabled').text = 'TRUE'
        ET.SubElement(clipitem, 'duration').text = '15000'
        
        crate = ET.SubElement(clipitem, 'rate')
        ET.SubElement(crate, 'timebase').text = '30'
        ET.SubElement(crate, 'ntsc').text = 'TRUE'
        
        ET.SubElement(clipitem, 'start').text = str(start)
        ET.SubElement(clipitem, 'end').text = str(end)
        
        ET.SubElement(clipitem, 'in').text = '0'
        ET.SubElement(clipitem, 'out').text = str(dur_frames)
        
        file_node = ET.SubElement(clipitem, 'file', id=fid)
        # Only define the file the first time it is used
        if fid not in files_defined:
            files_defined.append(fid)
            ET.SubElement(file_node, 'name').text = filename
            ET.SubElement(file_node, 'pathurl').text = file_path
            frate = ET.SubElement(file_node, 'rate')
            ET.SubElement(frate, 'timebase').text = '30'
            ET.SubElement(frate, 'ntsc').text = 'TRUE'
            ET.SubElement(file_node, 'duration').text = '15000'
            fmedia = ET.SubElement(file_node, 'media')
            fvideo = ET.SubElement(fmedia, 'video')
            ET.SubElement(fvideo, 'duration').text = '15000'
        
        current_frame = end
        total_frames = max(total_frames, end)
        
    duration.text = str(total_frames)
    
    # Prettify and save
    xmlstr = minidom.parseString(ET.tostring(xmeml)).toprettyxml(indent="  ")
    with open('/Volumes/Extreme SSD/JOSH/Exports/Joshy_BeatMapped.xml', 'w') as f:
        f.write(xmlstr)
        
    print(f"Generated XML with {clip_idx-1} clips!")

if __name__ == '__main__':
    generate_xml()
