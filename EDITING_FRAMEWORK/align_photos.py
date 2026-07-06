import json
import xml.etree.ElementTree as ET

# 1. Parse accurate audio track timings
tree = ET.parse('/Volumes/Extreme SSD/JOSH/Exports/Joshy_1.xml')
root = tree.getroot()
seq = root.find('.//sequence')
rate = seq.find('.//rate/timebase')
timebase = int(rate.text) if rate is not None else 30

audio_segments = []
for track in seq.findall('.//audio/track'):
    for clip in track.findall('.//clipitem'):
        name_node = clip.find('name')
        if name_node is None or '.mp3' not in name_node.text:
            continue
            
        start_node = clip.find('start')
        end_node = clip.find('end')
        in_node = clip.find('in')
        out_node = clip.find('out')
        
        if start_node is None or in_node is None: continue
        
        s_val = int(start_node.text)
        e_val = int(end_node.text)
        in_val = int(in_node.text)
        out_val = int(out_node.text)
        
        clip_dur = out_val - in_val
        
        if s_val == -1 and e_val != -1:
            s_val = e_val - clip_dur
        elif e_val == -1 and s_val != -1:
            e_val = s_val + clip_dur
        elif s_val == -1 and e_val == -1:
            continue
            
        clean_name = name_node.text.replace('{ext}', '')
        
        audio_segments.append({
            'name': clean_name,
            'tl_start_sec': s_val / timebase,
            'tl_end_sec': e_val / timebase,
            'src_in_sec': in_val / timebase,
            'src_out_sec': out_val / timebase
        })

# Load the beat map and master timeline
with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/audio_beat_map.json') as f:
    beat_map = json.load(f)
    
with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json') as f:
    master_tl = json.load(f)

# Build a list of all absolute beat and swell timestamps on the master timeline
master_beats = []
master_swells = []

# To avoid duplicate tracks (FCP has stereo tracks A and B), keep track of processed ranges
processed_ranges = []
for seg in audio_segments:
    # Check if this exact range was already processed
    r = (seg['tl_start_sec'], seg['tl_end_sec'], seg['name'])
    if r in processed_ranges: continue
    processed_ranges.append(r)
    
    # Map beats and swells from this segment
    data = beat_map.get(seg['name'], {})
    beats = data.get('beats', [])
    swells = data.get('swells', [])
    
    for b in beats:
        if seg['src_in_sec'] <= b <= seg['src_out_sec']:
            offset = b - seg['src_in_sec']
            master_beats.append(seg['tl_start_sec'] + offset)
            
    for s in swells:
        t = s['time']
        if seg['src_in_sec'] <= t <= seg['src_out_sec']:
            offset = t - seg['src_in_sec']
            master_swells.append({
                'time': seg['tl_start_sec'] + offset,
                'energy': s['energy']
            })

master_beats = sorted(list(set(master_beats)))
# Swells might have exact duplicate times if stereo tracks merged, but let's just sort
master_swells = sorted(master_swells, key=lambda x: x['time'])

# Group photos in master timeline by section
sections = []
current_sec = None
current_sec_photos = []

for sl in master_tl['slides']:
    if sl.get('isCard') or sl.get('isPlaceholder'):
        if current_sec:
            sections.append(current_sec)
        sections.append({'type': 'card', 'slide': sl})
        current_sec = None
    else:
        sec_name = sl.get('sectionName')
        if current_sec and current_sec['name'] == sec_name:
            current_sec['photos'].append(sl)
        else:
            if current_sec: sections.append(current_sec)
            current_sec = {'type': 'section', 'name': sec_name, 'photos': [sl]}
if current_sec: sections.append(current_sec)

# Layout mapping based on Joshy_1.xml
LAYOUT = [
    {'name': 'Early Pictures', 'start': 5.04, 'end': 71.50},
    {'name': 'Family, High School', 'start': 71.50, 'end': 167.79},
    {'name': 'Military Picts', 'start': 177.96, 'end': 247.62},
    {'name': 'Ben and Josh', 'start': 253.29, 'end': 345.96},
    {'name': 'Linsey and Josh', 'start': 356.42, 'end': 385.50},
    {'name': 'Celebrate Life', 'start': 385.50, 'end': 473.62}
]
layout_dict = {x['name']: x for x in LAYOUT}

new_slides = []
for sec in sections:
    if sec['type'] == 'card':
        new_slides.append(sec['slide'])
        continue
        
    sec_name = sec['name']
    photos = sec['photos']
    if not photos: continue
    
    meta = layout_dict.get(sec_name)
    if not meta:
        new_slides.extend(photos)
        continue
        
    s_start = meta['start']
    s_end = meta['end']
    
    if sec_name == 'Military Picts':
        # Snap to SWELLS
        valid_swells = [s for s in master_swells if s_start <= s['time'] <= s_end]
        # Remove duplicates
        unique_swells = []
        last_t = -1
        for s in valid_swells:
            if s['time'] - last_t > 0.1:
                unique_swells.append(s)
                last_t = s['time']
        
        # Sort by energy and take top N (where N = len(photos) - 1)
        needed = len(photos) - 1
        if needed > 0 and len(unique_swells) >= needed:
            top_swells = sorted(unique_swells, key=lambda x: x['energy'], reverse=True)[:needed]
            transition_times = sorted([s['time'] for s in top_swells])
        else:
            # fallback to evenly spaced if not enough swells
            transition_times = [s_start + i * ((s_end - s_start) / len(photos)) for i in range(1, len(photos))]
            
    else:
        # Snap to BEATS
        valid_beats = [b for b in master_beats if s_start <= b <= s_end]
        needed = len(photos) - 1
        
        if needed > 0 and len(valid_beats) >= needed:
            # We want to evenly space the photos across the available beats
            # e.g. if we have 100 beats and 20 photos, we pick every 5th beat
            step = max(1, len(valid_beats) / (needed + 1))
            transition_times = [valid_beats[int(i * step)] for i in range(1, needed + 1)]
        else:
            transition_times = [s_start + i * ((s_end - s_start) / len(photos)) for i in range(1, len(photos))]

    # Now calculate durations based on transition times
    current_time = s_start
    for i, p in enumerate(photos):
        if i < len(transition_times):
            next_t = transition_times[i]
        else:
            next_t = s_end
            
        dur = next_t - current_time
        p['duration_sec'] = round(dur, 4)
        p['duration_frames'] = round(dur * 24)
        new_slides.append(p)
        current_time = next_t

with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json', 'w') as f:
    json.dump({'slides': new_slides}, f, indent=4)

print("Timeline successfully beat-mapped!")
