# Error & Diagnostic Log

As mandated by **Rule 7** in `OPERATING_RULES.md`, this log tracks issues, misconfigurations, and their resolutions to ensure historical accountability and prevent recurring problems.

## Log Format
- **Date/Time:**
- **Severity:** [Low | Medium | High | Critical]
- **Component:** 
- **Error Description:**
- **Fix / Resolution:**
- **Status:** [Resolved | Pending]

---

### 2026-07-01
- **Severity:** Low
- **Component:** Browser Harness (`tab_manager.py`)
- **Error Description:** AppleScript-based tab management triggers blocking OS-level permission prompts (e.g., "osascript wants to control Chrome").
- **Fix / Resolution:** Replaced pure AppleScript tab management with a Python CDP script (`tab_manager.py`) that shells out to `browser-harness -c` to query WebSockets securely via `localhost:9222`.
- **Status:** Resolved

### 2026-07-01
- **Severity:** High
- **Component:** Workflow Protocol (Browser Tab Management)
- **Error Description:** Blindly executed `goto_url()` when told to open the Google Doc, which overwrote the active Player App tab. This destroyed the user's dual-monitor workspace because I adhered to an overly-literal "One-Tab Rule" rather than a context-aware system.
- **Fix / Resolution:** Refactored `tab_manager.py` to allow multiple distinct tools while deduplicating copies ("One Unique Instance per App"). Updated `OPERATING_RULES.md` to strictly forbid overwriting active tools with `goto_url()` and instead mandate `list_tabs()` checks combined with `switch_tab()` or `new_tab()`.
- **Status:** Resolved

### 2026-07-01
- **Severity:** Critical
- **Component:** Player App (`player.html`)
- **Error Description:** An infinite loop / stack overflow crashed the page immediately upon loading any sequence. `loadSequence()` called `stopPlayback()` (which triggers `seekToTime(0)` and `updateFrame()`) BEFORE assigning a value to `totalSec`. This caused `now >= totalSec` (e.g. 0 >= 0) to evaluate to true infinitely, crashing the JavaScript execution thread and preventing the UI from ever building the timeline or starting playback.
- **Fix / Resolution:** Moved the calculation of `totalSec` above the `seq` assignment and `stopPlayback()` call in `loadSequence()`. Also fixed a missing `togglePlay()` function definition.
- **Status:** Resolved
