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
MUSIC = PROJECT / "Music"
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
        if path == "/player_v2":
            return self._serve_file(FRAMEWORK / "player_v2.html", "text/html")
        if path == "/faces":
            return self._serve_file(FRAMEWORK / "faces.html", "text/html")
        if path == "/advanced":
            return self._serve_file(FRAMEWORK / "advanced.html", "text/html")
        
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

        # --- AUDIO TIMELINE API ---
        if path == "/api/audio-timeline":
            audio_file = FRAMEWORK / "audio_timeline.json"
            return self._json(json.loads(audio_file.read_text()) if audio_file.exists() else [])

        # --- PROPOSED CUTS API ---
        if path == "/api/proposed-cuts":
            beats_file = SEQUENCES_DIR / "proposed_cuts.json"
            return self._json(json.loads(beats_file.read_text()) if beats_file.exists() else {"cuts": []})

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
            target_path = PHOTOS / rel
            if target_path.is_file():
                range_header = self.headers.get("Range")
                total_size = target_path.stat().st_size
                with open(target_path, "rb") as fh:
                    if range_header:
                        import re
                        r_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                        if r_match:
                            start = int(r_match.group(1))
                            end_str = r_match.group(2)
                            end = int(end_str) if end_str else total_size - 1
                            length = end - start + 1
                            self.send_response(206)
                            self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
                        else:
                            start, length = 0, total_size
                            self.send_response(200)
                    else:
                        start, length = 0, total_size
                        self.send_response(200)
                    ct = self._content_type(target_path.suffix.lower())
                    self.send_header("Content-Type", ct)
                    self.send_header("Content-Length", str(length))
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    fh.seek(start)
                    self.wfile.write(fh.read(length))
                return
            self.send_error(404)
            return
            
        # --- SERVE PROXIES ---
        if path.startswith("/proxies/"):
            rel = path[len("/proxies/"):]
            file_path = PROJECT / "Proxies" / rel
            if file_path.is_file():
                self.send_response(200)
                ct = self._content_type(file_path.suffix.lower())
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(file_path.stat().st_size))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                with open(file_path, "rb") as fh:
                    try:
                        import shutil
                        shutil.copyfileobj(fh, self.wfile)
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                return
            self.send_error(404)
            return
        
        # --- SERVE MUSIC ---
        if path.startswith("/api/music/"):
            rel = path[len("/api/music/"):]
            # The audio files might be in Music/ or Music/FINAL_TRACKS/
            # Search for the exact name
            target_path = None
            for f in MUSIC.rglob("*"):
                if f.is_file() and f.name == rel:
                    target_path = f
                    break
            if target_path:
                range_header = self.headers.get("Range")
                total_size = target_path.stat().st_size
                with open(target_path, "rb") as fh:
                    if range_header:
                        import re
                        r_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                        if r_match:
                            start = int(r_match.group(1))
                            end_str = r_match.group(2)
                            end = int(end_str) if end_str else total_size - 1
                            length = end - start + 1
                            self.send_response(206)
                            self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
                        else:
                            start, length = 0, total_size
                            self.send_response(200)
                    else:
                        start, length = 0, total_size
                        self.send_response(200)
                    ct = self._content_type(target_path.suffix.lower())
                    self.send_header("Content-Type", ct)
                    self.send_header("Content-Length", str(length))
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    fh.seek(start)
                    self.wfile.write(fh.read(length))
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
                    try:
                        import shutil
                        shutil.copyfileobj(fh, self.wfile)
                    except (BrokenPipeError, ConnectionResetError):
                        pass
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
        
        if path == "/api/export_xml":
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            master_file = SEQUENCES_DIR / "master_timeline.json"
            if not master_file.exists():
                return self._json({"error": "master_timeline not found"}, 404)
            data = json.loads(master_file.read_text())
            slides = data.get("slides", [])
            
            xmeml = ET.Element("xmeml", version="5")
            project = ET.SubElement(xmeml, "project")
            ET.SubElement(project, "name").text = "Josh_Master_Sequence"
            children = ET.SubElement(project, "children")
            
            sequence = ET.SubElement(children, "sequence", id="master_sequence")
            ET.SubElement(sequence, "name").text = "Josh Master"
            
            rate = ET.SubElement(sequence, "rate")
            ET.SubElement(rate, "timebase").text = "30"
            ET.SubElement(rate, "ntsc").text = "FALSE"
            
            media = ET.SubElement(sequence, "media")
            video = ET.SubElement(media, "video")
            format_el = ET.SubElement(video, "format")
            sc = ET.SubElement(format_el, "samplecharacteristics")
            sc_rate = ET.SubElement(sc, "rate")
            ET.SubElement(sc_rate, "timebase").text = "30"
            ET.SubElement(sc_rate, "ntsc").text = "FALSE"
            ET.SubElement(sc, "width").text = "1920"
            ET.SubElement(sc, "height").text = "1080"
            
            v_track = ET.SubElement(video, "track")
            
            current_frame = 0
            for idx, sl in enumerate(slides):
                dur = sl.get("duration_frames", 150)
                
                if sl.get("isPlaceholder"):
                    current_frame += dur
                    continue
                
                clipitem = ET.SubElement(v_track, "clipitem", id=f"clip_{idx}")
                if sl.get("isCard"):
                    ET.SubElement(clipitem, "name").text = sl.get("title", "Card")
                else:
                    ET.SubElement(clipitem, "name").text = sl.get("file", f"Slide_{idx}")
                    
                ET.SubElement(clipitem, "duration").text = str(dur)
                
                rate_el = ET.SubElement(clipitem, "rate")
                ET.SubElement(rate_el, "timebase").text = "30"
                ET.SubElement(rate_el, "ntsc").text = "FALSE"
                
                ET.SubElement(clipitem, "start").text = str(current_frame)
                ET.SubElement(clipitem, "end").text = str(current_frame + dur)
                ET.SubElement(clipitem, "in").text = "0"
                ET.SubElement(clipitem, "out").text = str(dur)
                
                if not sl.get("isCard"):
                    file_el = ET.SubElement(clipitem, "file", id=f"file_{idx}")
                    ET.SubElement(file_el, "name").text = sl.get("file")
                    file_path = f"file://localhost/Volumes/Extreme SSD/JOSH/Photos/RAW_IMPORTS/{sl.get('folder')}/{sl.get('file')}"
                    ET.SubElement(file_el, "pathurl").text = urllib.parse.quote(file_path, safe='/:')
                
                current_frame += dur
                
            ET.SubElement(sequence, "duration").text = str(current_frame)
            
            audio = ET.SubElement(media, "audio")
            ET.SubElement(audio, "numOutputChannels").text = "2"
            format_el = ET.SubElement(audio, "format")
            sc = ET.SubElement(format_el, "samplecharacteristics")
            ET.SubElement(sc, "depth").text = "16"
            ET.SubElement(sc, "samplerate").text = "48000"
            
            a_track1 = ET.SubElement(audio, "track")
            a_track2 = ET.SubElement(audio, "track")
            
            for t_idx, a_track in enumerate([a_track1, a_track2]):
                clipitem = ET.SubElement(a_track, "clipitem", id=f"audio_clip_{t_idx}")
                ET.SubElement(clipitem, "name").text = "Master.mp3"
                ET.SubElement(clipitem, "duration").text = str(current_frame)
                rate_el = ET.SubElement(clipitem, "rate")
                ET.SubElement(rate_el, "timebase").text = "30"
                ET.SubElement(rate_el, "ntsc").text = "FALSE"
                
                ET.SubElement(clipitem, "start").text = "0"
                ET.SubElement(clipitem, "end").text = str(current_frame)
                ET.SubElement(clipitem, "in").text = "0"
                ET.SubElement(clipitem, "out").text = str(current_frame)
                
                file_el = ET.SubElement(clipitem, "file", id="master_audio_file" if t_idx == 0 else "")
                if t_idx == 0:
                    ET.SubElement(file_el, "name").text = "Master.mp3"
                    file_path = "file://localhost/Volumes/Extreme SSD/JOSH/Music/Master.mp3"
                    ET.SubElement(file_el, "pathurl").text = urllib.parse.quote(file_path, safe='/:')
                
                sourcetrack = ET.SubElement(clipitem, "sourcetrack")
                ET.SubElement(sourcetrack, "mediatype").text = "audio"
                ET.SubElement(sourcetrack, "trackindex").text = str(t_idx + 1)
            
            xmlstr = minidom.parseString(ET.tostring(xmeml)).toprettyxml(indent="  ")
            xmlstr = xmlstr.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>')
            
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Disposition", 'attachment; filename="Josh_Master_Sequence.xml"')
            self.end_headers()
            self.wfile.write(xmlstr.encode("utf-8"))
            return

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
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
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
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print(f"Josh Memorial server v2 — http://localhost:{PORT}")
        print(f"  Browser: /  |  Builder: /builder  |  Player: /player")
        print(f"  Photos: {PHOTOS}")
        httpd.serve_forever()
