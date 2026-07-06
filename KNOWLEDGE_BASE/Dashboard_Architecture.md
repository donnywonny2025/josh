# Josh Memorial - Video Editing Framework Architecture

**CRITICAL AGENT DIRECTIVE:** Read this document BEFORE attempting to build, start, or modify any web applications in this repository. DO NOT build new web apps. The entire video editing NLE is already built and located in `/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/`.

## The System
This is a fully custom, browser-based Non-Linear Video Editor (NLE). It was built to allow the user to visually assemble, transition, and synchronize 500+ photos to a memorial audio track, and then export the final result as an FCP7 XML file for Premiere Pro / Final Cut.

## Server backend (`serve.py`)
- **Port:** `8080` (ALWAYS RUN ON 8080. DO NOT USE `http.server 8000`).
- **Command:** `python3 serve.py` inside `EDITING_FRAMEWORK/`
- **Purpose:** Serves the frontend UI and provides crucial REST API endpoints (`/api/master`, `/api/sequences`, `/api/audio-timeline`) which the React/JS frontends rely on to load data. If you use a generic `http.server`, the APIs will 404 and the app will break.

## Frontend UIs
1. **Dashboard (`/` or `app.html`)**: Overview of the project status.
2. **Builder (`/builder` or `builder.html`)**: The drag-and-drop Sequence Builder. Shows photo slots, durations, sections, and the timeline. 
3. **Player (`/player_v2` or `player_v2.html`)**: The synchronized video player. Plays the audio track and visually switches photos on the beat based on the timeline JSON.

## Data Pipeline
1. **The Photos**: Stored in `Photos/RAW_IMPORTS/` by category folders.
2. **The LLaVA Vision Scan**: A deep local AI vision model scanned all 536 photos and generated `master_photo_db.json`. This database contains:
   - `description`: Textual descriptions of what is happening (e.g., "Two men smiling in military uniforms").
   - `estimated_age`: (DEPRECATED - User explicitly rejected the AI age estimations because they were inaccurate).
3. **Identity Mapping**: Apple Vision faces were extracted into `face_data/face_clusters.json` and `face_labels.json` to know exactly who is in every photo (Josh, Ben, Linsey, etc).
4. **Sequence Population (`curate_v3.py`)**: This script intelligently populates the timeline sequence (`sequences/master_timeline.json`) using the AI vision descriptions (scoring points for smiles, groups, military) and semantic sorting based on Folder Order.
5. **XML Export**: The finalized JSON timeline can be exported to FCP7 XML format for final rendering in a professional video editor.

## Known Gotchas & User Preferences
- **DO NOT USE `absolute_age` OR LLaVA AGE LOGIC.** The AI guessed ages horribly wrong. Rely on the user's manual Folder categorization ("Baby & toddler Josh" -> "Josh school years" -> etc.) for chronology.
- **DO NOT OPEN NEW TABS REPEATEDLY.** If Chrome is already open to `localhost:8080`, just refresh or navigate within the existing tab.
- **DO NOT LEAVE GHOST PROCESSES.** If you need to restart `serve.py`, make sure to `pkill -f serve.py` first so the port isn't blocked.
