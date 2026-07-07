import json

OUT_FILE = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/true_beats.json"
BPM = 100.0
# We use the official tempo from the web
sec_per_beat = 60.0 / BPM

# Starting at 0.0 seconds, generate 1000 strict metronome beats
beats = [i * sec_per_beat for i in range(1000)]

output = {
    "tempo": BPM,
    "beats": beats
}

with open(OUT_FILE, "w") as f:
    json.dump(output, f, indent=4)

print(f"Generated strict {BPM} BPM grid. Saved to {OUT_FILE}")
