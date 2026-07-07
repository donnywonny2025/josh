import json
import librosa
import numpy as np
import scipy.signal

MP3_PATH = '/Volumes/Extreme SSD/JOSH/Music/Master.mp3'
OUT_FILE = '/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/true_beats.json'

print("Extracting raw acoustic energy from Master.mp3...")
y, sr = librosa.load(MP3_PATH, sr=22050, duration=138.0)
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
times = librosa.times_like(onset_env, sr=sr)

# Find peaks with a minimum distance (e.g., at least 0.5 seconds apart so it's not a strobe light)
peaks, properties = scipy.signal.find_peaks(onset_env, distance=int(sr/512 * 0.5), prominence=0.5)

# Filter peaks to only those that occur between the Intro (5.03s) and Military section (138.3s)
valid_peaks = []
for p in peaks:
    if 5.033 < times[p] < 138.3:
        valid_peaks.append(p)
valid_peaks = np.array(valid_peaks)

# Sort those valid peaks by their raw acoustic energy (prominence)
peak_prominences = properties['prominences'][np.isin(peaks, valid_peaks)]
sorted_peak_indices = valid_peaks[np.argsort(peak_prominences)[::-1]]

# Take exactly the top 86 heaviest hits in the song to match our 86 photos
top_86_peaks = sorted_peak_indices[:86]

# Sort them back into chronological order
top_86_times = sorted(times[top_86_peaks])

output = {
    "tempo": "Dynamic Groove",
    "beats": [float(t) for t in top_86_times]
}

with open(OUT_FILE, "w") as f:
    json.dump(output, f, indent=4)

print(f"Generated {len(top_86_times)} dynamic groove cuts. Saved to {OUT_FILE}")
