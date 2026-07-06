import os
import glob
import subprocess
from urllib.parse import quote

# Configuration
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
PHOTOS_DIR = os.path.join(PROJECT_ROOT, "PHOTOS", "RAW_IMPORTS", "Baby & toddler Josh")
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Baby_Toddler_v1.xml")

TB = 24
STILL_DURATION = 86400 # Default duration for still images
CLIP_DURATION = 120 # 5 seconds per slide at 24fps

def get_image_dimensions(filepath):
    """Uses ffprobe to get image width and height."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", filepath
    ]
    try:
        output = subprocess.check_output(cmd, text=True).strip()
        if output:
            parts = output.split(",")
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
    except Exception as e:
        print(f"Error probing {filepath}: {e}")
    return 1920, 1080 # Fallback

def build_photo_sequence():
    # Find all images
    valid_exts = {".jpg", ".jpeg", ".png"}
    files = []
    for f in os.listdir(PHOTOS_DIR):
        if os.path.splitext(f.lower())[1] in valid_exts and not f.startswith("."):
            files.append(os.path.join(PHOTOS_DIR, f))
    
    files.sort() # Ensure consistent order
    
    print(f"Found {len(files)} photos.")

    master_clips_xml = ""
    seq_clipitems_xml = ""
    
    current_start = 0

    for i, filepath in enumerate(files):
        fid = i + 1
        filename = os.path.basename(filepath)
        w, h = get_image_dimensions(filepath)
        
        url = "file://localhost" + quote(filepath)
        
        # 1. Generate Master Clip (Strict Premiere Native Nesting)
        master_clip = f'''        <clip id="masterclip-{fid}">
          <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
          <name>{filename}</name>
          <media>
            <video>
              <track>
                <clipitem id="clipitem-master-{fid}">
                  <file id="file-{fid}">
                    <name>{filename}</name>
                    <pathurl>{url}</pathurl>
                    <duration>{STILL_DURATION}</duration>
                    <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                    <media>
                        <video><samplecharacteristics>
                            <width>{w}</width><height>{h}</height>
                        </samplecharacteristics></video>
                    </media>
                  </file>
                </clipitem>
              </track>
            </video>
          </media>
        </clip>
'''
        master_clips_xml += master_clip
        
        # 2. Generate Sequence Clipitem
        end_f = current_start + CLIP_DURATION
        seq_clip = f'''          <clipitem id="clip-{fid}">
            <name>{filename}</name>
            <duration>{STILL_DURATION}</duration>
            <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
            <start>{current_start}</start><end>{end_f}</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>{CLIP_DURATION}</out>
            <file id="file-{fid}"/>
          </clipitem>
'''
        seq_clipitems_xml += seq_clip
        current_start = end_f

    # 3. Assemble full XML
    total_duration = current_start
    
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Baby &amp; Toddler Photo Sequence</name>
    <children>
      <bin>
        <name>Photos</name>
        <children>
{master_clips_xml}        </children>
      </bin>
      <bin>
        <name>Sequences</name>
        <children>
          <sequence id="seq-1">
            <name>Baby &amp; Toddler - 19 Slides</name>
            <duration>{total_duration}</duration>
            <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
            <timecode>
                <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                <string>00:00:00:00</string>
                <frame>0</frame>
                <displayformat>NDF</displayformat>
            </timecode>
            <media>
              <video>
                <format><samplecharacteristics>
                  <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                  <width>3840</width><height>2160</height>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
{seq_clipitems_xml}                </track>
              </video>
              <audio>
                <numOutputAudioTracks>2</numOutputAudioTracks>
                <format><samplecharacteristics>
                  <depth>16</depth><samplerate>48000</samplerate>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>1</outputchannelindex>
                </track>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>2</outputchannelindex>
                </track>
              </audio>
            </media>
          </sequence>
        </children>
      </bin>
    </children>
  </project>
</xmeml>
'''

    os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
    with open(OUT_XML, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
        
    print(f"Success! Generated XML: {OUT_XML}")

if __name__ == "__main__":
    build_photo_sequence()
