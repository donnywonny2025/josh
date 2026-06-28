import re

def patch_app():
    with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/app.html', 'r') as f:
        content = f.read()

    # 1. Add CSS
    if '.face-badge' not in content:
        css = "\n.grid-item .face-badge { position:absolute; top:4px; right:4px; background:rgba(74,158,255,0.85); color:#fff; font-size:9px; font-weight:600; padding:2px 6px; border-radius:4px; z-index:2; max-width:90%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }\n.grid-item .type-badge { position:absolute; top:24px; left:6px; font-size:9px; padding:1px 5px; border-radius:4px; font-weight:600; }"
        content = content.replace(".grid-item .type-badge { position:absolute; top:4px; left:6px; font-size:9px; padding:1px 5px; border-radius:4px; font-weight:600; }", css)

    # 2. Add State vars
    if 'let faceMap = {};' not in content:
        content = content.replace("let masterData = null;", "let masterData = null;\nlet faceClusters = null;\nlet faceLabels = {};\nlet faceMap = {};")

    # 3. Update Init
    old_init = """  const [foldersResp, marksResp, masterResp] = await Promise.all([
    fetch('/api/folders').then(r => r.json()),
    fetch('/api/marks').then(r => r.json()),
    fetch('/api/master').then(r => r.json())
  ]);
  folders = foldersResp;
  marks = marksResp;
  masterData = masterResp;"""

    new_init = """  const [foldersResp, marksResp, masterResp, clustersResp, labelsResp] = await Promise.all([
    fetch('/api/folders').then(r => r.json()),
    fetch('/api/marks').then(r => r.json()),
    fetch('/api/master').then(r => r.json()),
    fetch('/data/face_data/face_clusters.json').then(r => r.ok ? r.json() : null).catch(()=>null),
    fetch('/api/face-labels').then(r => r.ok ? r.json() : {}).catch(()=>({}))
  ]);
  folders = foldersResp;
  marks = marksResp;
  masterData = masterResp;
  faceClusters = clustersResp;
  faceLabels = labelsResp;
  buildFaceMap();"""
    content = content.replace(old_init, new_init)

    # 4. Add buildFaceMap
    build_fn = """function buildFaceMap() {
  faceMap = {};
  if (!faceClusters || !faceClusters.clusters) return;
  for (const c of faceClusters.clusters) {
    let label = faceLabels[c.person_id] || c.label;
    if (label.startsWith("Unknown")) continue;
    for (const p of c.photos) {
      const key = p.folder + '/' + p.file;
      if (!faceMap[key]) faceMap[key] = [];
      if (!faceMap[key].includes(label)) faceMap[key].push(label);
    }
  }
}"""
    if 'function buildFaceMap' not in content:
        content = content.replace("// --- SIDEBAR ---", build_fn + "\n\n// --- SIDEBAR ---")

    # 5. Update renderGrid
    if 'const faces = faceMap[key] || [];' not in content:
        content = content.replace("const classes = [", "const faces = faceMap[key] || [];\n    const faceBadge = faces.length > 0 ? `<div class=\"face-badge\">👤 ${faces.join(', ')}</div>` : '';\n    const classes = [")
        content = content.replace("<div class=\"label\">${f.name}</div>", "${faceBadge}<div class=\"label\">${f.name}</div>")

    # 6. Update renderLightbox
    if 'const faceStr = faces.length' not in content:
        content = content.replace("const mark = marks[key] || '';", "const mark = marks[key] || '';\n  const faces = faceMap[key] || [];\n  const faceStr = faces.length > 0 ? `  •  👤 ${faces.join(', ')}` : '';")
        content = content.replace("}MB  •  ${f.type}`;", "}MB  •  ${f.type}${faceStr}`;")

    with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/app.html', 'w') as f:
        f.write(content)

def patch_builder():
    with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/builder.html', 'r') as f:
        content = f.read()

    # 1. Add CSS
    if '.pool-item .face-badge' not in content:
        css = "\n.pool-item .face-badge { position:absolute; top:2px; left:2px; background:rgba(74,158,255,0.85); color:#fff; font-size:8px; font-weight:600; padding:1px 4px; border-radius:3px; z-index:2; max-width:90%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }"
        content = content.replace("/* MAIN */", css + "\n\n/* MAIN */")

    # 2. Add State vars
    if 'let faceMap = {};' not in content:
        content = content.replace("let savedSequences = [];", "let savedSequences = [];\nlet faceClusters = null;\nlet faceLabels = {};\nlet faceMap = {};")

    # 3. Update Init
    old_init = """  const [fResp, mResp, sResp] = await Promise.all([
    fetch('/api/folders').then(r=>r.json()),
    fetch('/api/master').then(r=>r.json()),
    fetch('/api/sequences').then(r=>r.json())
  ]);
  folders = fResp;
  masterData = mResp;
  savedSequences = sResp;"""
    
    new_init = """  const [fResp, mResp, sResp, cResp, lResp] = await Promise.all([
    fetch('/api/folders').then(r=>r.json()),
    fetch('/api/master').then(r=>r.json()),
    fetch('/api/sequences').then(r=>r.json()),
    fetch('/data/face_data/face_clusters.json').then(r => r.ok ? r.json() : null).catch(()=>null),
    fetch('/api/face-labels').then(r => r.ok ? r.json() : {}).catch(()=>({}))
  ]);
  folders = fResp;
  masterData = mResp;
  savedSequences = sResp;
  faceClusters = cResp;
  faceLabels = lResp;
  buildFaceMap();"""
    content = content.replace(old_init, new_init)

    # 4. Add buildFaceMap
    build_fn = """function buildFaceMap() {
  faceMap = {};
  if (!faceClusters || !faceClusters.clusters) return;
  for (const c of faceClusters.clusters) {
    let label = faceLabels[c.person_id] || c.label;
    if (label.startsWith("Unknown")) continue;
    for (const p of c.photos) {
      const key = p.folder + '/' + p.file;
      if (!faceMap[key]) faceMap[key] = [];
      if (!faceMap[key].includes(label)) faceMap[key].push(label);
    }
  }
}"""
    if 'function buildFaceMap' not in content:
        content = content.replace("function populateSectionSelect", build_fn + "\n\nfunction populateSectionSelect")

    # 5. Update renderPool
    if 'const faces = faceMap[key] || [];' not in content:
        content = content.replace("const cls = inSeq.has(key) ? 'pool-item in-seq' : 'pool-item';", "const cls = inSeq.has(key) ? 'pool-item in-seq' : 'pool-item';\n    const faces = faceMap[key] || [];\n    const faceBadge = faces.length > 0 ? `<div class=\"face-badge\">👤 ${faces.join(', ')}</div>` : '';")
        content = content.replace("<div class=\"name\">${f.name}</div>", "${faceBadge}<div class=\"name\">${f.name}</div>")
        content = content.replace("<div class=\"name\">🎬 ${f.name}</div>", "${faceBadge}<div class=\"name\">🎬 ${f.name}</div>")

    # 6. Update Preview Panel
    if 'const faceStr =' not in content:
        content = content.replace("function showPreview(src, name) {", "function showPreview(src, name, key) {\n  const faces = key && faceMap[key] ? faceMap[key] : [];\n  const faceStr = faces.length > 0 ? `<br><span style=\"color:#4a9eff\">👤 ${faces.join(', ')}</span>` : '';")
        content = content.replace("`<img src=\"${src}\"><div class=\"label\">${name}</div>`;", "`<img src=\"${src}\"><div class=\"label\">${name}${faceStr}</div>`;")
        
        # We need to pass the key from the hover events
        content = content.replace("showPreview('${src.replace(/'/g,\"\\\\'\")}','${f.name.replace(/'/g,\"\\\\'\")}')", "showPreview('${src.replace(/'/g,\"\\\\'\")}','${f.name.replace(/'/g,\"\\\\'\")}', '${key.replace(/'/g,\"\\\\'\")}')")
        
        # And for the timeline preview
        content = content.replace("showPreview('${src.replace(/'/g,\"\\\\'\")}','${s.file.replace(/'/g,\"\\\\'\")}')", "showPreview('${src.replace(/'/g,\"\\\\'\")}','${s.file.replace(/'/g,\"\\\\'\")}', '${s.folder.replace(/'/g,\"\\\\'\") + '/' + s.file.replace(/'/g,\"\\\\'\")}')")
        
        content = content.replace("showPreview(`/photos/${encodeURIComponent(s.folder)}/${encodeURIComponent(s.file)}`, s.file);", "showPreview(`/photos/${encodeURIComponent(s.folder)}/${encodeURIComponent(s.file)}`, s.file, s.folder + '/' + s.file);")

    with open('/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/builder.html', 'w') as f:
        f.write(content)

patch_app()
patch_builder()
print("Done patching.")
