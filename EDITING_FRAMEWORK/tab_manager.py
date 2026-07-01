#!/usr/bin/env python3
"""
Josh Memorial — Tab Management System
Enforces the Context-Aware Multi-Tab Rule: "One Unique Instance per App"
Kills stale about:blank tabs and deduplicates tabs based on their base URL.
"""

import subprocess
import sys

SCRIPT = """
import sys
from urllib.parse import urlparse

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
        
    # Group by base URL scheme + netloc + path (ignores query params like ?seq=X or ?q=X)
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    except Exception:
        base = url.split('?')[0].rstrip('/')
        
    if base in seen:
        print(f"[-] Closing duplicate: {url} [{tid}]")
        cdp("Target.closeTarget", targetId=tid)
        closed += 1
    else:
        seen[base] = tid

if closed > 0:
    print(f"[✔] Tab sanitation complete. Closed {closed} duplicate tabs.")
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
    print("--- Browser Harness Tab Manager (Context-Aware) ---")
    sanitize_tabs()
