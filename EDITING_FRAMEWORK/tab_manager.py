#!/usr/bin/env python3
"""
Josh Memorial — Tab Management System
Enforces the One-Tab Rule and kills stale about:blank tabs securely via Browser Harness CDP.
"""

import subprocess
import sys

SCRIPT = """
import sys

tabs = list_tabs()
closed = 0
seen = {}

for tab in tabs:
    url = tab.get('url', '')
    tid = tab.get('targetId')
    
    if url == 'about:blank':
        print(f"[-] Closing empty tab (about:blank) [{tid}]")
        cdp("Target.closeTarget", targetId=tid)
        closed += 1
        continue
        
    base = url.split('?')[0].rstrip('/')
    if 'localhost:8080' in base:
        if base in seen:
            print(f"[-] Closing duplicate: {url} [{tid}]")
            cdp("Target.closeTarget", targetId=tid)
            closed += 1
        else:
            seen[base] = tid

if closed > 0:
    print(f"[✔] Tab sanitation complete. Closed {closed} tabs.")
else:
    print("[✔] Tab environment is clean. No duplicates or blanks found.")
"""

def sanitize_tabs():
    try:
        subprocess.run(["browser-harness", "-c", SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Tab Manager failed to execute Browser Harness: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("--- Browser Harness Tab Manager ---")
    sanitize_tabs()
