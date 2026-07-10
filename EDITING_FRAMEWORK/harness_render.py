import time
import subprocess

print("Starting Browser Harness Render Pipeline...")

# Make sure we are on the right tab
goto_url("http://localhost:8123/player_v3")
wait_for_load()

# Pause native playback
js("if(playing) togglePlay();")

# Hide UI
js("""
    const tl = document.querySelector('.timeline-wrapper');
    if(tl) tl.style.display = 'none';
    const nv = document.querySelector('.nav');
    if(nv) nv.style.display = 'none';
    const ct = document.querySelector('.controls');
    if(ct) ct.style.display = 'none';
""")

fps = 30
output_file = "/Volumes/Extreme SSD/JOSH/Exports/Slideshow_V3_Render.mp4"

# Launch FFmpeg to encode the screenshots from stdin
ffmpeg_cmd = [
    "ffmpeg",
    "-y",
    "-f", "image2pipe",
    "-vcodec", "png",
    "-framerate", str(fps),
    "-i", "-",
    "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    output_file
]

process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

# Get total seconds dynamically from the web player
total_sec = float(js("totalSec"))
total_frames = int(total_sec * fps)

start_time = time.time()
print(f"Rendering {total_frames} frames ({total_sec} seconds)...")

for frame in range(total_frames):
    now_sec = frame / fps
    # Step the player logic
    js(f"updateFrame(true, {now_sec});")
    
    # Capture screenshot to temp file using browser-harness built-in function
    shot_path = capture_screenshot()
    
    # Read binary and pipe to ffmpeg
    with open(shot_path, "rb") as f:
        process.stdin.write(f.read())
        
    if frame % 30 == 0:
        elapsed = time.time() - start_time
        print(f"Rendered {frame}/{total_frames} frames... ({elapsed:.2f}s elapsed)")

print("Closing FFmpeg pipeline...")
process.stdin.close()
process.wait()

if process.returncode != 0:
    print("FFmpeg error:")
    print(process.stderr.read().decode())

print(f"Render complete! Saved to {output_file}")
print(f"Time taken: {time.time() - start_time:.2f} seconds.")
