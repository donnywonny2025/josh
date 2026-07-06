#!/usr/bin/env python3
"""
Josh Memorial — Clip Intelligence Ingestion Pipeline
=======================================================
Uploads 480p silent proxies to Gemini one at a time.
Returns structured JSON with visual analysis for every clip.

Usage:
  python3 ingest.py                    # Process all unanalyzed clips
  python3 ingest.py video.mp4          # Process specific clips only
"""

import os
import sys
import json
import time
import signal
from pathlib import Path
from google import genai
from google.genai import types

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PROJECT_DIR = Path("/Volumes/Extreme SSD/JOSH")
PROXY_DIR = PROJECT_DIR / "Photos" / "Proxies"
OUTPUT_FILE = PROJECT_DIR / "EDITING_FRAMEWORK" / "Clip_Intelligence.json"

# API Key (paid tier) ported from Parker Hannifin framework
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client = genai.Client(api_key=API_KEY)

# ─── ANALYSIS PROMPT ─────────────────────────────────────────────────────────
# Tags customized for Josh Memorial footage
PROMPT = """You are a highly perceptive, expert Documentary Assistant Editor logging raw, completely silent video footage for a memorial tribute video.
Your job is to provide extreme detail on what happens visually during this entire clip, specifically looking for the person we are memorializing (Josh).

Return a JSON object with this exact structure:
{
  "clip_id": "FILENAME_PLACEHOLDER",
  "subject_details": "Describe the main subject(s) in detail. Describe Josh if you see him. Focus on expressions, smiles, laughter, or interactions.",
  "environment": "Describe the location in detail.",
  "visual_timeline": [
    {
      "timecode_range": "00:00:00 - 00:00:05",
      "action_description": "Extremely detailed description of what happens during these seconds — specifically noting smiles, laughter, talking, or touching/hugs."
    }
  ],
  "thematic_tags": [
    "Select ALL relevant tags from this list: JOSH_VISIBLE, JOSH_SMILING, JOSH_LAUGHING, HUG, GROUP, INDIVIDUAL, ACTION, SPORTS, CANDID, POSED, EMOTIONAL, UPBEAT, OUTDOOR, INDOOR"
  ],
  "usability_flags": {
    "looks_at_camera": "boolean",
    "camera_shake": "boolean",
    "clean_window": "The single best timecode range (e.g. 00:00:05.000 - 00:00:12.500) where the shot features someone looking happy or a great candid moment."
  }
}

CRITICAL RULES:
- Break the visual_timeline into 5-second chunks covering the ENTIRE clip duration.
- Notice every subtle movement, gesture, expression change.
- You must output VALID JSON only. No markdown formatting around the output.
"""

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        clip_list = sys.argv[1:]
    else:
        clip_list = sorted([f.name for f in PROXY_DIR.iterdir() if f.suffix.upper() in (".MP4", ".MOV", ".AVI", ".M4V")])

    existing_data = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

    print(f"🎬 Josh Memorial — Clip Intelligence Pipeline")
    print(f"   Clips to process: {len(clip_list)}")
    print(f"   Already analyzed: {len(existing_data)}")
    print(f"   Output: {OUTPUT_FILE}")
    print("-" * 60)

    processed = 0
    skipped = 0

    for clip_name in clip_list:
        if clip_name in existing_data:
            print(f"⏭️  Skipping {clip_name} — already analyzed")
            skipped += 1
            continue

        proxy_path = PROXY_DIR / clip_name
        if not proxy_path.exists():
            print(f"⚠️  Proxy for {clip_name} not found! Skipping.")
            continue

        print(f"\n📤 Uploading {clip_name} to Gemini...")
        try:
            uploaded_file = client.files.upload(file=str(proxy_path))
        except Exception as e:
            print(f"❌ Upload failed for {clip_name}: {e}")
            continue

        while uploaded_file.state.name == "PROCESSING":
            print(f"   ⏳ Waiting for Google to process {clip_name}...", end="\r", flush=True)
            time.sleep(3)
            uploaded_file = client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            print(f"\n❌ Gemini failed to process {clip_name}")
            continue

        print(f"\n   👁️  Analyzing {clip_name}...")
        t0 = time.time()

        prompt_filled = PROMPT.replace("FILENAME_PLACEHOLDER", clip_name)

        max_retries = 3
        success = False

        def timeout_handler(signum, frame):
            raise TimeoutError("Gemini call timed out after 120s")
            
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        
        for attempt in range(max_retries):
            try:
                signal.alarm(120)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_uri(
                                    file_uri=uploaded_file.uri,
                                    mime_type=uploaded_file.mime_type
                                ),
                                types.Part.from_text(text=prompt_filled),
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.2
                    )
                )
                signal.alarm(0)

                if response.text is None:
                    raise ValueError("Gemini returned empty response (None) — retrying")
                raw = response.text.strip()
                if raw.startswith("```json"):
                    raw = raw[7:-3].strip()

                clip_data = json.loads(raw)
                existing_data[clip_name] = clip_data

                with open(OUTPUT_FILE, "w") as f:
                    json.dump(existing_data, f, indent=2)

                elapsed = time.time() - t0
                cw = clip_data.get("usability_flags", {}).get("clean_window", "N/A")
                tags = clip_data.get("thematic_tags", [])
                print(f"   ✅ {clip_name} analyzed in {elapsed:.1f}s")
                print(f"      Tags: {', '.join(tags)}")
                print(f"      Clean window: {cw}")
                success = True
                processed += 1
                break

            except (TimeoutError, Exception) as e:
                signal.alarm(0)
                err = str(e)
                if "503" in err or "429" in err or "empty response" in err or "timed out" in err:
                    wait = (attempt + 1) * 15
                    print(f"   ⚠️  Retryable error: {err[:60]}. Waiting {wait}s (retry {attempt+1}/{max_retries})...")
                    time.sleep(wait)
                else:
                    print(f"   ❌ Error analyzing {clip_name}: {e}")
                    break

        signal.signal(signal.SIGALRM, old_handler)

        try:
            client.files.delete(name=uploaded_file.name)
        except:
            pass

        print(f"   ⏳ Cooling down 15s before next clip...")
        time.sleep(15)

    print("\n" + "=" * 60)
    print(f"🎉 DONE — Processed: {processed} | Skipped: {skipped}")
    print(f"   Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
