# Josh Memorial — Operating Rules

> **Read this FIRST before doing any work in this project.**

---

## R1. Timers On Everything

Every task gets a timer. If I kick off a background process, scan, render, or anything async — I set a timer so I never go silent. The user should never have to wonder "is it still running?" or "did it forget about me?"

- Background commands → timer for expected duration
- Waiting on user input → no timer needed (system auto-wakes)
- Multi-step workflows → timer between each step
- **No exceptions.** Every action chain ends either with a completed result or a timer that brings me back.

---

## R2. Browser Harness For All Browser Work

All browser interaction uses Browser Harness (CDP), never `browser_subagent`.

### Quick Reference

```bash
# Basic usage pattern
browser-harness -c "
new_tab('https://example.com')
wait_for_load()
print(page_info())
"
```

### Key Functions
| Function | Purpose |
|----------|---------|
| `new_tab(url)` | Opens a NEW tab (use ONLY for first navigation) |
| `goto_url(url)` | Navigate WITHIN existing tab (use for all subsequent navs) |
| `wait_for_load()` | Poll until document.readyState == 'complete' |
| `page_info()` | Returns {url, title, w, h, sx, sy, pw, ph} |
| `capture_screenshot(path)` | Save PNG screenshot (auto-versioned with timestamp) |
| `click_at_xy(x, y)` | Compositor-level click (works through iframes/shadow DOM) |
| `type_text(text)` | Insert text at focus |
| `press_key(key, modifiers)` | Key events (modifiers: 1=Alt, 2=Ctrl, 4=Meta, 8=Shift) |
| `scroll(x, y, dy)` | Mouse wheel scroll at position |
| `js(expression)` | Execute JavaScript in attached tab |
| `list_tabs()` | All CDP page targets |
| `switch_tab(target_id)` | Attach + activate a tab |
| `ensure_real_tab()` | Recover from stale/internal tabs |
| `current_tab()` | Get attached tab info |
| `http_get(url)` | Pure HTTP fetch (no browser needed) |

### Context-Aware Tab Navigation
- **Run Tab Manager:** ALWAYS run `python3 /Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/tab_manager.py` to securely close `about:blank` and enforce "One Unique Instance per App".
- **NEVER use `goto_url()` to overwrite an active tool:** The user relies on a dual-monitor multi-tab workflow.
- **Navigation Protocol:** When opening a URL, first check `list_tabs()`. If it exists, use `switch_tab(targetId)`. If it does not exist, use `new_tab(url)`. Only use `goto_url()` if you are explicitly navigating *within* an already correct context.
- **Screenshots to artifacts directory, never /tmp.**

### Screenshots Path
All screenshots save to the conversation artifacts directory:
```
/Users/jeffkerr/.gemini/antigravity-ide/brain/{conversation-id}/
```

### Connection Recovery
```python
# If tab goes stale:
ensure_real_tab()

# If daemon is dead:
ensure_daemon()  # auto-called by run.py
```

---

## R3. File Names Are Sacred

Source filenames (photos, music, any media) are NEVER changed. They are the anchor for:
- Absolute paths in XML
- Premiere media linking
- Inventory tracking
- Metadata association

Sequence names, labels, and organizational names can change freely.

---

## R4. Everything Stays On The Project Drive

All media lives under `/Volumes/Extreme SSD/JOSH/`. Never reference files from Desktop, Downloads, or other drives. If new photos arrive, they go into `Photos/RAW_IMPORTS/`.

All `pathurl` values in generated XML are absolute to this drive.

---

## R5. Auto-Version Everything

Never overwrite XML files or generated outputs. Every run creates a versioned file:
```
Josh_Memorial_v{N}_{timestamp}.xml
```

---

## R6. Show, Don't Tell

When building anything visual — use Browser Harness to open and verify it. Take a screenshot and show the user. Never say "open the link" — handle it autonomously.

---

## R7. Document Every Mistake

Errors get logged in `KNOWLEDGE_BASE/ERROR_LOG.md` with severity, details, fix, and status.
