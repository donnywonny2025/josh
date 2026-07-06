import json
import xml.etree.ElementTree as ET

# 1. Parse accurate audio track timings from Joshy_1.xml to get exact src_in cut points!
tree = ET.parse('/Volumes/Extreme SSD/JOSH/Exports/Joshy_1.xml')
root = tree.getroot()
seq = root.find('.//sequence')
rate = seq.find('.//rate/timebase')
timebase = 30 # The timeline is absolutely 30fps, regardless of what the sequence rate tag says

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

# Map beats directly to absolute timeline
master_beats = []
master_swells = []
processed_ranges = []
for seg in audio_segments:
    r = (seg['tl_start_sec'], seg['tl_end_sec'], seg['name'])
    if r in processed_ranges: continue
    processed_ranges.append(r)
    
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
master_swells = sorted(master_swells, key=lambda x: x['time'])

# 2. Perfect Schedule mapped to the new audio tracks
SCHEDULE = {
    'cards': {
        'Joshua Michael Burns': 5.04,
        'United States Navy Explosive Ordnance Disposal (EOD) Group Shot': 4.00,
        'A bond Between Brothers': 4.00,
        'Remembering The Moments': 4.00,
        'Until We Meet Again': 5.00,
        'Rope Swing': 5.00
    },
    'sections': {
        'Early Pictures': {'start': 5.04, 'end': 72.37},
        'Family, High School': {'start': 72.37, 'end': 134.33},
        'Military Picts': {'start': 138.33, 'end': 198.33},
        'Ben and Josh': {'start': 202.33, 'end': 276.77},
        'Linsey and Josh': {'start': 280.77, 'end': 316.27},
        'Celebrate Life': {'start': 316.27, 'end': 387.27}
    }
}

new_slides = []
current_sec_name = None
current_sec_photos = []

def process_section(name, photos):
    if not photos: return
    meta = SCHEDULE['sections'].get(name)
    if not meta:
        new_slides.extend(photos)
        return
        
    s_start = meta['start']
    s_end = meta['end']
    
    valid_beats = [b for b in master_beats if s_start <= b <= s_end]
    needed = len(photos) - 1
    if needed > 0 and len(valid_beats) >= needed:
        step = max(1, len(valid_beats) / (needed + 1))
        transition_times = [valid_beats[int(i * step)] for i in range(1, needed + 1)]
    else:
        transition_times = [s_start + i * ((s_end - s_start) / len(photos)) for i in range(1, len(photos))]

    current_time = s_start
    for i, p in enumerate(photos):
        next_t = transition_times[i] if i < len(transition_times) else s_end
        dur = next_t - current_time
        p['duration_sec'] = round(dur, 4)
        p['duration_frames'] = int(round(dur * 30))
        new_slides.append(p)
        current_time = next_t

# Iterate timeline items
for sl in master_tl['slides']:
    if sl.get('isCard'):
        process_section(current_sec_name, current_sec_photos)
        current_sec_name = None
        current_sec_photos = []
        
        title_lines = sl.get('title', '').split('\n')
        key = title_lines[0].strip() if title_lines else ''
        if 'Remembering' in key: key = 'Remembering The Moments'
        if 'United States' in key: key = 'United States Navy Explosive Ordnance Disposal (EOD) Group Shot'
        
        dur_sec = SCHEDULE['cards'].get(key, 5.0)
        sl['duration_sec'] = dur_sec
        sl['duration_frames'] = int(round(dur_sec * 30))
        new_slides.append(sl)
    else:
        sec_name = sl.get('sectionName')
        if current_sec_name and current_sec_name == sec_name:
            current_sec_photos.append(sl)
        else:
            process_section(current_sec_name, current_sec_photos)
            current_sec_name = sec_name
            current_sec_photos = [sl]

process_section(current_sec_name, current_sec_photos)

with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/sequences/master_timeline.json', 'w') as f:
    json.dump({'slides': new_slides}, f, indent=4)

print("Timeline successfully beat-mapped with flawless src_in alignment and accurate 30fps durations!")
