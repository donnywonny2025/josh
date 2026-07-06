# Web App Architecture (EDITING_FRAMEWORK)

## The Core Concept
The `EDITING_FRAMEWORK` is a local Python-backed web application running on port `8080`. It serves as the visual engine for selecting, sequencing, and previewing the memorial video before sending it to Premiere via XML.

## 1. The Backend (`serve.py`)
- **Server:** Runs a standard `http.server` (synchronous) bound to `localhost:8080`.
- **APIs:** 
  - `/api/folders` & `/api/photos/`: Scans the `Photos/RAW_IMPORTS/` directory.
  - `/api/sequences/`: Reads and writes JSON sequence files in `sequences/`.
  - `/api/marks`: Reads/writes favorite/exclude metadata to `marks.json`.
  - `/api/face-labels`: Interface for the AI face-clustering data.
- **Media Delivery:** Serves media directly from the `Music` and `Photos` directories via raw byte streaming (`Content-Type` mappings).

## 2. The Browser (`app.html`)
- **Purpose:** Fast photo culling.
- **Workflow:** View all folders, filter out bad shots, star good shots.
- **Mechanism:** Writes to `marks.json`.

## 3. The Builder (`builder.html`)
- **Purpose:** Constructing the actual timeline sequence.
- **Workflow:** 
  1. Select a "Section" (Chapter) from the top dropdown.
  2. Drag and drop photos from the left pool into the timeline.
  3. Adjust the exact duration (in seconds) for each slide.
- **Data Source:** Pulls from `/api/sequences/:id` and writes updates via POST on save.

## 4. The Player (`player.html`)
- **Purpose:** Full-screen playback simulation.
- **Features:** 
  - Preloads audio from `/api/music/`.
  - Uses CSS classes (`slide.active`, `slide.hidden`) to crossfade images natively in the DOM.
  - Automatically applies a Ken Burns "push" using CSS animations (`@keyframes pushIn`).
  - **Smart Framing:** Uses the `photo_framing_map.json` center-of-mass to set the CSS `transform-origin` and `object-position`, ensuring faces are never cut off on 16:9 screens.
  - **Manual Framing Override:** The "Align Framing" button enables drag-to-pan, writing custom `focus: [x, y]` arrays back to the sequence JSON.

## Coding Best Practices for this App
1. **Vanilla JS ONLY:** The app uses pure vanilla JS state (`let seq`, `let playing`). Do not try to inject a framework like React or Vue. Stick to raw DOM manipulation (`document.getElementById`).
2. **URL Encoding:** Always encode folder/file names when building src URLs (`/photos/${encodeURIComponent(folder)}/${encodeURIComponent(file)}`).
3. **Persistence:** State changes (like framing adjustments or sequence reordering) must be POSTed to the backend APIs to persist; they do not auto-save unless explicitly wired to do so.
