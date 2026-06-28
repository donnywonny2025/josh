# Josh Memorial — Project Context

## Overview
Memorial tribute project for Josh, Jeff's brother-in-law. Josh passed in 2026. He was a close, integral member of the family.

## Deliverables

### 1. Event Video
- **Purpose:** Plays once at the memorial event
- **Format:** Standalone video file (likely 1080p or 4K, TBD based on venue playback)
- **Content:** Curated photo slideshow with music, transitions, and pacing
- **Duration:** TBD — depends on photo count and music selection

### 2. Looping Slideshow  
- **Purpose:** Plays on loop during the gathering (before/after the event, reception, etc.)
- **Format:** Either a rendered loop video or a Premiere sequence set to loop
- **Content:** Broader selection of photos, possibly with softer music or ambient audio
- **Duration:** Designed to loop seamlessly

## Technical Approach
- **Pipeline:** Photo inventory → metadata extraction → sort by year → selects → XML sequence → Premiere import → render
- **XML Framework:** FCP7 XMEML (proven from Parker Hannifin project)
- **Adaptation:** This is a slideshow project (still photos), not multi-cam video. The XML will use still image clips with hold durations and transitions instead of video clips.

## Photo Inventory Status
- [ ] Photos collected from family
- [ ] Metadata extracted (EXIF dates, dimensions, orientations)
- [ ] Sorted by year/era
- [ ] Selects made for Event Video
- [ ] Selects made for Looping Slideshow

## Music Status
- [ ] Music selected for Event Video
- [ ] Music selected / ambient track for Looping Slideshow

## Key Decisions (TBD)
- Target resolution (1080p vs 4K)
- Target frame rate (23.976 vs 29.97 vs 30)
- Photo hold duration (default seconds per photo)
- Transition type (crossfade, dip to black, etc.)
- Title cards / text overlays needed?
- Event date (affects deadline)

## File Locations
```
/Volumes/Extreme SSD/JOSH/
├── Photos/
│   ├── RAW_IMPORTS/        ← Drop all source photos here first
│   ├── SORTED_BY_YEAR/     ← Auto-sorted after inventory scan
│   ├── SELECTS/            ← Curated picks for the sequences
│   └── PROCESSED/          ← Resized/color-corrected for timeline
├── Music/                  ← Audio tracks for the slideshow
├── Graphics/               ← Title cards, text overlays, logos
├── Exports/                ← Final rendered deliverables
├── Premiere/               ← Premiere project files
├── XML_Exports/            ← Generated FCP7 XML sequences
├── EDITING_FRAMEWORK/      ← Python scripts for inventory & XML gen
└── KNOWLEDGE_BASE/         ← This file + project intelligence
```
