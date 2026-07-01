# Josh Memorial — Project Context

## The Core Video Arc
*(From Phyllis and family, outlining the chronological and thematic movement of the memorial video)*
1. **Baby & Toddler Years:** Early years and general movement of him growing up.
2. **Early School:** Early school friends and childhood.
3. **High School:** School dances, hanging out with friends.
4. **Military Years:** (This was his college). Time in the service, military buddies.
5. **The Brothers:** A dedicated segment for Ben and Josh's bond.
6. **Josh & Linsey:** Their marriage and their years together.
7. **The Last Few Years:** A mix of everybody: family and friends together.
*Note: General family photos of Josh will be sprinkled throughout the entire video.*

## Music Strategy & Phyllis's Directives
We are using the "Josh's Music" Spotify playlist (37 tracks). Phyllis explicitly mapped certain songs to specific photo folders/sections:
- **"He Ain't Heavy, He's My Brother" (The Hollies):** For the photos of Ben and Josh.
- **"Dancing in the Sky" (Dani and Lizzy):** For Josh having fun, dancing, travels.
- **"I'ma Warrior" (Soldier Hard):** For the military segment. *CRITICAL EDIT:* Eliminate the talking segment about Iraq at the beginning. Profanity is okay.
- **"Save a Place for Me" (Matthew West):** For the "save a place for me" folder featuring passed loved ones.
- **"Finally at Peace" (Juno Skye):** Requested for the end/closing sequence.
- **"Don't Cry When I'm Gone" (Tony Garcia):** General tribute.

*Phyllis's Creative License Note:* "I know you can't play all the songs in their entirety so I am deferring to you and your creativity to put it all together."

## Biographical Notes & Family Structure
Memorial tribute project for Josh, Jeff's brother-in-law. Josh passed in 2026. He was a close, integral member of the family.
When Josh was growing up, his family hosted foreign exchange students. Aunt Cindy was Josh's favorite aunt (Deceased).

**Immediate Family:**
- **Parents:** Dennis Burns and Phyllis Dowell
- **Siblings:** Ben Burns (older brother - Deceased) and Natalie Burns (sister)
- **Grandparents:** "Grandma Number Two" (Paternal Grandmother), Grandpa Burns (Paternal Grandfather)

**Extended Family & Friends:**
- Uncle Mike, Aunt Kristina, Aunt Cindy (Deceased), Aunt Diane
- Cousin Sarah, Cousin Faith, Cousin Lindsay, Cousin Joe, Cousin Steve, Cousin Brad, Cousin Kyle (Deceased), Cousin's Daughter, Bill (Deceased)
- Linsey Kerr (Wife), Jeff Kerr (Brother-in-law), Debbie Kerr
- Collin Mekan, Liz, Eric Hoffman, Annie Foreman, Mel (High School Friend), Ellen Parker, Carlton, Jon Burr, Marcy (Ben's widow, remarried), Wes, Lisa Burr.

## Identified Faces (Face ID Tracker)
The following individuals have been visually tagged and correlated into the `SORTED_BY_PERSON` directory:
- Josh Burns (variants: 1998, with mud on face, child)
- Dennis Burns, Phyllis Dowell, Ben Burns (child/adult), Natalie Burns
- Grandma Number Two, Grandpa Burns
- Linsey Kerr, Cousin Sarah, Cousin Faith, Uncle Mike, Aunt Kristina, Cousin Lindsay, Cousin Joe, Cousin Steve, Cousin Brad, Cousin Kyle, Cousin's Daughter
- Collin Mekan, Liz, Marcy, Wes, Lisa Burr, Bill, Foreign Exchange Student, Debbie Kerr, Aunt Cindy, Aunt Diane, Military Buddy, Eric Hoffman, Annie Foreman, Mel, Ellen Parker, Carlton, Jon Burr.
- Unknowns: Faces 104, 105, 106, 60, 66, 70, 71, 78, 80, 96, 100, 102.

## Deliverables & Technical Approach
**1. Event Video:** Standalone video file curated with music, transitions, and pacing. Length determined by 17.1-minute auto-generated limit.
**2. Looping Slideshow:** Plays on loop during gathering. Broader selection, ambient audio.

**Pipeline:**
- **1. Browser App (`player.html`):** Rapid prototyping, pacing math, and visual safe-margin framing.
- **2. XML Generation:** Compiling timing data into `memorial_sequence.xml`.
- **3. Premiere Pro:** Refining the timeline, adjusting pacing, and fine-tuning cuts.
- **4. After Effects:** Layering the intro, applying particles/lens flares, and subtle FX (without bogging down the main Premiere timeline).

## File Locations
- `/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS/`: Drop all source photos here first
- `/Volumes/Extreme SSD/JOSH/Photos/SORTED_BY_YEAR/`: Auto-sorted after inventory scan
- `/Volumes/Extreme SSD/JOSH/Music/`: Audio tracks (Spotify bulk downloads)
- `/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/`: Python scripts for XML generation
