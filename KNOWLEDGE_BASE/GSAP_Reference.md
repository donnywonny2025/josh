# GSAP (GreenSock) Documentation & Integration Guide

## 1. What is GSAP?
GSAP (GreenSock Animation Platform) is an industry-standard JavaScript animation library. It solves all cross-browser rendering bugs, handles hardware-accelerated 3D transforms (`translate3d`), and manages frame-rate synchronization (`requestAnimationFrame`) perfectly. It is the engine that powers cinematic, "Apple-style" web animations.

**Library Location in Project:**
`/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/lib/gsap/gsap.min.js`

## 2. Including GSAP in the App
When we are ready to build the parallax theme, we simply add this script tag to the bottom of the HTML file (before our custom script):
```html
<script src="lib/gsap/gsap.min.js"></script>
```

---

## 3. Core Syntax for After Effects-Style Timelines

To create cinematic motion, we use `gsap.timeline()`. This allows us to chain animations exactly like a timeline in After Effects.

### Basic Parallax (Foreground vs Background Speed)
To create 3D depth, the background moves slower than the foreground.

```javascript
// Create a timeline that lasts 6 seconds total
let slideTl = gsap.timeline();

// 1. Animate the blurred background (moves slightly)
slideTl.to(".background-proxy-image", {
  duration: 6,
  scale: 1.1,         // Slight zoom in
  x: 20,              // Move 20px right
  ease: "none"        // Linear easing, like a constant drone shot
}, 0); // The '0' means start at exactly 0 seconds on the timeline

// 2. Animate the foreground subject (moves faster/further)
slideTl.to(".foreground-main-image", {
  duration: 6,
  scale: 1.15,
  x: 60,              // Move 60px right (parallax depth)
  ease: "power2.out"  // Starts fast, slowly drifts to a halt
}, 0); 
```

### Staggering Multiple Background Proxies
If we load 8 tiny background proxy images, we can animate all of them at once with slight offsets using `stagger`.

```javascript
slideTl.from(".collage-proxy", {
  duration: 3,
  opacity: 0,
  z: -500, // Starts far back in 3D space
  ease: "power3.out",
  stagger: 0.1 // Each photo flies in 0.1s after the previous one
}, 0);
```

---

## 4. Why This Works Perfectly for the Slideshow

1. **Hardware Acceleration:** By exclusively animating `x`, `y`, `z`, `scale`, and `opacity`, GSAP forces the browser to use the GPU. This means no dropped frames.
2. **Absolute Timing:** We hardcoded the slides to `4.0` or `6.093` seconds. We can easily pass that exact variable into the GSAP `duration` parameter so the animation finishes perfectly on the cut.
3. **Crossfades:** We can smoothly fade one timeline out while the next fades in, overlapping them effortlessly.

## 5. Next Steps for Implementation
When you give the green light to touch the app:
1. We will link `gsap.min.js` in `player.html`.
2. We will wrap the photos in a `.foreground` and `.background` layer.
3. We will write a GSAP timeline function that triggers every time a new slide loads in the sequence.
