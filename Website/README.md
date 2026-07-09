# Josh Memorial Website

This directory contains the source code for the standalone Josh Memorial Website. It is designed to be a high-performance, single-page memorial experience built on pristine vanilla HTML/JS/CSS with absolutely zero heavy framework dependencies (no React, no Howler.js).

## Core Architecture & Tech Stack

- **HTML5:** `index.html` is a single-page document.
- **CSS3:** `style.css` contains all styling, including grid layouts, responsive breakpoints, typography, and scroll-driven parallax effects.
- **Vanilla JS:** Native, lightweight javascript handles all interactive elements (video overlays, music playback, gallery modal).
- **Hosting / Deployment:** Deployed via GitHub Pages.

## Key Features & Structure

1. **Background Audio (BGM) & Safari/Chrome Autoplay Hack:**
   - Browsers strictly block programmatic `.play()` on `<audio>` tags until the user interacts with the page.
   - **The Hack:** We use a `<video playsinline style="display:none;">` tag pointing to an `.mp3` source. Modern browsers *allow* inline video tags to autoplay programmatically. This bypasses the restriction, allowing the background memorial track to begin seamlessly.

2. **Tribute Video Overlay Modal (Interlocking Media State):**
   - The central framed video is the "Tribute Video". 
   - When the user clicks the video overlay, the Javascript triggers an interlocking state change:
     - It immediately pauses the background music (`wasBgmPlayingBeforeVideo = true`).
     - It expands the video modal and unmutes the video audio.
     - When the user clicks out, the video shrinks back to a silent loop, and the script checks the previous state and seamlessly restores the background music if it was playing.

3. **WebKit Controls Alignment:**
   - The tribute video is framed by a `pointer-events: none;` wooden frame overlay.
   - To prevent the native `<video controls>` from being obscured by the bottom border of the wooden frame, we inject WebKit-specific CSS (`::-webkit-media-controls-enclosure`) to add padding and push the controls up into the safe viewing zone.

4. **Media Directory:**
   - `/images/`: Houses all static assets, UI icons, and the memorial photo galleries.
   - `/music/`: Houses the highly compressed 4.5MB `.mp3` background track (converted from a massive 45MB `.wav` to prevent buffer overflows).
   - `/videos/`: Houses the memorial video files.

## Local Development

You can simply open `index.html` in any browser, or to bypass strict CORS file restrictions, you can serve the directory using Python:

```bash
cd Website
python3 -m http.server 8000
```
Then navigate to `http://localhost:8000/`.
