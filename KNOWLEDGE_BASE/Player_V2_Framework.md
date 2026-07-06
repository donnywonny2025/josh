# Josh Memorial Video - Player V2 Framework Documentation

This document outlines the architecture, data flow, and features of the custom HTML5 timeline player and AI curation system built for the Josh Memorial Video project.

## 1. Core Architecture

The framework consists of a lightweight, local web-based editor (`player_v2.html`) that simulates a Non-Linear Editor (NLE) like Final Cut Pro. It reads a master JSON timeline, syncs it perfectly to a 24-fps audio track (`master.mp3`), and allows for manual curation, scrubbing, and framing adjustments (scale/position). 

Once the user finishes their edits, the system compiles the JSON timeline into an `FCP7 XML` file. This XML file can be directly imported into Final Cut Pro, Premiere Pro, or DaVinci Resolve, instantaneously generating a perfectly cut sequence with all framing data, timings, and high-res media linked.

## 2. The Curation Pipeline

### AI Facial Recognition & Context Scanning
1. **Face Detection (`face_clusters.json`, `face_labels.json`)**: All photos in the inventory were scanned using AI facial recognition to cluster faces and identify Josh, Ben, Linsey, and other family members.
2. **Context Scanning (`photo_context.json`)**: A vision model scanned all photos to identify contextual tags such as "group", "military", "wedding", "smiling", and "blurry".
3. **Framing Data (`photo_framing.json`)**: Contains user-defined scale, X, and Y positional adjustments for photos to ensure perfect composition in a 16:9 vertical or horizontal frame.

### `curate_and_populate.py` (The Brains)
This script is responsible for automatically populating the timeline placeholders based on the narrative structure.
- **Strict Face Enforcement**: Before a photo is even considered, the script cross-references the facial recognition data to ensure Josh is explicitly detected in the photo. Photos without Josh are immediately discarded.
- **Scoring System**: Photos are scored based on contextual data. Group shots receive a massive +10 bonus to ensure a diverse cast of people. Other family members, weddings, military uniforms, and smiling faces also receive positive weights. 
- **Sorting**: Photos are categorized into specific chronological pools (Early Pictures, High School, Military, Celebrate Life) and then sorted by their score. The absolute best photos are chosen first.
- **Output**: The script overwrites `sequences/master_timeline.json` with the selected photos while strictly preserving the timing (`duration_sec`) of the master template.

## 3. Player V2 Features (`player_v2.html`)

The interactive player provides a smooth, frame-accurate editing experience.

### Playback & Sync
- **Strict 24 FPS Logic**: The player's heartbeat is the `updateFrame` loop running on `requestAnimationFrame`. It strictly calculates the current frame (`nowSec * 24.0`) to ensure photos change at the exact right millisecond to hit the musical beats.
- **Dual-Buffer System**: To prevent flickering, the player uses two image tags (`#slideA` and `#slideB`). It seamlessly crossfades or cuts between them by toggling the `.hidden` CSS class, ensuring the next photo is pre-loaded before it appears.

### Curation & Scrubbing Tools
- **Drag-to-Scrub Timeline**: The timeline container has custom event listeners (`mousedown`, `mousemove`, `mouseup`) that allow the user to drag the playhead left and right, scrubbing through time instantly.
- **Zoom Slider**: Uses a logarithmic scale to let the user zoom deep into the timeline to see exact photo timings, or zoom out to see the entire 12-minute sequence at a glance.
- **State Persistence**: The current playback time is constantly saved to the browser's `localStorage` (`josh_player_time`). If the user refreshes the page, a rock-solid initialization sequence restores the exact timecode they were at, waiting for the audio metadata to load before applying the seek to prevent race conditions.
- **Transport Controls**: Standard controls including Play/Pause, Next Photo (`seekRelative(1)`), Previous Photo (`seekRelative(-1)`), and a Home button (`seekToTime(0)`) to jump back to the beginning.

### Real-Time Overlays
- **Timecode & Data Overlay**: A blue semi-transparent overlay dynamically tracks the exact timecode (`M:SS.ms`) and the physical hard drive path of the currently active photo. This is crucial for manual swapping and communication with the AI.

### Framing Mode
- **Lock Framing**: Clicking the "Align" (✅) button saves any manual scale, X, and Y positional adjustments made in the UI directly back to the server (`/api/save_framing`), which writes to `photo_framing.json`. This ensures all manual composition work is perfectly translated to the final FCP7 XML.

## 4. Final Export

Once all photos are manually swapped, approved, and framed in the `player_v2.html` interface, a separate compilation script (`export_final_xml.py` / `parse_xml.py`) takes `master_timeline.json` and `photo_framing.json` and weaves them together into the final `Joshy.xml` file for the NLE.
