import os
from urllib.parse import quote

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Josh_Memorial_v19_NATIVE_STRUCTURE.xml")

def build_scratch():
    # 1. File definitions
    # MATCHING NATIVE PREMIERE EXPORT STRUCTURE EXACTLY
    
    file_vid = f'''        <clip id="masterclip-1">
          <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
          <name>video1.mp4</name>
          <media>
            <video>
              <track>
                <clipitem id="clipitem-1">
                  <file id="file-1">
                    <name>video1.mp4</name>
                    <pathurl>file://localhost{quote("/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/test/video1.mp4")}</pathurl>
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
            <audio>
              <track>
                <clipitem id="clipitem-2">
                  <file id="file-1"/>
                </clipitem>
              </track>
            </audio>
          </media>
        </clip>'''
        
    file_aud = f'''        <clip id="masterclip-2">
          <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
          <name>audio1.mp3</name>
          <media>
            <audio>
              <track>
                <clipitem id="clipitem-3">
                  <file id="file-2">
                    <name>audio1.mp3</name>
                    <duration>10000</duration>
                    <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
                    <pathurl>file://localhost{quote("/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/test/audio1.mp3")}</pathurl>
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
        </clip>'''

    # 2. Sequence clip items
    seq_vid = f'''          <clipitem id="clip-4">
            <name>video1.mp4</name>
            <duration>500</duration>
            <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
            <start>0</start><end>500</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>500</out>
            <file id="file-1"/>
          </clipitem>'''

    seq_aud = f'''          <clipitem id="clip-5">
            <name>audio1.mp3</name>
            <duration>10000</duration>
            <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
            <start>0</start><end>500</end>
            <enabled>TRUE</enabled>
            <in>0</in><out>500</out>
            <file id="file-2"/>
          </clipitem>'''

    # 3. Assemble sequence
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Josh Memorial Native</name>
    <children>
      <bin>
        <name>Footage</name>
        <children>
{file_vid}
{file_aud}
        </children>
      </bin>
      <bin>
        <name>Sequences</name>
        <children>
      <sequence id="seq-1">
        <name>Scratch Sequence Native</name>
        <duration>500</duration>
        <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
        <timecode>
            <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
            <string>00:00:00:00</string>
            <frame>0</frame>
            <displayformat>NDF</displayformat>
        </timecode>
        <media>
          <video>
            <format><samplecharacteristics>
              <rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>
              <width>3840</width><height>2160</height>
            </samplecharacteristics></format>
        <track>
          <enabled>TRUE</enabled>
          <locked>FALSE</locked>
{seq_vid}
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
{seq_aud}
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
        
    print(f"Success! Generated Scratch XML: {OUT_XML}")

if __name__ == "__main__":
    build_scratch()
