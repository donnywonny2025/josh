import json
import librosa
import numpy as np
from pathlib import Path

# Extract audio paths directly from the timeline logic
audio_tracks = {
    "YouTube_Version_The Ballad Of Buster Scruggs Soundtrack - \"How Deep\" - Carter Burwell.mp3": "/Volumes/Extreme SSD/JOSH/Music/Jeffs selects/YouTube_Version_The Ballad Of Buster Scruggs Soundtrack - ＂How Deep＂ - Carter Burwell.mp3",
    "The Hollies - He Ain't Heavy He's My Brother - 2003 Remaster..mp3": "/Volumes/Extreme SSD/JOSH/Music/The Hollies - He Ain't Heavy He's My Brother - 2003 Remaster.{ext}.mp3" 
}

out_file = Path('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/audio_beat_map.json')
if out_file.exists():
    output_data = json.loads(out_file.read_text())
else:
    output_data = {}

for name, path_str in audio_tracks.items():
    p = Path(path_str)
    
    # Try with .mp3 if the original doesn't exist
    if not p.exists():
        if '{ext}' in p.name:
            p = p.with_name(p.name.replace('{ext}', ''))
            
    print(f"Processing: {p.name}")
    if not p.exists():
        print(f"  [!] NOT FOUND: {p}")
        continue
        
    # Load audio
    print(f"  Loading audio...")
    y, sr = librosa.load(str(p), sr=22050) # Standard sample rate
    
    # 1. Beat Detection
    print(f"  Extracting beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # 2. RMS Energy (Swells)
    print(f"  Calculating RMS energy swells...")
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
    
    # Find local maxima in RMS (swells)
    # A simple peak picking algorithm
    import scipy.signal
    peaks, _ = scipy.signal.find_peaks(rms, distance=sr//hop_length) # at least 1s apart
    
    # Sort peaks by energy
    peak_times = times[peaks]
    peak_energies = rms[peaks]
    
    # Store top 200 swells for this song
    swell_data = sorted(zip(peak_times, peak_energies), key=lambda x: x[1], reverse=True)[:200]
    
    output_data[name] = {
        'tempo': float(tempo) if isinstance(tempo, (float, np.float32, np.float64)) else float(tempo[0]),
        'beats': [float(b) for b in beat_times],
        'swells': [{'time': float(t), 'energy': float(e)} for t, e in swell_data]
    }

out_file = Path('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/audio_beat_map.json')
out_file.write_text(json.dumps(output_data, indent=2))
print(f"\\nSaved beat and swell data to {out_file.name}")
