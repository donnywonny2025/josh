import os
import subprocess
from pathlib import Path

PHOTOS_DIR = Path("../Photos/RAW_IMPORTS")
PROXIES_DIR = Path("../Proxies")

def main():
    if not PHOTOS_DIR.exists():
        print(f"Photos directory {PHOTOS_DIR} does not exist.")
        return

    PROXIES_DIR.mkdir(exist_ok=True)
    count = 0

    for d in sorted(PHOTOS_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith('.'):
            proxy_folder = PROXIES_DIR / d.name
            proxy_folder.mkdir(exist_ok=True)
            
            for f in sorted(d.iterdir()):
                if f.is_file() and not f.name.startswith('.'):
                    ext = f.suffix.lower()
                    if ext in ('.jpg','.jpeg','.png','.gif','.heic','.bmp','.tiff'):
                        out_file = proxy_folder / f.name
                        if not out_file.exists():
                            # Generate proxy using sips
                            subprocess.run([
                                'sips', '-Z', '200',
                                str(f),
                                '--out', str(out_file)
                            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            count += 1
                            print(f"Proxy created: {out_file.relative_to(PROXIES_DIR)}")
    
    print(f"Finished generating {count} proxies.")

if __name__ == "__main__":
    main()
