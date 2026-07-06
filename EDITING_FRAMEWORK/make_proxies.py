import os
import subprocess
from pathlib import Path

# Paths
SOURCE_ROOT = Path('/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS')
PROXY_DIR = Path('/Volumes/Extreme SSD/JOSH/Photos/Proxies')
PROXY_DIR.mkdir(parents=True, exist_ok=True)

video_extensions = ('.mp4', '.mov', '.m4v', '.avi')

def make_proxies():
    print(f"Scanning for videos in {SOURCE_ROOT}...")
    
    videos = []
    for root, _, files in os.walk(SOURCE_ROOT):
        for f in files:
            if not f.startswith('.') and f.lower().endswith(video_extensions):
                videos.append(Path(root) / f)
                
    print(f"Found {len(videos)} videos.")
    print(f"Generating 480p silent proxies to {PROXY_DIR}...\n")
    
    for i, video_path in enumerate(videos, 1):
        out_name = f"{video_path.parent.name}____{video_path.name}"
        # replace spaces and weird characters to make it cleaner
        out_name = out_name.replace(" ", "_").replace("&", "and")
        
        out_path = PROXY_DIR / out_name
        
        if out_path.exists():
            print(f"[{i}/{len(videos)}] Proxy exists: {out_name}")
            continue
            
        print(f"[{i}/{len(videos)}] Rendering {out_name}...")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", "scale=-2:480",  # scale to 480p height, keep aspect ratio
            "-an",                  # remove audio (silent)
            "-c:v", "libx264",      # use h264 for fast encode and compatibility
            "-crf", "28",           # lower quality to save space/time
            "-preset", "veryfast",  # fast encoding
            str(out_path)
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"  ✅ Done.")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed: {e}")

if __name__ == '__main__':
    make_proxies()
