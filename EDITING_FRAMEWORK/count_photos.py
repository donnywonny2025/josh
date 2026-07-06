import os

p = '/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS'
dirs = [d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d))]

for d in sorted(dirs):
    dir_path = os.path.join(p, d)
    count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and not f.startswith('.')])
    print(f'{d}: {count} photos')
