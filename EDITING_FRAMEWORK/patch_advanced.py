import re
from pathlib import Path

f = Path("advanced.html")
html = f.read_text()

# 1. Update title
html = html.replace("<title>Josh Memorial — Player</title>", "<title>Josh Memorial — Advanced Player</title>")

# 2. Update CSS
css_old = """
.display .slide { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; transition:opacity 1s ease; }
.display .slide img { width:100%; height:100%; object-fit:cover; object-position:center; }
.display .slide.active { opacity:1; z-index:2; }
.display .slide.hidden { opacity:0; z-index:1; }

/* KEN BURNS PUSH */
@keyframes pushIn {
  from { transform: scale(1.0); }
  to { transform: scale(1.05); }
}
.display .slide.active.push img { animation: pushIn 10s linear forwards; }
"""

css_new = """
.display .slide { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; opacity:0; z-index:1; visibility:hidden; }
.display .slide.active { opacity:1; z-index:2; visibility:visible; }

/* GSAP Layers */
.slide .bg-layer { position:absolute; inset:-10%; width:120%; height:120%; background-size:cover; background-position:center; z-index:1; filter: blur(10px) brightness(0.6); }
.slide .fg-layer { position:relative; width:100%; height:100%; z-index:2; display:flex; align-items:center; justify-content:center; }
.slide .fg-layer img { width:100%; height:100%; object-fit:cover; object-position:center; box-shadow: 0 0 60px rgba(0,0,0,0.9); }
"""
html = html.replace(css_old.strip(), css_new.strip())

# 3. Update HTML markup
html_old = """
      <div class="slide hidden" id="slideA"><img id="imgA"></div>
      <div class="slide hidden" id="slideB"><img id="imgB"></div>
"""
html_new = """
      <div class="slide" id="slideA">
        <div class="bg-layer" id="bgA"></div>
        <div class="fg-layer"><img id="imgA"></div>
      </div>
      <div class="slide" id="slideB">
        <div class="bg-layer" id="bgB"></div>
        <div class="fg-layer"><img id="imgB"></div>
      </div>
"""
html = html.replace(html_old.strip(), html_new.strip())

# 4. Add GSAP script
html = html.replace("<script>\n// --- STATE ---", '<script src="lib/gsap/gsap.min.js"></script>\n<script>\n// --- STATE ---')

# 5. Add GSAP timeline state
html = html.replace("let totalSec = 0;", "let totalSec = 0;\nlet currentGsapTl = null;")

# 6. Rewrite showSlide
js_old = """
  const transDur = parseFloat(document.getElementById('transSlider').value);
  nextSlideDiv.style.transition = `opacity ${transDur}s ease`;
  curSlideDiv.style.transition = `opacity ${transDur}s ease`;
  
  // Smart Framing Logic
  const frameInfo = framingMap[slide.file];
  let px = 50, py = 50;
  let useSmartFraming = false;

  if (slide.focus) {
      px = slide.focus[0];
      py = slide.focus[1];
      useSmartFraming = true;
  } else if (frameInfo && frameInfo.width && frameInfo.height && frameInfo.center_of_mass) {
      px = (frameInfo.center_of_mass[0] / frameInfo.width) * 100;
      py = (frameInfo.center_of_mass[1] / frameInfo.height) * 100;
      useSmartFraming = true;
  }

  if (useSmartFraming) {
      nextImg.style.objectPosition = `${px}% ${py}%`;
      nextSlideDiv.style.transformOrigin = `${px}% ${py}%`;
  } else {
      nextImg.style.objectPosition = '50% 50%';
      nextSlideDiv.style.transformOrigin = '50% 50%';
  }
  
  nextImg.src = src;
  
  let scale = slide.scale || 100;
  nextSlideDiv.style.transform = `scale(${scale / 100})`;
  if (document.getElementById('scaleSlider')) {
      document.getElementById('scaleSlider').value = scale;
      document.getElementById('scaleVal').textContent = scale + '%';
  }
  
  nextSlideDiv.classList.add('active');
  nextSlideDiv.classList.remove('hidden');
  curSlideDiv.classList.remove('active');
  curSlideDiv.classList.add('hidden');
  
  // Handle Ken Burns
  const usePush = document.getElementById('pushToggle').checked;
  if (usePush) {
      nextSlideDiv.classList.add('push');
  } else {
      nextSlideDiv.classList.remove('push');
  }
  curSlideDiv.classList.remove('push');
  
  activeSlide = nextDiv;
"""

js_new = """
  // Smart Framing Logic
  const frameInfo = framingMap[slide.file];
  let px = 50, py = 50;
  let useSmartFraming = false;

  if (slide.focus) {
      px = slide.focus[0];
      py = slide.focus[1];
      useSmartFraming = true;
  } else if (frameInfo && frameInfo.width && frameInfo.height && frameInfo.center_of_mass) {
      px = (frameInfo.center_of_mass[0] / frameInfo.width) * 100;
      py = (frameInfo.center_of_mass[1] / frameInfo.height) * 100;
      useSmartFraming = true;
  }

  if (useSmartFraming) {
      nextImg.style.objectPosition = `${px}% ${py}%`;
  } else {
      nextImg.style.objectPosition = '50% 50%';
  }
  
  nextImg.src = src;
  
  // Set Proxy Background
  const bgLayer = document.getElementById(`bg${nextDiv}`);
  const proxyUrl = `/proxies/${seq.id}_bg.jpg`;
  bgLayer.style.backgroundImage = `url('${proxyUrl}')`;
  
  let scale = slide.scale || 100;
  const fgLayer = nextSlideDiv.querySelector('.fg-layer');
  fgLayer.style.transform = `scale(${scale / 100})`;
  
  if (document.getElementById('scaleSlider')) {
      document.getElementById('scaleSlider').value = scale;
      document.getElementById('scaleVal').textContent = scale + '%';
  }
  
  const transDur = parseFloat(document.getElementById('transSlider').value);
  const dur = (slide.duration_sec || seq.default_duration_sec || 5);
  
  // GSAP Cinematic Parallax
  if (currentGsapTl) {
      currentGsapTl.kill();
  }
  
  currentGsapTl = gsap.timeline();
  
  // Bring new slide in
  currentGsapTl.set(nextSlideDiv, { zIndex: 2, visibility: 'visible' })
               .to(nextSlideDiv, { opacity: 1, duration: transDur, ease: "none" }, 0);
               
  // Fade old slide out slightly delayed
  currentGsapTl.set(curSlideDiv, { zIndex: 1 })
               .to(curSlideDiv, { opacity: 0, duration: transDur, ease: "none" }, 0);
               
  // Parallax motion (Fixed: Only smooth inward zoom, no horizontal sliding!)
  const usePush = document.getElementById('pushToggle').checked;
  if (usePush) {
      // Background slow drift
      currentGsapTl.fromTo(bgLayer, 
          { scale: 1.0, x: 0, y: 0 },
          { scale: 1.05, x: 0, y: 0, duration: dur + transDur, ease: "none" }, 
          0
      );
      
      // Foreground slightly faster push
      currentGsapTl.fromTo(fgLayer,
          { scale: (scale/100), x: 0, y: 0 },
          { scale: (scale/100) + 0.08, x: 0, y: 0, duration: dur + transDur, ease: "power1.out" },
          0
      );
  }
  
  nextSlideDiv.classList.add('active');
  curSlideDiv.classList.remove('active');
  
  activeSlide = nextDiv;
"""

html = html.replace(js_old.strip(), js_new.strip())

# 7. Add seq.id tracking for proxy loading
html = html.replace("seq = newSeq;", "seq = newSeq;\n  seq.id = id;")

# 8. Pause GSAP on pausePlayback
html = html.replace("if (requestID) cancelAnimationFrame(requestID);", "if (requestID) cancelAnimationFrame(requestID);\n  if (currentGsapTl) currentGsapTl.pause();")
html = html.replace("playing = true;\n  document.getElementById('btnPlayPause').textContent = '⏸';", "playing = true;\n  document.getElementById('btnPlayPause').textContent = '⏸';\n  if (currentGsapTl) currentGsapTl.play();")

f.write_text(html)
