import os
import json
from xml.sax.saxutils import escape
from urllib.parse import quote

# ---------------------------------------------------------
# CONSTANTS & SETUP
# ---------------------------------------------------------
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")

TIMEBASE = 24
NTSC = "TRUE"
FPS = 24000 / 1001.0
AUDIO_RATE = 48000
AUDIO_DEPTH = 16

def s2f(seconds): return round(seconds * FPS)

def build_file_path(folder, filename):
    raw_path = f"{PROJECT_ROOT}/{folder}/{filename}"
    return f"file://localhost{quote(raw_path)}"

def generate_xml():
    audio_filename = "John Denver - Perhaps Love.mp3.mp3"
    f_id = "file-1"
    f_name = audio_filename
    f_pathurl = build_file_path("Music", audio_filename)

    file_xml = f'''<file id="{f_id}">
                <name>{escape(f_name)}</name>
                <pathurl>{f_pathurl}</pathurl>
                <media>
                    <audio><samplecharacteristics>
                        <depth>{AUDIO_DEPTH}</depth><samplerate>{AUDIO_RATE}</samplerate>
                    </samplecharacteristics><channelcount>2</channelcount></audio>
                </media>
            </file>'''
            
    clip_xml = f'''        <clip id="masterclip-{f_id}">
          <name>{escape(f_name)}</name>
          <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
          {file_xml}
        </clip>'''

    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Josh Memorial Test 4</name>
    <children>
      <bin>
        <name>Footage Exact</name>
        <children>
{clip_xml}
        </children>
      </bin>
    </children>
  </project>
</xmeml>
'''

    out_file = os.path.join(XML_DIR, "Josh_Memorial_TEST_EXACT.xml")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml()
