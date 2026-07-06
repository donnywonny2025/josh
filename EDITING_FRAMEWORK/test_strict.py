import os
from urllib.parse import quote

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")
TIMEBASE = 24
NTSC = "TRUE"

def generate_xml():
    video_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/video1.mp4')}"
    image_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/image1.jpg')}"
    audio_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/audio1.mp3')}"
    
    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Josh Memorial Strict Format</name>
    <children>
      <bin>
        <name>Footage</name>
        <children>
            <clip id="masterclip-file-1">
              <name>video1.mp4</name>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <file id="file-1">
                  <name>video1.mp4</name>
                  <pathurl>{video_path}</pathurl>
                  <media>
                      <video><samplecharacteristics>
                          <width>3840</width><height>2160</height>
                      </samplecharacteristics></video>
                      <audio><samplecharacteristics>
                          <depth>16</depth><samplerate>48000</samplerate>
                      </samplecharacteristics><channelcount>2</channelcount></audio>
                  </media>
              </file>
            </clip>

            <clip id="masterclip-file-2">
              <name>image1.jpg</name>
              <duration>86400</duration>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <stillframe>TRUE</stillframe>
              <file id="file-2">
                  <name>image1.jpg</name>
                  <duration>86400</duration>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <pathurl>{image_path}</pathurl>
                  <media>
                      <video><samplecharacteristics>
                          <width>3840</width><height>2160</height>
                      </samplecharacteristics></video>
                  </media>
              </file>
            </clip>

            <clip id="masterclip-file-3">
              <name>audio1.mp3</name>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <file id="file-3">
                  <name>audio1.mp3</name>
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
          <sequence>
            <name>Test Strict Sequence</name>
            <duration>480</duration>
            <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
            <media>
              <video>
                <format><samplecharacteristics>
                  <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                  <width>3840</width><height>2160</height>
                </samplecharacteristics></format>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <clipitem id="clip-1">
                    <name>video1.mp4</name>
                    <duration>240</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>240</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>240</out>
                    <file id="file-1"/>
                  </clipitem>
                  <clipitem id="clip-2">
                    <name>image1.jpg</name>
                    <duration>240</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>240</start><end>480</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>240</out>
                    <stillframe>TRUE</stillframe>
                    <file id="file-2"/>
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
                  <clipitem id="clip-3">
                    <name>video1.mp4</name>
                    <duration>240</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>240</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>240</out>
                    <file id="file-1"/>
                  </clipitem>
                </track>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>2</outputchannelindex>
                  <clipitem id="clip-4">
                    <name>audio1.mp3</name>
                    <duration>480</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>480</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>480</out>
                    <file id="file-3"/>
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

    out_file = os.path.join(XML_DIR, "Josh_Memorial_v11_STRICT.xml")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml()
