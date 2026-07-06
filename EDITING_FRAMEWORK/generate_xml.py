import os
import json
import subprocess
from urllib.parse import quote

# ---------------------------------------------------------
# CONSTANTS & SETUP
# ---------------------------------------------------------
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")
SEQUENCES_DIR = os.path.join(PROJECT_ROOT, "EDITING_FRAMEWORK", "sequences")

# Sequence properties
TIMEBASE = 24
NTSC = "TRUE"
FPS = 24.0
WIDTH, HEIGHT = 1920, 1080
AUDIO_RATE = 48000
AUDIO_DEPTH = 16
STILL_MASTER_DURATION = 86400 # 1 hour, to allow any slide duration

def s2f(seconds):
    """Convert seconds to frames."""
    return int(round(seconds * FPS))

def get_next_xml_filename(base_name="Josh_Memorial"):
    """Auto-increments the XML version number so we never overwrite."""
    import glob
    existing_files = glob.glob(os.path.join(XML_DIR, f"{base_name}_v*.xml"))
    max_v = 0
    for f in existing_files:
        try:
            v_str = os.path.basename(f).replace(f"{base_name}_v", "").replace(".xml", "")
            max_v = max(max_v, int(v_str))
        except ValueError:
            pass
    return os.path.join(XML_DIR, f"{base_name}_v{max_v + 1}.xml")

def encode_path(p):
    """URL encode spaces and XML escape ampersands, mimicking Premiere exactly."""
    return p.replace(" ", "%20").replace("&", "&amp;")

def get_image_dimensions(filepath):
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
    except Exception:
        pass
    return 1920, 1080

def generate_xml(sequence_id):
    seq_path = os.path.join(SEQUENCES_DIR, f"{sequence_id}.json")
    if not os.path.exists(seq_path):
        print(f"Sequence not found: {seq_path}")
        return

    with open(seq_path, 'r') as f:
        seq = json.load(f)

    # 1. Grab Audio
    audio_filename = seq.get("song", {}).get("filename")
    audio_path = os.path.join(PROJECT_ROOT, "Music", audio_filename)
    audio_url = "file://localhost" + encode_path(audio_path)
    
    # 2. Master Clips XML
    master_clips_xml = ""
    file_idx = 1
    
    # Add Audio Master Clip
    master_clips_xml += f'''        <clip id="masterclip-a">
          <ismasterclip>TRUE</ismasterclip>
          <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
          <name>{audio_filename}</name>
          <media>
            <audio>
              <track>
                <clipitem id="clipitem-master-a">
                  <masterclipid>masterclip-a</masterclipid>
                  <name>{audio_filename}</name>
                  <file id="file-a">
                    <name>{audio_filename}</name>
                    <duration>{s2f(10000)}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <pathurl>{audio_url}</pathurl>
                    <media>
                        <audio><samplecharacteristics>
                            <depth>{AUDIO_DEPTH}</depth><samplerate>{AUDIO_RATE}</samplerate>
                        </samplecharacteristics><channelcount>2</channelcount></audio>
                    </media>
                  </file>
                </clipitem>
              </track>
            </audio>
          </media>
        </clip>\n'''

    # Sequence Video Track string
    seq_vid_xml = ""
    current_start = 0

    # Photos
    for idx, slide in enumerate(seq.get("slides", [])):
        fid = idx + 1
        filename = slide["file"]
        folder = slide["folder"]
        filepath = os.path.join(PROJECT_ROOT, "PHOTOS", "RAW_IMPORTS", folder, filename)
        
        w, h = get_image_dimensions(filepath)
        url = "file://localhost" + encode_path(filepath)
        
        duration_sec = slide.get("duration_sec", seq.get("default_duration_sec", 6.0))
        duration_frames = s2f(duration_sec)
        
        # --- SCALE & ALIGNMENT LOGIC ---
        scale_x = WIDTH / float(w)
        scale_y = HEIGHT / float(h)
        scale_factor = max(scale_x, scale_y)
        target_scale = scale_factor * 100.0
        
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
        
        filter_xml = f'''            <filter>
              <effect>
                <name>Basic Motion</name>
                <effectid>basic</effectid>
                <effectcategory>motion</effectcategory>
                <effecttype>motion</effecttype>
                <mediatype>video</mediatype>
                <parameter>
                  <parameterid>scale</parameterid>
                  <name>Scale</name>
                  <value>{target_scale:.2f}</value>
                </parameter>
                <parameter>
                  <parameterid>center</parameterid>
                  <name>Center</name>
                  <value>
                    <horiz>{horiz:.6f}</horiz>
                    <vert>{vert:.6f}</vert>
                  </value>
                </parameter>
              </effect>
            </filter>'''
        # -------------------------------
        
        master_clips_xml += f'''        <clip id="masterclip-{fid}" explodedTracks="true">
          <masterclipid>masterclip-{fid}</masterclipid>
          <ismasterclip>TRUE</ismasterclip>
          <duration>{STILL_MASTER_DURATION}</duration>
          <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
          <in>0</in>
          <out>{STILL_MASTER_DURATION - 1}</out>
          <name>{filename}</name>
          <media>
            <video>
              <track>
                <clipitem id="clipitem-master-{fid}">
                  <masterclipid>masterclip-{fid}</masterclipid>
                  <name>{filename}</name>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <alphatype>none</alphatype>
                  <pixelaspectratio>square</pixelaspectratio>
                  <anamorphic>FALSE</anamorphic>
                  <file id="file-{fid}">
                    <name>{filename}</name>
                    <pathurl>{url}</pathurl>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <timecode>
                        <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                        <string>00:00:00:00</string>
                        <frame>0</frame>
                        <displayformat>NDF</displayformat>
                    </timecode>
                    <media>
                        <video>
                            <samplecharacteristics>
                                <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                                <width>{w}</width><height>{h}</height>
                                <anamorphic>FALSE</anamorphic>
                                <pixelaspectratio>square</pixelaspectratio>
                                <fielddominance>none</fielddominance>
                            </samplecharacteristics>
                        </video>
                    </media>
                  </file>
                </clipitem>
              </track>
            </video>
          </media>
        </clip>\n'''
        
        end_f = current_start + duration_frames
        seq_vid_xml += f'''          <clipitem id="seq-clip-{fid}">
            <name>{filename}</name>
            <duration>{STILL_MASTER_DURATION}</duration>
            <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
            <start>{current_start}</start><end>{end_f}</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>{duration_frames}</out>
            <file id="file-{fid}"/>
{filter_xml}
          </clipitem>\n'''
        current_start = end_f

    total_duration = current_start
    
    seq_name = seq.get("name", "Generated Sequence").replace("&", "&amp;")
    
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>{seq_name}</name>
    <children>
      <bin>
        <name>Photos &amp; Video</name>
        <children>
{master_clips_xml}        </children>
      </bin>
      <bin>
        <name>Sequences</name>
        <children>
          <sequence id="seq-1">
            <name>{seq_name}</name>
            <duration>{total_duration}</duration>
            <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
            <timecode>
                <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                <string>00:00:00:00</string>
                <frame>0</frame>
                <displayformat>NDF</displayformat>
            </timecode>
            <media>
              <video>
                <format><samplecharacteristics>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <width>{WIDTH}</width><height>{HEIGHT}</height>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
{seq_vid_xml}                </track>
              </video>
              <audio>
                <numOutputAudioTracks>2</numOutputAudioTracks>
                <format><samplecharacteristics>
                  <depth>{AUDIO_DEPTH}</depth><samplerate>{AUDIO_RATE}</samplerate>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>1</outputchannelindex>
                  <clipitem id="seq-clip-a">
                    <name>{audio_filename}</name>
                    <duration>{s2f(10000)}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{total_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{total_duration}</out>
                    <file id="file-a"/>
                  </clipitem>
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

    out_file = get_next_xml_filename()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
        
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml("baby-toddler")
