import re
from pathlib import Path

f = Path("advanced.html")
html = f.read_text()

# 1. Update DOM Structure
markup_old = """
      <div id="canvasContainer" class="display" onclick="togglePlayPause()">
"""
markup_new = """
      <div id="global-bg"></div>
      <div id="canvasContainer" class="display" onclick="togglePlayPause()">
"""
if '<div id="global-bg"></div>' not in html:
    html = html.replace(markup_old.strip(), markup_new.strip())

markup_old_2 = """
      <canvas id="particleCanvas"></canvas>
      <div id="lightLeaks"></div>
"""
markup_new_2 = """
      <canvas id="particleCanvas"></canvas>
      <div id="lightLeaks"></div>
      <div id="extreme-fg"></div>
"""
if '<div id="extreme-fg"></div>' not in html:
    html = html.replace(markup_old_2.strip(), markup_new_2.strip())

# 2. Update CSS
css_new = """
/* Global Layers */
#global-bg { position:absolute; inset:-20%; width:140%; height:140%; z-index:0; background-size:cover; background-position:center; filter: brightness(0.7); }
#extreme-fg { position:absolute; inset:0; width:100%; height:100%; z-index:40; pointer-events:none; }
.extreme-fg-img { position:absolute; width:45%; object-fit:contain; border-radius:30px; box-shadow: 0 40px 80px rgba(0,0,0,0.9); filter: blur(15px); }

.display .slide { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; opacity:0; z-index:1; visibility:hidden; }
.display .slide.active { opacity:1; z-index:2; visibility:visible; }

/* Slide Layers */
.slide .fg-layer { position:relative; width:100%; height:100%; z-index:10; display:flex; align-items:center; justify-content:center; }
.slide .fg-layer img { width:auto; height:auto; max-width:75%; max-height:75%; object-fit:contain; border-radius: 20px; filter: drop-shadow(0 40px 80px rgba(0,0,0,0.9)); object-position:center; }

/* FX Overlays */
#particleCanvas { position:absolute; inset:0; width:100%; height:100%; z-index:50; pointer-events:none; mix-blend-mode: screen; }
#lightLeaks { position:absolute; inset:0; width:100%; height:100%; z-index:60; pointer-events:none; mix-blend-mode: screen; transition: background 2s ease; opacity:0.8; }
"""
html = re.sub(r'/\* GSAP Layers \*/.*?#lightLeaks {.*?}', css_new.strip(), html, flags=re.DOTALL)


# 3. Update initSequence to start Global GSAP animations
js_init_old = """
      document.getElementById('seqTitle').textContent = `Sequence: ${seq.id} (${seq.slides.length} slides)`;
      buildSlides(seq.slides);
"""
js_init_new = """
      document.getElementById('seqTitle').textContent = `Sequence: ${seq.id} (${seq.slides.length} slides)`;
      buildSlides(seq.slides);
      
      // Setup Global Background
      const globalBg = document.getElementById('global-bg');
      globalBg.style.backgroundImage = `url('/proxies/${seq.id}_bg.jpg')`;
      
      window.globalBgTl = gsap.to(globalBg, {
          scale: 1.25,
          x: 40,
          y: -30,
          duration: 120,
          ease: "none",
          repeat: -1,
          yoyo: true
      });
      
      // Setup Extreme Foreground
      const extremeFg = document.getElementById('extreme-fg');
      extremeFg.innerHTML = '';
      const fgPhotos = [...seq.slides].sort(() => 0.5 - Math.random()).slice(0, 2);
      fgPhotos.forEach((s, idx) => {
          const img = document.createElement('img');
          img.src = `/photos/${encodeURIComponent(s.folder)}/${encodeURIComponent(s.file)}`;
          img.className = 'extreme-fg-img';
          if (idx === 0) {
              img.style.left = '-10%';
              img.style.bottom = '-10%';
              img.dataset.rot = -20;
          } else {
              img.style.right = '-10%';
              img.style.top = '-10%';
              img.dataset.rot = 20;
          }
          extremeFg.appendChild(img);
      });
      
      window.extremeFgTl = gsap.to('.extreme-fg-img', {
          scale: 1.3,
          x: (i) => i === 0 ? 80 : -80,
          y: (i) => i === 0 ? -40 : 40,
          rotation: (i, el) => parseFloat(el.dataset.rot) + (i===0?10:-10),
          duration: 90,
          ease: "none",
          repeat: -1,
          yoyo: true
      });
"""
if 'window.globalBgTl' not in html:
    html = html.replace(js_init_old.strip(), js_init_new.strip())


# 4. Update buildSlides to NOT create bg-layer
js_build_old = """
          div.innerHTML = `
            <div class="bg-layer" id="bg${i}"></div>
            <div class="fg-layer">
              <img src="/photos/${encodeURIComponent(slide.folder)}/${encodeURIComponent(slide.file)}" />
            </div>
          `;
"""
js_build_new = """
          div.innerHTML = `
            <div class="fg-layer">
              <img src="/photos/${encodeURIComponent(slide.folder)}/${encodeURIComponent(slide.file)}" />
            </div>
          `;
"""
html = html.replace(js_build_old.strip(), js_build_new.strip())


# 5. Update showSlide for dynamic foreground entry transitions
js_showSlide_old = """
  // Trigger Light Leak transition
  triggerLightLeak();

  // Load single seamless ambient proxy background
  const bgLayer = document.getElementById(`bg${nextDiv}`);
  bgLayer.innerHTML = ''; // Clear any dynamic nodes just in case
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
  if (currentGsapTl) currentGsapTl.kill();
  currentGsapTl = gsap.timeline();
  
  currentGsapTl.set(nextSlideDiv, { zIndex: 2, visibility: 'visible' })
               .to(nextSlideDiv, { opacity: 1, duration: transDur, ease: "sine.inOut" }, 0);
               
  currentGsapTl.set(curSlideDiv, { zIndex: 1 })
               .to(curSlideDiv, { opacity: 0, duration: transDur, ease: "sine.inOut" }, 0);
               
  const usePush = document.getElementById('pushToggle').checked;
  if (usePush) {
      // Background seamless ambient drift
      const dirX = Math.random() > 0.5 ? 1 : -1;
      const dirY = Math.random() > 0.5 ? 1 : -1;
      currentGsapTl.fromTo(bgLayer, 
          { scale: 1.0, x: 0, y: 0 },
          { scale: 1.15, x: 20 * dirX, y: 15 * dirY, duration: dur + transDur, ease: "sine.inOut" },
          0
      );
      
      // Foreground cinematic drift (slow scale, subtle rotation)
      const baseScale = scale/100;
      const rotStart = -1 + Math.random() * 2;
      const rotEnd = rotStart + (-1 + Math.random() * 2);
      
      currentGsapTl.fromTo(fgLayer,
          { scale: baseScale, x: 0, y: 0, rotation: rotStart },
          { scale: baseScale + 0.1, x: 10, y: -5, rotation: rotEnd, duration: dur + transDur, ease: "sine.inOut" },
          0
      );
  }
"""

js_showSlide_new = """
  triggerLightLeak();

  let scale = slide.scale || 100;
  const fgLayer = nextSlideDiv.querySelector('.fg-layer');
  
  if (document.getElementById('scaleSlider')) {
      document.getElementById('scaleSlider').value = scale;
      document.getElementById('scaleVal').textContent = scale + '%';
  }
  
  const transDur = parseFloat(document.getElementById('transSlider').value);
  const dur = (slide.duration_sec || seq.default_duration_sec || 5);
  
  if (currentGsapTl) currentGsapTl.kill();
  currentGsapTl = gsap.timeline();
  
  // Slide div management
  currentGsapTl.set(nextSlideDiv, { zIndex: 2, visibility: 'visible', opacity: 1 });
  if (curDiv !== -1) {
      currentGsapTl.set(curSlideDiv, { zIndex: 1 })
                   .to(curSlideDiv, { opacity: 0, duration: transDur, ease: "power2.inOut" }, 0);
  }
               
  const usePush = document.getElementById('pushToggle').checked;
  if (usePush) {
      const baseScale = scale/100;
      const rotStart = -3 + Math.random() * 6;
      const rotEnd = rotStart + (-1 + Math.random() * 2);
      
      // DYNAMIC ENTRY: Pop in from scaled-down state with rotation and Y-shift
      currentGsapTl.fromTo(fgLayer,
          { scale: baseScale - 0.15, opacity: 0, rotation: rotStart - 5, y: 40 },
          { scale: baseScale, opacity: 1, rotation: rotStart, y: 0, duration: transDur, ease: "power3.out" },
          0
      );
      
      // CONTINUOUS DRIFT: Slow push after entry
      currentGsapTl.to(fgLayer,
          { scale: baseScale + 0.1, x: 10, y: -10, rotation: rotEnd, duration: dur, ease: "sine.inOut" },
          transDur
      );
  }
"""
# Need to use re.sub or exact match carefully since whitespace varies.
# Instead of replacing a massive block, let's use regex or split on a reliable marker.
# We will just replace everything inside showSlide from `triggerLightLeak();` down to the end of the `if (usePush)` block.

def replace_showSlide(html_content):
    start_marker = "  // Trigger Light Leak transition"
    end_marker = "  // Update Nav State"
    if start_marker in html_content and end_marker in html_content:
        pre = html_content.split(start_marker)[0]
        post = end_marker + html_content.split(end_marker, 1)[1]
        return pre + js_showSlide_new + "\n  " + post
    return html_content

html = replace_showSlide(html)
f.write_text(html)
