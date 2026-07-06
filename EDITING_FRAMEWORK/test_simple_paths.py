import os
from urllib.parse import quote

# ---------------------------------------------------------
# CONSTANTS & SETUP
# ---------------------------------------------------------
PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")

TIMEBASE = 24
NTSC = "TRUE"

def s2f(seconds): return round(seconds * (24000/1001.0))

def generate_xml():
    audio_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/audio1.mp3')}"
    image_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/image1.jpg')}"
    
    still_duration = 86400
    seq_duration = s2f(6.0)

    # Simplified clip and sequence structure modeled exactly after what works, removing extra tags where possible
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Josh Memorial Simple Paths</name>
    <children>
      <bin>
        <name>Footage</name>
        <children>
            <clip id="masterclip-file-1">
              <name>image1.jpg</name>
              <duration>{still_duration}</duration>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <stillframe>TRUE</stillframe>
              <file id="file-1">
                  <name>image1.jpg</name>
                  <duration>{still_duration}</duration>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <pathurl>{image_path}</pathurl>
                  <media>
                      <video><samplecharacteristics>
                          <width>3840</width><height>2160</height>
                      </samplecharacteristics></video>
                  </media>
              </file>
            </clip>
            <clip id="masterclip-file-2">
              <name>audio1.mp3</name>
              <duration>{s2f(10000)}</duration>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <file id="file-2">
                  <name>audio1.mp3</name>
                  <duration>{s2f(10000)}</duration>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <pathurl>{audio_path}</pathurl>
                  <media>
                      <audio><samplecharacteristics>
                          <depth>16</depth><samplerate>48000</samplerate>
                      </samplecharacteristics><channelcount>2</channelcount></audio>
                  </media>
              </file>
            </clip>
        </children>
      </bin>
      <bin>
        <name>Sequences</name>
        <children>
          <sequence id="seq-main">
            <name>Test Simple Path Sequence</name>
            <duration>{seq_duration}</duration>
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
                  <width>3840</width><height>2160</height>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <clipitem id="clip-v-1">
                    <name>image1.jpg</name>
                    <duration>{seq_duration}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{seq_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{seq_duration}</out>
                    <stillframe>TRUE</stillframe>
                    <file id="file-1"/>
                  </clipitem>
                </track>
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
                  <clipitem id="clip-a-1">
                    <name>audio1.mp3</name>
                    <duration>{s2f(10000)}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{seq_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{seq_duration}</out>
                    <file id="file-2"/>
                  </clipitem>
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

    out_file = os.path.join(XML_DIR, "Josh_Memorial_v9_SIMPLE.xml")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml()
