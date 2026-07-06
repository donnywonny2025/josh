import os

p = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'
dirs = [d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d))]

video_extensions = ('.mp4', '.mov', '.m4v', '.avi')
total_videos = 0

print("Video counts by section:")
for d in sorted(dirs):
    dir_path = os.path.join(p, d)
    videos = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.lower().endswith(video_extensions) and not f.startswith('.')]
    count = len(videos)
    if count > 0:
        print(f'{d}: {count} videos')
    total_videos += count

print(f"\nTotal video files across all folders: {total_videos}")
