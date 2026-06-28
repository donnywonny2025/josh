# Josh Memorial — Video Editing & AI Framework

This repository contains the intelligent, browser-based framework designed to automate the editing process for the Josh Memorial video project.

The system bypasses the tedious manual labor of NLE timelines (Premiere) by allowing you to sequence photos, assign music, and automatically build frame-accurate Adobe Premiere XMLs straight out of your web browser.

## Core Architecture

- **`EDITING_FRAMEWORK/`**: The main brain. Contains the backend server (`serve.py`), the UI tools (`app.html`, `builder.html`, `faces.html`), and the AI Face Recognition pipeline.
- **`KNOWLEDGE_BASE/`**: Contains the `PROJECT_CONTEXT.md` and `MUSIC_REFERENCE.md` documents tracking the creative narrative, exact track durations, and timeline logic.
- **`XML_Exports/`**: Where the backend saves the finalized `.xml` files ready to be dragged directly into Premiere Pro.

## Features

1. **Face ID Hub (`/faces`)**: Uses Python `face_recognition` (dlib) to automatically scan, cluster, and crop every face in the project. Includes a real-time UI for naming individuals and pushing updates to the system.
2. **Photo Browser (`/`)**: A visual gallery for reviewing all raw imports. Dynamically displays Face ID tags (e.g., `👤 Josh, David`) overlaid directly on the photos.
3. **Sequence Builder (`/builder`)**: The editing timeline. Drag-and-drop photos, assign durations, match sections to specific audio tracks, and save sequences to JSON.
4. **FCP7 XML Generator**: Translates the sequences into mathematically precise Premiere Pro XML files, calculating standard durations, crossfades, and sequence pacing perfectly synced to the audio.

## How to Run

1. Navigate to the project directory.
2. Start the local server:
   ```bash
   cd EDITING_FRAMEWORK
   python3 serve.py
   ```
3. Open `http://localhost:8080/` in your browser.

*Note: The raw heavy media files (Photos, Music, Premiere Project files) are intentionally excluded via `.gitignore` to keep this repository lightweight and code-focused.*
