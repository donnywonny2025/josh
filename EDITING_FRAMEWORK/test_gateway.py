import os
from urllib.parse import quote

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
XML_DIR = os.path.join(PROJECT_ROOT, "Premiere", "XML")
TIMEBASE = 24
NTSC = "TRUE"

def s2f(seconds): return round(seconds * (24000/1001.0))

def generate_xml():
    video_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/video1.mp4')}"
    image_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/image1.jpg')}"
    audio_path = f"file://localhost{quote(f'{PROJECT_ROOT}/EDITING_FRAMEWORK/test/audio1.mp3')}"
    
    still_duration = 86400
    seq_duration = s2f(6.0)
    video_duration = s2f(10.0) # just an arbitrary duration for the clip in the sequence

    sequence_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <project>
    <name>Josh Memorial Gateway Test</name>
    <children>
      <bin>
        <name>Footage</name>
        <children>
            <!-- VIDEO GATEWAY CLIP -->
            <clip id="masterclip-file-vid">
              <name>video1.mp4</name>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <file id="file-vid">
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

            <!-- STILL IMAGE -->
            <clip id="masterclip-file-img">
              <name>image1.jpg</name>
              <duration>{still_duration}</duration>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <stillframe>TRUE</stillframe>
              <file id="file-img">
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

            <!-- AUDIO -->
            <clip id="masterclip-file-aud">
              <name>audio1.mp3</name>
              <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
              <file id="file-aud">
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
          <sequence id="seq-main">
            <name>Test Gateway Sequence</name>
            <duration>{seq_duration * 3}</duration>
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
                  <!-- THE VIDEO GATEWAY -->
                  <clipitem id="clip-v-vid">
                    <name>video1.mp4</name>
                    <duration>{video_duration}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{video_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{video_duration}</out>
                    <file id="file-vid"/>
                  </clipitem>
                  <!-- THE STILL IMAGE -->
                  <clipitem id="clip-v-img">
                    <name>image1.jpg</name>
                    <duration>{seq_duration}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>{video_duration}</start><end>{video_duration + seq_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{seq_duration}</out>
                    <stillframe>TRUE</stillframe>
                    <file id="file-img"/>
                  </clipitem>
                </track>
              </video>
              <audio>
                <numOutputAudioTracks>2</numOutputAudioTracks>
                <format><samplecharacteristics>
                  <depth>16</depth><samplerate>48000</samplerate>
                </samplecharacteristics></format>
                <!-- AUDIO FROM THE VIDEO GATEWAY -->
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>1</outputchannelindex>
                  <clipitem id="clip-a-vid">
                    <name>video1.mp4</name>
                    <duration>{video_duration}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{video_duration}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{video_duration}</out>
                    <file id="file-vid"/>
                  </clipitem>
                </track>
                <track>
                  <enabled>TRUE</enabled>
                  <locked>FALSE</locked>
                  <outputchannelindex>2</outputchannelindex>
                  <clipitem id="clip-a-aud">
                    <name>audio1.mp3</name>
                    <duration>{s2f(10000)}</duration>
                    <rate><timebase>{TIMEBASE}</timebase><ntsc>{NTSC}</ntsc></rate>
                    <start>0</start><end>{s2f(10000)}</end>
                    <enabled>TRUE</enabled>
                    <in>0</in><out>{s2f(10000)}</out>
                    <file id="file-aud"/>
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

    out_file = os.path.join(XML_DIR, "Josh_Memorial_v10_GATEWAY.xml")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(sequence_xml)
    print(f"Success! Generated XML: {out_file}")

if __name__ == "__main__":
    generate_xml()
