import os
import json
import glob
from xml.sax.saxutils import escape
from urllib.parse import quote

# ---------------------------------------------------------
# CONSTANTS & SETUP
# ---------------------------------------------------------
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")
SEQUENCES_DIR = os.path.join(PROJECT_ROOT, "EDITING_FRAMEWORK", "sequences")

TIMEBASE = 24
NTSC = "TRUE"
FPS = 24000 / 1001.0
AUDIO_RATE = 48000
AUDIO_DEPTH = 16

def s2f(seconds): return round(seconds * FPS)

def build_file_path(folder, filename):
    raw_path = f"{PROJECT_ROOT}/{folder}/{filename}"
    return f"file://localhost{quote(raw_path)}"

def generate_xml(sequence_id):
    seq_path = os.path.join(SEQUENCES_DIR, f"{sequence_id}.json")
    with open(seq_path, 'r') as f: seq = json.load(f)

    file_registry = {}
    file_idx = 1
    audio_filename = seq.get("song", {}).get("filename", "audio.mp3").replace("{ext}", "mp3")
    file_registry["audio"] = {
        "id": f"file-{file_idx}",
        "name": audio_filename,
        "pathurl": build_file_path("Music", audio_filename),
        "duration": s2f(10000), 
        "is_audio": True
    }
    file_idx += 1

    for slide in seq.get("slides", []):
        if slide["file"] not in file_registry:
            file_registry[slide["file"]] = {
                "id": f"file-{file_idx}",
                "name": slide["file"],
                "pathurl": build_file_path(slide["folder"], slide["file"]),
                "width": 3840,
                "height": 2160,
                "is_audio": False
            }
            file_idx += 1

    file_blocks = []
    for key, f in file_registry.items():
        if f["is_audio"]:
            file_xml = f'''<file id="{f['id']}">
                <name>{escape(f['name'])}</name>
                <duration>{f['duration']}</duration>
                <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                <pathurl>{f['pathurl']}</pathurl>
                <media>
                    <audio><samplecharacteristics>
                        <depth>{AUDIO_DEPTH}</depth><samplerate>{AUDIO_RATE}</samplerate>
                    </samplecharacteristics><channelcount>2</channelcount></audio>
                </media>
            </file>'''
            clip_xml = f'''        <clip id="masterclip-{f['id']}">
          <name>{escape(f['name'])}</name>
          <duration>{f['duration']}</duration>
          <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
          {file_xml}
        </clip>'''
        else:
            still_duration = 86400
            file_xml = f'''<file id="{f['id']}">
                <name>{escape(f['name'])}</name>
                <duration>{still_duration}</duration>
                <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                <pathurl>{f['pathurl']}</pathurl>
                <media>
                    <video><samplecharacteristics>
                        <width>{f['width']}</width><height>{f['height']}</height>
                    </samplecharacteristics></video>
                </media>
            </file>'''
            clip_xml = f'''        <clip id="masterclip-{f['id']}">
          <name>{escape(f['name'])}</name>
          <duration>{still_duration}</duration>
          <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
          {file_xml}
        </clip>'''
        file_blocks.append(clip_xml)

    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <bin>
    <name>Footage</name>
    <children>
{chr(10).join(file_blocks)}
    </children>
  </bin>
</xmeml>
'''

    out_file = os.path.join(XML_DIR, "Josh_Memorial_TEST_BIN_ONLY.xml")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml("baby-toddler")
