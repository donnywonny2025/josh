# START HERE - Josh Memorial Video Project

## What We Are Building
We are building a custom web-based application (`player_v2.html`) to visually align, sort, and beat-match 144 photos to a precise 8-minute audio edit, and then export those photos as a final **FCP7 XML file** for Adobe Premiere.

This web player is essentially our own custom video editor tailored specifically for this memorial project.

## The Source of Truth (The XML)
All timing, sections, and audio tracks are dictated by **`Joshy_1.xml`** (located in `Exports/`). 
* The timeline is exactly **8 minutes and 14 seconds** long.
* The songs are: Caamp, Carter Burwell, The Hollies, and Healing.
* **CRITICAL RULE:** All scripts must run at **24 FPS**. If 30 FPS is used anywhere, the entire timeline will drift out of sync.

## The Code Architecture & Workflow (EDITING_FRAMEWORK)
All scripts live in `/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/`. This is a Python backend + Vanilla HTML/JS frontend architecture.

1. **Audio Analysis (`audio_analyzer.py`)**
   - **Purpose:** Uses `librosa` to analyze the MP3 files for rhythmic beats (percussive transients) and RMS energy swells (volume peaks).
   - **Output:** Saves timestamps to `audio_beat_map.json`.

2. **Timeline Math (`align_photos.py`)**
   - **Purpose:** The core math engine. It reads the section bounds from `Joshy_1.xml`. It takes the photos and mathematically snaps their durations to the beats and swells in `audio_beat_map.json`. 
   - **Rules:** The **Military** section snaps to RMS energy swells (for cinematic impact). All other sections snap to percussive beats.
   - **Output:** Overwrites `sequences/master_timeline.json` with exact `duration_sec` and `duration_frames` for every single photo.

3. **The Web Player (`player_v2.html` & `serve.py`)**
   - **Backend:** `serve.py` is a simple Python HTTP server that serves the UI and exposes API endpoints (like `/api/export_xml`).
   - **Frontend:** `player_v2.html` is the UI. It is NOT an MP4 video player. It dynamically renders the JPG/PNG photos sequentially using JavaScript based on the durations in `master_timeline.json`. 
   - **Timeline UI:** Renders a flat, single-track visual representation of the audio tracks at the bottom of the screen to avoid UI clutter, reading from `audio_timeline.json`.

4. **XML Export (`generate_xml.py`)**
   - **Purpose:** When the user clicks "Export XML" in the UI, `serve.py` triggers this script. It reads the final `master_timeline.json` and outputs a compliant FCP7 XML file.
   - **Constraint:** It must maintain strict 24 FPS math (`s2f(sec) = round(sec * 24)`) and replace the original placeholder `Graphic` blocks from Premiere with the actual beat-matched photos.

## Current State
The backend math (24 FPS alignment) and the UI track rendering are fully synced and locked to `Joshy_1.xml`. 

**Next Steps:** We are ready to start physically placing, adding, and removing photos from the timeline using the web player, adjusting their Ken Burns framing, and preparing for the final XML export to Premiere.

## 🎯 NEXT CHAT GOAL
When a new chat session starts, the **primary and exclusive focus** should be on `player_v2.html` and its associated JavaScript. The goal is to build out the UI functionality to allow the user to easily **add pictures, remove pictures, and reorder them** directly within the web player interface.

**🚨 ULTIMATE END GOAL:** Remember that this entire web app is just a staging environment. At the end of the day, whatever changes the user makes in `player_v2.html` MUST be pushed out to a valid **FCP7 Premiere XML** (via `generate_xml.py`). Any features you build for adding/removing photos must perfectly update `master_timeline.json` so the XML generator can successfully export the timeline back into Premiere.
