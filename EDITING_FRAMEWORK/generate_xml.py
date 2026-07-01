import json
import os
from xml.sax.saxutils import escape

PACING_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/timeline_pacing_map.json'
FRAMING_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/photo_framing_map.json'
OUTPUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/memorial_sequence.xml'

def s2f(seconds, fps=23.976):
    return int(round(seconds * fps))

def generate_xml():
    if not os.path.exists(PACING_FILE):
        print("Pacing map missing!")
        return
        
    with open(PACING_FILE, 'r') as f:
        pacing = json.load(f)
        
    framing = {}
    if os.path.exists(FRAMING_FILE):
        with open(FRAMING_FILE, 'r') as f:
            framing = json.load(f)
            
    fps = pacing['global_settings']['fps']
    sequence = pacing['sequence']
    
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml.append('<!DOCTYPE xmeml>')
    xml.append('<xmeml version="4">')
    xml.append('  <bin>')
    xml.append('    <name>Josh Memorial XML</name>')
    xml.append('    <children>')
    
    # ---------------------------------------------------------
    # PARKER HANNIFIN RULE 1: Master File Definitions in Bin
    # ---------------------------------------------------------
    xml.append('      <bin>')
    xml.append('        <name>Footage</name>')
    xml.append('        <children>')
    
    file_id_map = {}
    
    for i, clip in enumerate(sequence):
        file_id = f"file-{i}"
        file_id_map[clip['file']] = file_id
        
        path_url = "file://localhost" + escape(clip['path'].replace(' ', '%20'))
        
        # We need a nominal duration for the file definition. Just use 1 hour.
        source_dur_frames = s2f(3600, fps) 
        
        xml.append(f'          <clip id="clip-{i}">')
        xml.append('            <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>')
        xml.append(f'            <name>{escape(clip["file"])}</name>')
        xml.append('            <media>')
        xml.append('              <video>')
        xml.append('                <track>')
        xml.append('                  <clipitem>')
        xml.append(f'                    <file id="{file_id}">')
        xml.append(f'                      <name>{escape(clip["file"])}</name>')
        xml.append(f'                      <duration>{source_dur_frames}</duration>')
        xml.append('                      <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>')
        xml.append(f'                      <pathurl>{path_url}</pathurl>')
        xml.append('                      <media>')
        xml.append('                        <video>')
        xml.append('                          <samplecharacteristics>')
        xml.append('                            <width>1920</width>')
        xml.append('                            <height>1080</height>')
        xml.append('                          </samplecharacteristics>')
        xml.append('                        </video>')
        xml.append('                      </media>')
        xml.append('                    </file>')
        xml.append('                  </clipitem>')
        xml.append('                </track>')
        xml.append('              </video>')
        xml.append('            </media>')
        xml.append('          </clip>')
        
    xml.append('        </children>')
    xml.append('      </bin>')
    
    # ---------------------------------------------------------
    # SEQUENCE DEFINITION
    # ---------------------------------------------------------
    xml.append('      <sequence>')
    xml.append('        <name>Josh Memorial Timeline</name>')
    xml.append('        <duration>86400</duration>')
    xml.append('        <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>')
    xml.append('        <media>')
    xml.append('          <video>')
    xml.append('            <format>')
    xml.append('              <samplecharacteristics>')
    xml.append('                <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>')
    xml.append('                <width>1920</width>')
    xml.append('                <height>1080</height>')
    xml.append('                <pixelaspectratio>square</pixelaspectratio>')
    xml.append('              </samplecharacteristics>')
    xml.append('            </format>')
    
    # Track 1
    xml.append('            <track>')
    
    for i, clip in enumerate(sequence):
        f_in = s2f(clip['timeline_in_s'], fps)
        f_out = s2f(clip['timeline_out_s'], fps)
        
        # Just use nominal source IN/OUT
        src_in = 0
        src_out = f_out - f_in
        
        file_id = file_id_map[clip['file']]
        
        # ---------------------------------------------------------
        # ALGORITHMIC FRAMING MATH
        # ---------------------------------------------------------
        target_h = 0.0
        target_v = 0.0
        
        frame_data = framing.get(clip['file'], {})
        if frame_data.get('center_of_mass'):
            # Convert pixel coords to -0.5 to 0.5 space
            x, y = frame_data['center_of_mass']
            w, h = frame_data['width'], frame_data['height']
            
            # If face is at left (x=0), horiz is -0.5. To push TO it, we need to slide image right, so horiz becomes positive
            normalized_x = (x / w) - 0.5
            normalized_y = (y / h) - 0.5
            
            # The push factor (don't push all the way to edge, just nudge)
            target_h = -normalized_x * 10  # FCP7 Center coordinates are tricky, sometimes it\'s mapped differently. 
            target_v = -normalized_y * 10
            
        xml.append('              <clipitem>')
        xml.append(f'                <name>{escape(clip["file"])}</name>')
        xml.append(f'                <start>{f_in}</start>')
        xml.append(f'                <end>{f_out}</end>')
        xml.append(f'                <in>{src_in}</in>')
        xml.append(f'                <out>{src_out}</out>')
        
        # PARKER HANNIFIN RULE 2: Clean file reference, NO metadata
        xml.append(f'                <file id="{file_id}"/>')
        
        # Apply Ken Burns
        xml.append('                <filter>')
        xml.append('                  <effect>')
        xml.append('                    <name>Basic Motion</name>')
        xml.append('                    <effectid>basic</effectid>')
        xml.append('                    <effectcategory>motion</effectcategory>')
        xml.append('                    <effecttype>motion</effecttype>')
        xml.append('                    <mediatype>video</mediatype>')
        
        # SCALE
        xml.append('                    <parameter>')
        xml.append('                      <parameterid>scale</parameterid>')
        xml.append('                      <name>Scale</name>')
        xml.append('                      <keyframe>')
        xml.append('                        <when>0</when>')
        xml.append('                        <value>100</value>')
        xml.append('                      </keyframe>')
        xml.append('                      <keyframe>')
        xml.append(f'                        <when>{src_out}</when>')
        xml.append('                        <value>115</value>')
        xml.append('                      </keyframe>')
        xml.append('                    </parameter>')
        
        # CENTER
        xml.append('                    <parameter>')
        xml.append('                      <parameterid>center</parameterid>')
        xml.append('                      <name>Center</name>')
        xml.append('                      <keyframe>')
        xml.append('                        <when>0</when>')
        xml.append('                        <value><horiz>0</horiz><vert>0</vert></value>')
        xml.append('                      </keyframe>')
        xml.append('                      <keyframe>')
        xml.append(f'                        <when>{src_out}</when>')
        xml.append(f'                        <value><horiz>{round(target_h, 3)}</horiz><vert>{round(target_v, 3)}</vert></value>')
        xml.append('                      </keyframe>')
        xml.append('                    </parameter>')
        
        xml.append('                  </effect>')
        xml.append('                </filter>')
        xml.append('              </clipitem>')
        
    xml.append('            </track>')
    xml.append('          </video>')
    xml.append('        </media>')
    xml.append('      </sequence>')
    
    xml.append('    </children>')
    xml.append('  </bin>')
    xml.append('</xmeml>')
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(xml))
        
    print(f"Generated {OUTPUT_FILE} using Parker Hannifin minimalist rules!")

if __name__ == '__main__':
    generate_xml()
