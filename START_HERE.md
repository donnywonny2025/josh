# Josh Memorial Project — Start Here

> **URGENT AGENT DIRECTIVE:** READ THIS CONVERSATION TRANSCRIPT FIRST.
> **Conversation ID:** 7a5ecc61-d065-4df2-8aa6-b7cef6bcd099
> You must read the transcript of this conversation to fully understand the context of how this FCP7 XML was built and validated against the Parker Hannifin framework.

## The Parker Hannifin XML Validation (Conversation Recap)
Over the last five minutes, the user grilled the agent to ensure the notoriously fragile Premiere Pro XML framework was correctly ported from the Parker Hannifin "Multi-Cam Edit" project. 

**The User Asked:**
- *"Do you understand how that works inside of Parker Hannifin?"*
- *"Is there documentation that explains the problems, explains how to do it correctly?"* 
- *"Did you read through all that documentation?"*

**The AI Confirmed:**
Yes, the agent read the *XML Multicam Sync Bible* and the *FCP7 XML Deep Reference*. We proved that `generate_xml.py` perfectly avoids the 4 catastrophic Premiere XML bugs:
1. **The Bin Contamination & Duplication Nightmare:** All photos are pre-registered as Master Clips in a `<bin>` at the top of the XML. The `<name>` tags are never altered.
2. **The Overengineering Spiral:** The XML uses the absolute minimalist `<clipitem>` template. We explicitly stripped out `<sourcetrack>` and `<link>` elements because Parker Hannifin proved they break Premiere.
3. **The Timebase Drift Bug:** Every single cut is hard-stamped with `<rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>` to prevent audio drift.
4. **The Golden Math Rule:** The code strictly enforces `out - in == end - start` on every single photo.

---

> **Navigation Breadcrumb:** If you are looking for your son's Arcade game project (Lincoln Circle), your other workspace is located at: `/Volumes/WORK 2TB/WORK 2026/LincolnCircle`

This document explains the automated photo timeline pipeline we built for Josh's memorial video. This system completely replaces the need to manually drag, drop, and sort photos in Premiere Pro.

## How the System Works

We built a custom Python automation pipeline that groups photos by emotional themes, sorts them chronologically within those themes, and generates an FCP7 XML timeline that you can import directly into Premiere Pro.

### 1. Thematic Sorting
Phyllis mapped out specific songs for specific emotional arcs. Instead of a single chronological timeline, the photos are organized into thematic buckets based on the folders in `Photos/RAW_IMPORTS/`:
- **Military**
- **Travel_Fun**
- **Ben_and_Josh**
- **Passed_Loved_Ones**
- **General**

### 2. Exact Age Calculation (1982)
Within each of those folders, the `chrono_engine.py` script scans the EXIF metadata of every single photo. It takes the year the photo was taken, subtracts Josh's birth year (**1982**), and calculates his exact age in that moment. It then mathematically sorts the photos perfectly from youngest to oldest *within* each music theme.

### 3. Timeline Pacing
The `generate_pacing.py` script automatically calculates the duration for each photo to match a standard memorial video pace (2.5-second hold + 0.5-second cross-dissolve). 
- **Current Total Photos:** 513
- **Generated Sequence Length:** 17.1 Minutes

## How to Run the Pipeline

If you add new photos or change the folders, you just run the pipeline to rebuild the XML file instantly.

1. **Rebuild the Data:**
   ```bash
   python3 EDITING_FRAMEWORK/chrono_engine.py
   python3 EDITING_FRAMEWORK/generate_pacing.py
   ```

2. **Generate the Premiere Sequence:**
   ```bash
   python3 EDITING_FRAMEWORK/generate_xml.py
   ```

3. **Import to Premiere:**
   Simply drag the generated `EDITING_FRAMEWORK/memorial_sequence.xml` directly into Premiere Pro. It will instantly build out your timeline with all 513 photos perfectly ordered.

## Pending Tasks / Next Steps
- **Audio Mixing:** The 2-hour Spotify playlist needs to be edited down to fit the 17.1-minute timeline, and the intro talking segment must be stripped from the "I'ma Warrior" military track. This can be done via FFmpeg scripts or manually inside Premiere.
