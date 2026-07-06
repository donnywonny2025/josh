# Josh Memorial Video - Technical Setup & Timeline Rules

## 1. The Core Pipeline
This project uses a custom web-based viewer (`player_v2.html`) to visually preview and align photos before exporting a final **FCP7 XML** file that can be imported back into Premiere Pro. 
- **Goal:** Replace placeholder "Graphic" blocks with actual photos, mathematically snapped to the audio beats.
- **Backend:** Python-based scripts (`serve.py`, `align_photos.py`, `audio_analyzer.py`).

## 2. The Source of Truth (The XML)
The canonical Premiere timeline export is **`Joshy_1.xml`**.
- **DO NOT USE `Joshy.xml`**. `Joshy_1.xml` contains the finalized 8-minute edit ending with the song *Healing*.
- The XML contains dummy text cards (e.g., `Graphic`) that define the exact start and stop bounds for each section (Early Pictures, High School, Military, etc.).

## 3. Timeline Configuration & Math Rules
- **Timebase:** `24 fps`. 
- **CRITICAL MATH RULE:** All Python scripts MUST use 24fps (not 30fps). Attempting to calculate durations at 30fps will cause massive timeline drift where the photos desync from the audio tracks.

## 4. Audio Track Layout (From Joshy_1.xml)
The audio timeline spans exactly **11,869 frames** (approximately 8 minutes and 14 seconds). The songs are laid out as follows (with minor overlapping crossfades):
1. **Caamp - By and By**: Starts at `0`, ends at `4225` (Frames)
2. **Carter Burwell - How Deep**: Starts at `4030`, ends at `6079`
3. **The Hollies - He Ain't Heavy, He's My Brother**: Starts at `5950`, ends at `8459`
4. **Healing (Official Music Video)**: Starts at `8303`, ends at `11618`

*Note: For the web player preview, these overlapping stereo tracks are flattened into a single continuous visual track to prevent UI clutter.*

## 5. Photo Alignment Logic (`align_photos.py`)
1. **Audio Analysis:** `audio_analyzer.py` runs librosa on the MP3 files to extract two data streams:
   - Rhythmic beats (percussive transients)
   - RMS energy swells (volume peaks)
2. **Beat Snapping:** Most sections (Early Pictures, Family, etc.) snap the duration of each photo to the nearest rhythmic beat.
3. **Swell Snapping:** The **Military** section uses a different algorithm—snapping photo transitions specifically to major RMS energy swells to give the segment a more cinematic, emotional feel.
