import time
import subprocess

print("Starting 10-Second Test Render...")

goto_url("http://localhost:8123/player_v3")
wait_for_load()
js("if(playing) togglePlay();")
js("""
    const tl = document.querySelector('.timeline-wrapper');
    if(tl) tl.style.display = 'none';
    const nv = document.querySelector('.nav');
    if(nv) nv.style.display = 'none';
    const ct = document.querySelector('.controls');
    if(ct) ct.style.display = 'none';
""")

fps = 30
output_file = "/Volumes/Extreme SSD/JOSH/Exports/Test_10s_Render.mp4"
test_frames = 300

ffmpeg_cmd = [
    "ffmpeg", "-y", "-f", "image2pipe", "-vcodec", "png",
    "-framerate", str(fps), "-i", "-",
    "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-crf", "18",
    output_file
]

process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

start_time = time.time()
print(f"Rendering {test_frames} frames (10 seconds)...")

for frame in range(test_frames):
    now_sec = frame / fps
    js(f"updateFrame(true, {now_sec});")
    shot_path = capture_screenshot()
    with open(shot_path, "rb") as f:
        process.stdin.write(f.read())
        
    if frame % 30 == 0:
        elapsed = time.time() - start_time
        print(f"Rendered {frame}/{test_frames} frames... ({elapsed:.2f}s elapsed)")

print("Closing FFmpeg pipeline...")
process.stdin.close()
process.wait()

if process.returncode != 0:
    print("FFmpeg error:")
    print(process.stderr.read().decode())

print(f"Test render complete! Saved to {output_file}")
