import os
import glob
import subprocess

# Configuration
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
PHOTOS_DIR = os.path.join(PROJECT_ROOT, "PHOTOS", "RAW_IMPORTS", "Baby & toddler Josh")
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Baby_Toddler_v2.xml")

TB = 24
STILL_DURATION = 150 # What Premiere used in Test.xml for duration
CLIP_DURATION = 120 # 5 seconds per slide at 24fps

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

def build_xml():
    # 1. Grab photos
    valid_exts = {".jpg", ".jpeg", ".png"}
    files = []
    for f in os.listdir(PHOTOS_DIR):
        if os.path.splitext(f.lower())[1] in valid_exts and not f.startswith("."):
            files.append(os.path.join(PHOTOS_DIR, f))
    files.sort()
    
    # 2. Add the video clip to the very beginning, as per user request to "trick/force" Premiere
    video_path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/test/video1.mp4"
    audio_path = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/test/audio1.mp3"
    
    def encode_path(p):
        return p.replace(" ", "%20").replace("&", "&amp;")

    master_clips_xml = f'''        <clip id="masterclip-v">
          <ismasterclip>TRUE</ismasterclip>
          <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
          <name>video1.mp4</name>
          <media>
            <video>
              <track>
                <clipitem id="clipitem-v">
                  <masterclipid>masterclip-v</masterclipid>
                  <name>video1.mp4</name>
                  <file id="file-v">
                    <name>video1.mp4</name>
                    <pathurl>file://localhost{encode_path(video_path)}</pathurl>
                    <media>
                        <audio><channelcount>2</channelcount></audio>
                        <video><samplecharacteristics>
                            <width>3840</width><height>2160</height>
                        </samplecharacteristics></video>
                    </media>
                  </file>
                </clipitem>
              </track>
            </video>
          </media>
        </clip>
        <clip id="masterclip-a">
          <ismasterclip>TRUE</ismasterclip>
          <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
          <name>audio1.mp3</name>
          <media>
            <audio>
              <track>
                <clipitem id="clipitem-a">
                  <masterclipid>masterclip-a</masterclipid>
                  <name>audio1.mp3</name>
                  <file id="file-a">
                    <name>audio1.mp3</name>
                    <duration>10000</duration>
                    <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                    <pathurl>file://localhost{encode_path(audio_path)}</pathurl>
                    <media>
                        <audio><samplecharacteristics>
                            <depth>16</depth><samplerate>48000</samplerate>
                        </samplecharacteristics><channelcount>2</channelcount></audio>
                    </media>
                  </file>
                </clipitem>
              </track>
            </audio>
          </media>
        </clip>
'''

    # Sequence Video Track string
    seq_vid_xml = f'''          <clipitem id="seq-clip-v">
            <name>video1.mp4</name>
            <duration>500</duration>
            <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
            <start>0</start><end>500</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>500</out>
            <file id="file-v"/>
          </clipitem>
'''
    current_start = 500

    # Photos
    for i, filepath in enumerate(files):
        fid = i + 1
        filename = os.path.basename(filepath)
        w, h = get_image_dimensions(filepath)
        url = "file://localhost" + encode_path(filepath)
        
        # Exact structure mapped from Test.xml
        master_clips_xml += f'''        <clip id="masterclip-{fid}" explodedTracks="true">
          <masterclipid>masterclip-{fid}</masterclipid>
          <ismasterclip>TRUE</ismasterclip>
          <duration>{STILL_DURATION}</duration>
          <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
          <in>0</in>
          <out>{STILL_DURATION - 1}</out>
          <name>{filename}</name>
          <media>
            <video>
              <track>
                <clipitem id="clipitem-master-{fid}">
                  <masterclipid>masterclip-{fid}</masterclipid>
                  <name>{filename}</name>
                  <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                  <alphatype>none</alphatype>
                  <pixelaspectratio>square</pixelaspectratio>
                  <anamorphic>FALSE</anamorphic>
                  <file id="file-{fid}">
                    <name>{filename}</name>
                    <pathurl>{url}</pathurl>
                    <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                    <timecode>
                        <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                        <string>00:00:00:00</string>
                        <frame>0</frame>
                        <displayformat>NDF</displayformat>
                    </timecode>
                    <media>
                        <video>
                            <samplecharacteristics>
                                <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
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
        </clip>
'''
        # Sequence Clipitem
        end_f = current_start + CLIP_DURATION
        seq_vid_xml += f'''          <clipitem id="seq-clip-{fid}">
            <name>{filename}</name>
            <duration>{STILL_DURATION}</duration>
            <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
            <start>{current_start}</start><end>{end_f}</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>{CLIP_DURATION}</out>
            <file id="file-{fid}"/>
          </clipitem>
'''
        current_start = end_f

    total_duration = current_start
    
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Baby &amp; Toddler Native Structure</name>
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
{seq_vid_xml}                </track>
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
                  <clipitem id="seq-clip-a">
                    <name>audio1.mp3</name>
                    <duration>10000</duration>
                    <rate><timebase>{TB}</timebase><ntsc>TRUE</ntsc></rate>
                    <start>0</start><end>500</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>500</out>
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

    os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
    with open(OUT_XML, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
        
    print(f"Success! Generated XML: {OUT_XML}")

if __name__ == "__main__":
    build_xml()
