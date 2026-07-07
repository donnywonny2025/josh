# Josh Memorial - Editing Framework & XML Pipeline

## Core Architecture
Because Premiere Pro struggles with smoothly previewing, reframing, and pacing hundreds of high-res photos to beat-mapped music without lagging, we built a custom "offline" HTML/JS editing framework. 

This framework acts as a bridge: we do all the creative pacing and framing in the fast HTML player, and then programmatically compile those decisions back into a mathematically perfect Premiere Pro XML.

## 1. The Timeline State (`master_timeline.json` & `true_beats.json`)
The source of truth for the entire edit lives in the JSON data.
- **`sequences/master_timeline.json`**: Dictates the exact order of the photos, the duration they stay on screen (in frames), and their `[X, Y]` center of mass focus points.
- **`true_beats.json`**: Contains the mathematically precise frame timings of the music beat-drops, ensuring our photos transition perfectly on the grid.

## 2. The HTML Audition Player (`player_v2.html` & `serve.py`)
- **`serve.py`**: A Python web server that serves the local directory, bypassing CORS to load the heavy photos. It exposes an `/api/save_timeline` endpoint so the HTML player can persist edits.
- **`player_v2.html`**: A cinematic audition player. It uses GSAP to simulate Ken Burns zooms and `object-position` CSS to simulate framing. It allows rapid pacing adjustments and drag-and-drop reordering. 

### How to use the player:
1. Open terminal and run `python3 serve.py` from the `EDITING_FRAMEWORK` directory.
2. Open `http://localhost:8000/player_v2.html` in Chrome.
3. Make changes and hit 'Save' to update `master_timeline.json`.

## 3. The Premiere XML Generation (CRITICAL WORKFLOW)
**WARNING: NEVER screen-record the HTML player as a final export. The final deliverable is ALWAYS an FCP7 XML sequence.**

Once the edit is locked in the HTML player, it must be translated into Premiere Pro. We do this using `build_master_xml.py` (or `generate_xml.py`). 
This script reads the JSON state and outputs `/Volumes/Extreme SSD/JOSH/Exports/Josh_Master_BeatMapped_With_Motion.xml`.

### The XML Math (How we translate CSS to Premiere Basic Motion):
1. **Auto-Cover Scaling:** The script calculates the exact scale required to `cover` a 1920x1080 sequence based on the raw photo's aspect ratio, preventing black bars.
2. **Smart Framing (Center):** It takes the `focus` percentage from the JSON and translates it into Premiere's `<horiz>` and `<vert>` offset fractions.
3. **Ken Burns Zoom:** The script injects `<keyframe>` blocks into the FCP7 XML's `<parameter>` for `Scale`. It sets a start keyframe at the base "cover" scale, and an end keyframe at `base_scale * 1.05`, generating a seamless 5% push-in.

## 4. AI Tooling & Automation Scripts
Over the course of the project, we built numerous Python tools to automate tedious tasks:
- **`find_best_josh.py`**: Reads the AI image database and copies the top 5 aesthetically pleasing solo photos of Josh into a "Best Picks" folder.
- **`advanced_analyzer.py`**: Scans the raw metadata of photos.
- **`surgical_swap.py`**: Allows precise swapping of individual photos inside the JSON timeline without breaking the pacing.
- **`patch_early_years.py`**: Programmatically injects the chronological early-years/childhood block into the start of the sequence.
- **`vinyl_title_generator.html`**: The UI for designing the custom memorial vinyl graphics.
