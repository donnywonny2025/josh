# Josh Memorial: Master Framework State
**Last Updated:** July 2026
**Purpose:** Hand-off document for the next AI session to immediately grasp the exact state of the Editing Framework, the timeline math, the UI, and the XML export pipeline.

---

## 1. System Architecture
The framework runs entirely locally using Python and Vanilla JS/CSS.
- **Server (`serve.py`)**: A Python HTTP server (`http.localhost:8080`) that serves static files, photos from `RAW_IMPORTS`, music from `/Music/`, and handles JSON API endpoints.
- **Master UI (`player_v2.html`)**: The consolidated "Advanced Player". It contains both the cinematic playback viewer and the functional NLE Timeline interface.

## 2. The Timeline Engine (The Math)
The entire timeline is driven by strict **30 Frames Per Second (FPS)** math to ensure 1:1 translation to Premiere Pro XML.
- **Frame Calculation:** `duration_frames = duration_sec * 30`.
- **UI Rendering:** The NLE timeline in `player_v2.html` is built dynamically using CSS variables:
  - `--f-start`: The exact frame the clip begins.
  - `--f-dur`: The length of the clip in frames.
  - `--z`: The Zoom factor (controlled by a slider) which multiplies against frames to calculate exact pixel widths (`left: calc(--f-start * --z * 1px)`).
- **Audio Sync:** The JS playback engine uses `audio.currentTime * 30.0` to calculate the current frame and push UI updates via `requestAnimationFrame`.

## 3. Master Data State (`master_timeline.json`)
The 8-minute master sequence is **100% fully populated**.
- All 76 placeholder slots were programmatically replaced with real image file paths.
- The Python script mapped the sections (Family, Military, Celebrate Life, etc.) to their respective folders in `/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS`.
- Every JSON object includes `duration_frames`, `folder`, and `file`.

## 4. Player V2 UX Features
- **Hover Tooltips:** The user can scrub their mouse over the tiny thumbnails in the NLE timeline track. A dynamic tooltip (`div#hoverTooltip`) appears above the cursor, instantly loading the high-res image and displaying the filename.
- **Ken Burns Cinematic Push:** The top player dynamically applies slow scale transforms (`.push`) to the active slide.
- **Title Cards:** Chapter markers render gracefully in the timeline (Track 1) and full-screen (Track 2).

## 5. The FCP7 XML Export Pipeline
The ultimate goal of this framework is to generate an XML file for Adobe Premiere Pro.
- **Endpoint:** `POST /api/export_xml` inside `serve.py`.
- **Format:** FCP7 `xmeml` version 5.
- **Settings:** Timebase exactly 30fps (`<timebase>30</timebase>`, `<ntsc>FALSE</ntsc>`).
- **Media Mapping:** Clips are generated with sequential `<start>` and `<end>` times matching the exact 30fps mathematical progression of the web timeline.
- **Transitions (The Strategy):** The XML is currently generated with **butt cuts** (no `<transitionitem>` elements). This is intentional. It allows the editor to import the clean sequence into Premiere, hit `Cmd+A` to select all clips, and `Cmd+D` to instantly apply the default cross-dissolve to every cut.

## 6. Known Directives for Next Agent
- **DO NOT** try to implement drag-and-drop. The user wants the timeline static and readable.
- **DO NOT** use `advanced.html` or `builder.html` for timeline work. `player_v2.html` IS the Advanced Player.
- **DO NOT** modify the `serve.py` server without restarting it via a persistent background task.
- The user's goal is to refine this XML output, adjust photo framing/timing as needed, and eventually bring it into Premiere Pro.
