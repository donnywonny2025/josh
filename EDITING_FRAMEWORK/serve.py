#!/usr/bin/env python3
"""Josh Memorial — Local Photo Server v2
Serves photo browser, sequence builder, player + APIs.
"""
import http.server
import json
import os
import socketserver
import urllib.parse
from datetime import datetime
from pathlib import Path

PORT = 8080
PROJECT = Path("/Volumes/Extreme SSD/JOSH")
PHOTOS = PROJECT / "Photos" / "RAW_IMPORTS"
FRAMEWORK = PROJECT / "EDITING_FRAMEWORK"
MARKS_FILE = FRAMEWORK / "marks.json"
SEQUENCES_DIR = FRAMEWORK / "sequences"
SEQUENCES_DIR.mkdir(exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        
        # --- PAGE ROUTES ---
        if path == "/" or path == "/index.html" or path == "/browser":
            return self._serve_file(FRAMEWORK / "app.html", "text/html")
        if path == "/builder":
            return self._serve_file(FRAMEWORK / "builder.html", "text/html")
        if path == "/player":
            return self._serve_file(FRAMEWORK / "player.html", "text/html")
        if path == "/faces":
            return self._serve_file(FRAMEWORK / "faces.html", "text/html")
        
        # --- FOLDER/PHOTO APIs ---
        if path == "/api/folders":
            folders = []
            for d in sorted(PHOTOS.iterdir()):
                if d.is_dir() and not d.name.startswith('.'):
                    files = [f.name for f in d.iterdir() if f.is_file() and not f.name.startswith('.')]
                    photos = [f for f in files if any(f.lower().endswith(e) for e in ('.jpg','.jpeg','.png','.gif','.heic','.bmp','.tiff'))]
                    videos = [f for f in files if any(f.lower().endswith(e) for e in ('.mov','.mp4','.m4v'))]
                    folders.append({"name": d.name, "photos": len(photos), "videos": len(videos), "total": len(photos) + len(videos)})
            return self._json(folders)
        
        if path.startswith("/api/photos/"):
            folder_name = path[len("/api/photos/"):]
            folder_path = PHOTOS / folder_name
            if folder_path.is_dir():
                files = []
                for f in sorted(folder_path.iterdir()):
                    if f.is_file() and not f.name.startswith('.'):
                        ext = f.suffix.lower()
                        ftype = "photo" if ext in ('.jpg','.jpeg','.png','.gif','.bmp','.tiff') else \
                                "video" if ext in ('.mov','.mp4','.m4v') else \
                                "heic" if ext == '.heic' else "other"
                        files.append({"name": f.name, "type": ftype, "size_kb": f.stat().st_size // 1024, "ext": ext})
                return self._json(files)
            return self._json({"error": "not found"}, 404)
        
        # --- MARKS API ---
        if path == "/api/marks":
            marks = json.loads(MARKS_FILE.read_text()) if MARKS_FILE.exists() else {}
            return self._json(marks)
        
        # --- MASTER DATA API ---
        if path == "/api/master":
            md = FRAMEWORK / "master_data.json"
            return self._json(json.loads(md.read_text()) if md.exists() else {})
        
        # --- FACE LABELS API ---
        if path == "/api/face-labels":
            labels_file = FRAMEWORK / "face_data" / "face_labels.json"
            return self._json(json.loads(labels_file.read_text()) if labels_file.exists() else {})

        
        # --- SEQUENCE APIs ---
        if path == "/api/sequences":
            seqs = []
            for f in sorted(SEQUENCES_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text())
                    seqs.append({
                        "id": f.stem,
                        "name": data.get("name", f.stem),
                        "section_id": data.get("section_id"),
                        "slides": len(data.get("slides", [])),
                        "modified": data.get("modified", ""),
                        "total_duration": sum(s.get("duration_sec", data.get("default_duration_sec", 5)) for s in data.get("slides", []))
                    })
                except:
                    pass
            return self._json(seqs)
        
        if path.startswith("/api/sequences/"):
            seq_id = path[len("/api/sequences/"):]
            seq_file = SEQUENCES_DIR / f"{seq_id}.json"
            if seq_file.exists():
                return self._json(json.loads(seq_file.read_text()))
            return self._json({"error": "not found"}, 404)
        
        # --- SERVE MUSIC ---
        if path.startswith("/music/"):
            rel = urllib.parse.unquote(path[len("/music/"):])
            file_path = PROJECT / "Music" / rel
            if file_path.is_file():
                self.send_response(200)
                ct = self._content_type(file_path.suffix.lower())
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(file_path.stat().st_size))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(file_path, "rb") as fh:
                    self.wfile.write(fh.read())
                return
            self.send_error(404)
            return
            
        # --- SERVE PHOTOS ---
        if path.startswith("/photos/"):
            rel = path[len("/photos/"):]
            file_path = PHOTOS / rel
            if file_path.is_file():
                self.send_response(200)
                ct = self._content_type(file_path.suffix.lower())
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(file_path.stat().st_size))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                with open(file_path, "rb") as fh:
                    self.wfile.write(fh.read())
                return
            self.send_error(404)
            return
        
        # --- SERVE DATA FILES ---
        if path.startswith("/data/"):
            rel = path[len("/data/"):]
            file_path = FRAMEWORK / rel
            if file_path.is_file():
                self.send_response(200)
                ct = self._content_type(file_path.suffix.lower())
                self.send_header("Content-Type", ct)
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                with open(file_path, "rb") as fh:
                    self.wfile.write(fh.read())
                return
        
        # --- SERVE STATIC FILES ---
        file_path = FRAMEWORK / path.lstrip("/")
        if file_path.is_file():
            return self._serve_file(file_path)
        
        self.send_error(404)
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        
        if path == "/api/marks":
            marks = json.loads(MARKS_FILE.read_text()) if MARKS_FILE.exists() else {}
            marks.update(body)
            MARKS_FILE.write_text(json.dumps(marks, indent=2))
            return self._json({"ok": True})
        
        if path.startswith("/api/sequences/"):
            seq_id = path[len("/api/sequences/"):]
            body["modified"] = datetime.now().isoformat()
            if "created" not in body:
                body["created"] = body["modified"]
            seq_file = SEQUENCES_DIR / f"{seq_id}.json"
            seq_file.write_text(json.dumps(body, indent=2))
            return self._json({"ok": True, "id": seq_id})
        
        if path == "/api/face-labels":
            face_data_dir = FRAMEWORK / "face_data"
            # Save updated cluster data
            if "full_data" in body:
                (face_data_dir / "face_clusters.json").write_text(json.dumps(body["full_data"], indent=2))
            # Save labels separately too
            if "labels" in body:
                (face_data_dir / "face_labels.json").write_text(json.dumps(body["labels"], indent=2))
            return self._json({"ok": True, "count": len(body.get("labels", {}))})
        
        self.send_error(404)
    
    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        
        if path.startswith("/api/sequences/"):
            seq_id = path[len("/api/sequences/"):]
            seq_file = SEQUENCES_DIR / f"{seq_id}.json"
            if seq_file.exists():
                seq_file.unlink()
                return self._json({"ok": True})
            return self._json({"error": "not found"}, 404)
        
        self.send_error(404)
    
    def _serve_file(self, filepath, content_type=None):
        filepath = Path(filepath)
        if not filepath.is_file():
            self.send_error(404)
            return
        if content_type is None:
            content_type = self._content_type(filepath.suffix.lower())
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())
    
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _content_type(self, ext):
        return {
            '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
            '.json': 'application/json', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif', '.heic': 'image/heic',
            '.mov': 'video/quicktime', '.mp4': 'video/mp4', '.m4v': 'video/mp4',
            '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
        }.get(ext, 'application/octet-stream')
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Josh Memorial server v2 — http://localhost:{PORT}")
        print(f"  Browser: /  |  Builder: /builder  |  Player: /player")
        print(f"  Photos: {PHOTOS}")
        httpd.serve_forever()
