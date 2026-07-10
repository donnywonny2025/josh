import asyncio
import os
import subprocess
import time
from playwright.async_api import async_playwright

async def render_video():
    print("Starting Playwright to render MP4...")
    
    # We want exactly 1080p, 30fps
    fps = 30
    width = 1920
    height = 1080
    
    output_file = "/Volumes/Extreme SSD/JOSH/Exports/Slideshow_V3_Render.mp4"
    
    # Launch ffmpeg
    # -y overwrites existing file
    # -f image2pipe forces input format to be a stream of images
    # -framerate sets the input frame rate
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "image2pipe",
        "-vcodec", "png",
        "-framerate", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        output_file
    ]
    
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 16:9 1080p viewport
        page = await browser.new_page(viewport={"width": width, "height": height})
        
        print("Navigating to V3 player...")
        await page.goto("http://localhost:8123/player_v3")
        
        # Wait for the images to load initially
        await page.wait_for_timeout(3000)
        
        # We need to pause the native playback and take control
        await page.evaluate("if(playing) togglePlay();")
        
        # Hide the timeline UI so it doesn't get recorded
        await page.evaluate("""
            const tl = document.querySelector('.timeline-wrapper');
            if(tl) tl.style.display = 'none';
            const nv = document.querySelector('.nav');
            if(nv) nv.style.display = 'none';
            const ct = document.querySelector('.controls');
            if(ct) ct.style.display = 'none';
        """)
        
        # We will render exactly 10 seconds of footage (300 frames) for testing
        test_frames = 300
        print(f"Rendering {test_frames} frames (10 seconds)...")
        
        start_time = time.time()
        for frame in range(test_frames):
            # Advance the javascript engine exactly 1 frame (1/30th of a second)
            now_sec = frame / fps
            await page.evaluate(f"updateFrame(true, {now_sec});")
            
            # Capture the DOM to PNG byte buffer
            screenshot_bytes = await page.screenshot(type="png")
            
            # Pipe bytes directly into FFmpeg
            process.stdin.write(screenshot_bytes)
            
            if frame % 30 == 0:
                print(f"Rendered {frame}/{test_frames} frames...")
                
        print("Closing browser and flushing FFmpeg...")
        await browser.close()
        
    process.stdin.close()
    stderr_output = process.stderr.read().decode('utf-8')
    process.wait()
    
    print(f"Render complete! Saved to {output_file}")
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(render_video())
