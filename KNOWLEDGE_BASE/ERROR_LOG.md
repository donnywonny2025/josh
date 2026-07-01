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
