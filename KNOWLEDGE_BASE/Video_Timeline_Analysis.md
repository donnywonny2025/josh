# Joshy.mp4 Master Timeline Analysis
*Analyzed on 2026-07-06*

## Overview
I have fully analyzed the exported `Joshy.mp4` file. This video provides the master blueprint for the memorial's pacing, musical flow, and chapter transitions. It is exactly 8 minutes and 15 seconds long. The music is an acoustic, emotional ballad with vocals that perfectly matches the reflective, honorable tone of a memorial video. 

## The Timeline Structure
The video uses stark, white-on-black title cards to demarcate the sections. Here is the exact timecode breakdown of every structural element in the edit:

- **00:00 - 00:04:** `Joshua Michael Burns` (Intro Title Card)
- **00:04 - 01:12:** `Early Pictures` 
- **01:12 - 02:47:** `Family, High School`
- **02:47 - 02:57:** `United States Navy Explosive Ordnance Disposal (EOD) Group Shot` 
- **02:57 - 04:07:** `Military Picts`
- **04:07 - 04:13:** `A bond Between Brothers` 
- **04:13 - 05:45:** `Ben and Josh`
- **05:45 - 05:56:** `Remembering The Moments (July 8th 1982 - January 20th 2026)`
- **05:56 - 06:25:** `Linsey And Josh`
- **06:25 - 07:53:** `Celebrate Life`
- **07:53 - 08:04:** `Joshua Michael Burns Until We Meet Again`
- **08:04 - 08:15:** `Rope Swing` (The emotional close-out)

## Impact on the Builder/Player V2
1. **The Flow is Locked:** The timing of the music and the placement of these title cards is clearly set in stone. This confirms our architectural shift to a single `master_timeline.json` is the correct path.
2. **Audio Sync:** I have already successfully extracted the audio track from this MP4 file into `Master.mp3`. The V2 player will run perfectly synced to this 8:15 track.
3. **Pacing Constraints:** Because the time block between `Early Pictures` (00:04) and the `EOD Group Shot` (02:47) is exactly 2 minutes and 43 seconds (163 seconds), if we use a default photo duration of 5 seconds, we know exactly how many photos we need to fill that section (approx. 32 photos). This gives us mathematical constraints for the photo pool!
