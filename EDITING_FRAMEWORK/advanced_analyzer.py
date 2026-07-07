import json
import librosa
import numpy as np

MP3_PATH = "/Volumes/Extreme SSD/JOSH/Music/Master.mp3"
OUT_FILE = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/true_beats.json"

print(f"Loading first 145 seconds of {MP3_PATH}...")
# We only care about the early section (up to 138.3s). Load 145s for safety.
y, sr = librosa.load(MP3_PATH, sr=22050, duration=145.0)

print("Running strict onset envelope and tempo tracking...")
# Get the onset envelope to isolate the percussive hits
onset_env = librosa.onset.onset_strength(y=y, sr=sr)

# Prioritize the known tempo of ~103 BPM
prior_tempo = 103.36

# Run the beat tracker with HIGH tightness (100) to penalize any chaotic drifting
# This forces the algorithm to adhere strictly to the metronome pulse of the song
tempo, beat_frames = librosa.beat.beat_track(
    onset_envelope=onset_env,
    sr=sr,
    start_bpm=prior_tempo,
    tightness=100
)

# Convert frames to exact millisecond timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# Save the perfect grid
output = {
    "tempo": float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo),
    "beats": [float(b) for b in beat_times]
}

with open(OUT_FILE, "w") as f:
    json.dump(output, f, indent=4)

print(f"SUCCESS! Detected {len(beat_times)} flawless beats at ~{output['tempo']:.2f} BPM.")
print(f"Saved to {OUT_FILE}")
