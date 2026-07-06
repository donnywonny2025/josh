import re
from pathlib import Path

f = Path("advanced.html")
html = f.read_text()

# 1. Update CSS
css_old = """
.display .slide { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; opacity:0; z-index:1; visibility:hidden; }
.display .slide.active { opacity:1; z-index:2; visibility:visible; }

/* GSAP Layers */
.slide .bg-layer { position:absolute; inset:-10%; width:120%; height:120%; background-size:cover; background-position:center; z-index:1; }
.slide .fg-layer { position:relative; width:100%; height:100%; z-index:2; display:flex; align-items:center; justify-content:center; }
.slide .fg-layer img { width:auto; height:auto; max-width:75%; max-height:75%; object-fit:contain; border-radius: 20px; box-shadow: 0 40px 80px rgba(0,0,0,0.9); object-position:center; filter: drop-shadow(0 0 60px rgba(0,0,0,0.9)); }
"""

css_new = """
.display .slide { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; opacity:0; z-index:1; visibility:hidden; }
.display .slide.active { opacity:1; z-index:2; visibility:visible; }

/* GSAP Layers */
.slide .bg-layer { position:absolute; inset:-20%; width:140%; height:140%; z-index:1; overflow:hidden; background:#0a0a0f; }
.slide .bg-layer img { position:absolute; object-fit:cover; border-radius:12px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); filter: blur(6px) brightness(0.6); }

.slide .fg-layer { position:relative; width:100%; height:100%; z-index:10; display:flex; align-items:center; justify-content:center; }
.slide .fg-layer img { width:auto; height:auto; max-width:75%; max-height:75%; object-fit:contain; border-radius: 20px; filter: drop-shadow(0 40px 80px rgba(0,0,0,0.9)); object-position:center; }

/* FX Overlays */
#particleCanvas { position:absolute; inset:0; width:100%; height:100%; z-index:50; pointer-events:none; mix-blend-mode: screen; }
#lightLeaks { position:absolute; inset:0; width:100%; height:100%; z-index:60; pointer-events:none; mix-blend-mode: screen; transition: background 2s ease; opacity:0.8; }
"""
html = html.replace(css_old.strip(), css_new.strip())

# 2. Inject Canvas and LightLeaks into display area
markup_old = """
      <!-- Left/Right Click Zones -->
      <div class="zone-left" onclick="seekRelative(-1)"></div>
      <div class="zone-right" onclick="seekRelative(1)"></div>
"""
markup_new = """
      <!-- Left/Right Click Zones -->
      <div class="zone-left" onclick="seekRelative(-1)"></div>
      <div class="zone-right" onclick="seekRelative(1)"></div>
      
      <canvas id="particleCanvas"></canvas>
      <div id="lightLeaks"></div>
"""
html = html.replace(markup_old.strip(), markup_new.strip())

# 3. Add Particle Engine script right before // --- STATE ---
particle_script = """
// --- PARTICLE ENGINE & FX ---
const pCanvas = document.getElementById('particleCanvas');
const pCtx = pCanvas.getContext('2d');
let particles = [];

function initParticles() {
    pCanvas.width = pCanvas.offsetWidth;
    pCanvas.height = pCanvas.offsetHeight;
    particles = [];
    for(let i=0; i<40; i++) {
        particles.push({
            x: Math.random() * pCanvas.width,
            y: Math.random() * pCanvas.height,
            radius: Math.random() * 35 + 10,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            alpha: Math.random() * 0.3 + 0.05,
            hue: Math.random() > 0.5 ? '255, 220, 180' : '200, 230, 255'
        });
    }
}

function renderParticles() {
    pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
    particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if(p.x < -100) p.x = pCanvas.width + 100;
        if(p.x > pCanvas.width + 100) p.x = -100;
        if(p.y < -100) p.y = pCanvas.height + 100;
        if(p.y > pCanvas.height + 100) p.y = -100;
        
        pCtx.beginPath();
        pCtx.arc(p.x, p.y, p.radius, 0, Math.PI*2);
        pCtx.fillStyle = `rgba(${p.hue}, ${p.alpha})`;
        pCtx.shadowBlur = 20;
        pCtx.shadowColor = `rgba(${p.hue}, ${p.alpha})`;
        pCtx.fill();
    });
    requestAnimationFrame(renderParticles);
}
window.addEventListener('resize', initParticles);
initParticles();
renderParticles();

function triggerLightLeak() {
    const leak = document.getElementById('lightLeaks');
    const colors = [
        `rgba(255,100,50,0.15)`,
        `rgba(255,150,100,0.1)`,
        `rgba(50,150,255,0.1)`,
        `rgba(255,255,255,0.1)`
    ];
    const c1 = colors[Math.floor(Math.random() * colors.length)];
    const c2 = colors[Math.floor(Math.random() * colors.length)];
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    leak.style.background = `radial-gradient(circle at ${x}% ${y}%, ${c1} 0%, transparent 70%), radial-gradient(circle at ${100-x}% ${100-y}%, ${c2} 0%, transparent 70%)`;
}
"""
html = html.replace("// --- STATE ---", particle_script + "\n// --- STATE ---")


# 4. Rewrite showSlide for dynamic backgrounds and cinematic GSAP
js_old_showSlide = """
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
"""

js_new_showSlide = """
  // Trigger Light Leak transition
  triggerLightLeak();

  // Dynamic Background Generation (True Parallax)
  const bgLayer = document.getElementById(`bg${nextDiv}`);
  bgLayer.innerHTML = ''; // Clear old
  
  const numBgPhotos = Math.min(16, seq.slides.length);
  // Pick random slides for background
  const bgSlides = [...seq.slides].sort(() => 0.5 - Math.random()).slice(0, numBgPhotos);
  
  const dynamicBgImgs = [];
  bgSlides.forEach(s => {
      const img = document.createElement('img');
      img.src = `/photos/${encodeURIComponent(s.folder)}/${encodeURIComponent(s.file)}`;
      
      // Randomize layout properties
      const widthPct = 20 + Math.random() * 25; 
      img.style.width = widthPct + '%';
      
      // Keep them roughly within bounds
      img.style.left = (5 + Math.random() * 70) + '%';
      img.style.top = (5 + Math.random() * 70) + '%';
      
      // Rotation
      const rot = -25 + Math.random() * 50;
      img.style.transform = `rotate(${rot}deg)`;
      
      // Store parallax depth multiplier
      img.dataset.parallaxSpeed = 0.5 + Math.random() * 1.5;
      img.dataset.rotStart = rot;
      
      bgLayer.appendChild(img);
      dynamicBgImgs.push(img);
  });
  
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
      // Background individual parallax
      dynamicBgImgs.forEach(img => {
          const speed = parseFloat(img.dataset.parallaxSpeed);
          const rotStart = parseFloat(img.dataset.rotStart);
          const dirX = Math.random() > 0.5 ? 1 : -1;
          const dirY = Math.random() > 0.5 ? 1 : -1;
          const rotDrift = Math.random() > 0.5 ? 2 : -2;
          
          currentGsapTl.fromTo(img, 
              { scale: 1.0, x: 0, y: 0, rotation: rotStart },
              { scale: 1.0 + (0.05 * speed), x: 30 * speed * dirX, y: 20 * speed * dirY, rotation: rotStart + rotDrift, duration: dur + transDur, ease: "sine.inOut" },
              0
          );
      });
      
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
html = html.replace(js_old_showSlide.strip(), js_new_showSlide.strip())

f.write_text(html)
