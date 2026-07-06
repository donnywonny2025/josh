# Antigravity Agent Memory Log & Directives
*Living document to track critical rules, preserved logic, and project state.*

## 1. Golden Directives (Never Break These)
- **NEVER OVERWRITE ORIGINAL CODE:** The original `player.html` and `advanced.html` contain highly specific, battle-tested logic (including the blurred background / foreground element isolation). Always duplicate files (like `player_v2.html`) before completely overhauling architectures.
- **PROTECT THE SEQUENCES:** The `/sequences/` folder contains manually timed and aligned JSON data that took hours to curate. Any new system we build must maintain backwards compatibility with reading these JSON files. Never delete or inadvertently overwrite them.
- **XML TIMEBASE:** Always reference the `FCP7_XML_Deep_Reference.md` when doing timecode math. Premiere uses specific offsets between `<start>` and `<in>`.

## 2. Preserved System Logic
### The Blurred Background / Foreground Effect
We successfully engineered a system that separates photos into two layers:
1. **Background Layer:** A blurred, scaled-up version of the photo to fill the 16:9 frame and kill black bars.
2. **Foreground Layer:** The original aspect ratio photo placed cleanly over the top.
*Directive:* This code is precious. It must remain intact in the original Player / Advanced Player files. If we rebuild the V2 player, we must either carry this logic over or preserve it perfectly in V1 so we can revert to it.

## 3. Current Project State
- Built `player_v2.html` as a clean slate for the new architecture.
- Rerouted `serve.py` to handle both the original Player and Player V2 simultaneously.
- Currently awaiting the architectural plan for how Player V2 will operate.

## 7. Immediate Visual Updating
- **Mandatory Action:** Every time the user requests a change or an update, immediately push the changes to the live browser UI and auto-refresh using `browser-harness`. Do NOT rely on the user to manually refresh the page. Visually confirm the state before responding.

## 8. Hard-Refresh Infrastructure
- **Mandatory Action:** When modifying server code or underlying web logic, you MUST restart the background server process. You MUST also configure the server to prevent aggressive browser caching (Cache-Control: no-store) on HTML/JS to ensure the live environment visually reflects the latest code when updated via browser-harness.
