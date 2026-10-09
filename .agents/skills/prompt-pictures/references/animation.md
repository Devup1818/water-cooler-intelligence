# Animation reference: Prompt Pictures

Read this before drawing anything. It covers:
- how a film page is built and rendered
- the motion maths
- an acting cheat sheet with frame counts
- three timing styles
- camera grammar, composition and type
- material recipes
- the review checklist

Everything here is at **30 fps, 1080×1920**.

---

## 1. Frames, beats and the bar map

One beat must be a whole number of frames:

| BPM | Frames per beat | Frames per bar | Feels like |
|---|---|---|---|
| 90 | 20 | 80 | lo-fi, cosy |
| 100 | 18 | 72 | storytelling, ragtime, swing |
| 112.5 | 16 | 64 | caper, swing |
| 120 | 15 | 60 | pop, march, montage |
| 128.57 | 14 | 56 | sports, anthem |

```js
// scripts/lib/timing.mjs: shared by the picture AND the score
export const FPS = 30, BPM = 120, BEAT = 15, BAR = 60, BARS = 12, TOTAL = 720;
export const at = (bar, beat = 1, eighth = 0) => (bar - 1) * BAR + (beat - 1) * BEAT + Math.floor(eighth * BEAT / 2);
export const EVENTS = [ /* { frame, kind, x, detail }, one per sound-worthy action, sorted by frame */ ];
```

- The picture **reads its cue frames from this file**. Never type a cue frame into the
  drawing code.
- Sixteenths that fall on half frames: use `Math.floor`. Half a frame (17 ms) early is
  inaudible.
- Measure `x` (0–1) from where you actually draw the thing, not from where you think it is.
  The score pans with it.

## 2. The page: HyperFrames composition (2D canvas)

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="24" data-width="1080" data-height="1920">
  <canvas id="c" width="1080" height="1920"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  const ctx = document.getElementById("c").getContext("2d");
  function draw(fr) {                         // a PURE function of the frame number
    fr = Math.round(fr);
    ctx.setTransform(1, 0, 0, 1, 0, 0);       // reset ALL state every frame: transform, alpha, composite, line caps, filters
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over"; ctx.lineCap = "butt"; ctx.filter = "none";
    ctx.clearRect(0, 0, 1080, 1920);
    // … draw the scene for frame fr …
  }
  async function build() {
    await document.fonts.ready;               // plus any image/offscreen pre-renders
    const tl = gsap.timeline({ paused: true }), proxy = { fr: 0 };
    tl.to(proxy, { fr: TOTAL, duration: TOTAL / FPS, ease: "none", onUpdate: () => draw(proxy.fr) }, 0);
    draw(0);
    window.__timelines = window.__timelines || {};
    window.__timelines["main"] = tl;          // HyperFrames seeks this timeline frame by frame
  }
  build();
</script>
```

**Three.js films** use a seek bridge instead of a GSAP timeline:
- Mark the root `data-no-timeline`.
- Expose a "ready" promise on `window.__hf.buildReady[...]`.
- Listen for the `hf-seek` event (`e.detail.time`). Render that exact time once.
- If the scene isn't built yet, defer the seek with `e.detail.waitUntil(ready.then(...))`.
- Read HyperFrames' docs for the current contract (`npx hyperframes@0.8.71 --help`).

**Commands**
- `npx --yes hyperframes@0.8.71 check` lints the composition.
- `… snapshot` renders stills.
- `… render -o ../out/film-silent.mp4 --workers 4` renders the film.

**Determinism rules** (the score depends on them):
- Use seeded randomness only. Never use `Math.random`, `Date` or `requestAnimationFrame`.

```js
function mulberry32(seed) { let a = seed >>> 0; return () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hash = (n) => mulberry32(n * 9973 + 17)();     // a per-frame or per-item random value, stable forever
```

- Frames must be **order-independent**. Drawing frame 500 cold must equal drawing it after
  frame 499. Prove it: render a few frames out of order and compare the pixels.
- **Pre-render** anything static (backgrounds, grain tiles, textures, text) into offscreen
  canvases once, and blit them per frame.
- Keep each frame cheap: no full-frame blur per frame. A headless browser can be killed if
  a single worker runs too long, so always render with 4 workers.

---

## 3. Motion maths

**The spring.** Use it for anything that pops, lands, settles or reacts. Never use linear
motion for these.

```js
// Damped spring step response: 0 → 1 with overshoot. t in seconds since the cue.
function spring(t, { freq = 2.2, damping = 0.45 } = {}) {   // freq Hz; damping 0.35 bouncy … 0.7 crisp
  if (t <= 0) return 0;
  const w = 2 * Math.PI * freq, z = damping, wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
}
const S = (fr, cue, opts) => spring((fr - cue) / 30, opts);   // value at frame fr for an action cued at frame cue
```

| Use | freq | damping | Result |
|---|---|---|---|
| UI pop-in, card, label | 2.5 | 0.5 | one small overshoot, settles in about 10 frames |
| Character landing / squash recovery | 3.0 | 0.35 | bouncy, two wobbles |
| Big title word | 1.8 | 0.55 | weighty, lands |
| Hair, tail, antenna (follow-through) | 3.5 | 0.3 | lags and jiggles |

**Easing for the camera and long travel:** `easeInOutCubic`. The camera should never
bounce.

```js
const easeInOutCubic = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
const backOut = (u, s = 1.7) => 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2);  // quick overshoot without a spring
const clamp01 = (u) => Math.max(0, Math.min(1, u)), seg = (fr, a, b) => clamp01((fr - a) / (b - a));
```

**Squash and stretch, preserving volume:**

```js
const squash = (amount) => ({ sx: 1 / Math.sqrt(1 - amount), sy: 1 - amount });   // amount 0.15 = a firm landing
// impulse on landing: amount = 0.18 * Math.exp(-(fr - land) / 4) * Math.cos((fr - land) * 0.9)
```

**Pose blending.**
- A pose is a plain object of numbers: head angle, brow height, arm angles, mouth openness…
- Blend between two poses with a spring, number by number. Strings (like mouth shape names)
  switch at the midpoint.
- Solve two-bone IK once, when you define a pose, so blended hands travel on **arcs**, not
  straight lines.

```js
// Each key springs from the previous target. The terms superpose, so there are no jumps
// and overlapping keys blend naturally. A key's frame is when the move STARTS. It lands
// about 5–6 frames later (freq 2.2), so put keys a few frames before the beat.
function track(fr, keys, opts) {               // keys: [[frame, pose], ...] sorted by frame
  const out = { ...keys[0][1] };
  for (let i = 1; i < keys.length; i++) {
    const [f, pose] = keys[i], prev = keys[i - 1][1], u = spring((fr - f) / 30, opts);
    if (u <= 0) break;
    for (const k in pose) out[k] = typeof pose[k] === "number" ? out[k] + (pose[k] - prev[k]) * u : (u > 0.5 ? pose[k] : out[k]);
  }
  return out;
}
```

---

## 4. Acting cheat sheet (frame counts at 30 fps)

| Beat | How |
|---|---|
| **Blink** | 2 frames closing, 1 closed, 2–3 opening. Blink on head turns and after big reactions. Leave 1.5–4 s between idle blinks, seeded. |
| **Eye dart** | 2 frames. **The eyes lead**: eyes, then the head 2–3 frames later, then the body 2 frames after that. |
| **Anticipation** | 4–8 frames moving the opposite way before any big move (crouch before a jump, wind-up before a throw). Small moves get 2–3 frames. |
| **Landing** | Squash 3–4 frames, then a spring back with one overshoot. Add a dust puff and a foley event on the contact frame. |
| **Moving hold** | Never freeze a character completely. Keep 1–2% breathing scale and a slow drift. The exception is designed stillness, where every frame is identical on purpose. |
| **Take / double take** | Look (3 frames) → glance away → snap back with a squash (4–6 frames) and a stinger. |
| **Deadpan to camera** | Turn the head 4 frames, then hold 8–12 frames with a single slow blink. |
| **Follow-through** | Hair, ties, tails and ears lag 2–4 frames behind and overshoot on a bouncy spring. |
| **Overlapping action** | Head leads, torso follows 2 frames later, arms 3–4. Nothing starts or stops together. |
| **Talking** | Open the mouth on each syllable and close it between. Nod slightly on stressed beats, and raise the brows on questions. |
| **Big emotion** | Push the pose 20% further than feels right. Phone screens are small. |

Readability rules:
- Every character reads at **thumbnail size**: strong silhouette, big eyes, one signature
  feature.
- Hands are where things go wrong. Draw a thumbs-up as a sideways fist with folded fingers
  and the thumb rising from the corner. A single raised digit at small size reads as a
  middle finger. **Check every hand pose at phone size.**
- Faces carry the acting: brows (worry, resolve, surprise), lids (sleepy, smug), and mouth
  shapes (wobbly worry, "o" exhale, grin, sideways smirk).

---

## 5. Timing styles

| Style | How | Used in |
|---|---|---|
| **Smooth 30** | Every frame new. The default. | Buy Milk, 47 Tabs, The Race |
| **On twos** (stop-motion) | Poses AND camera change only on even frames: `const step = Math.floor(fr / 2) * 2`. Add a seeded ±1.5% exposure flicker per step and a sub-pixel "boil" of silhouettes per step. | claymation |
| **Hand-cranked** (silent film) | Hold each drawing 2 frames (about 15 fps). Add gate weave (±2 px seeded), per-step exposure flicker, dust and scratches. Switch to smooth 30 when the story crosses into the "new world". | The Talkies |

Designed **stillness** means byte-identical frames under digital-zero audio. It's the
loudest moment a feed can have. Use it once per film.

---

## 6. Camera grammar

- **Establish, then push.** Open wide enough to read the place, then slowly push in during
  held moments.
- **Cut on the bar line.** Hard cuts land on downbeats. In a montage, **match cuts** keep
  the character in the same place in frame.
- **Whip pan:** 6–8 frames with motion streaks, landing on the beat with a small settle.
- **Insert close-up for the product moment.** The finger, the key and the glow get their
  own shot (or a magnifier bubble) so the gesture reads.
- **Don't move the camera while the viewer reads text.** Let the type settle first.
- **The camera eases; characters spring.** Never put a spring overshoot on the camera.

---

## 7. Composition, colour and type

- **One focal point per shot.** Everything else is quieter in contrast, saturation or
  size.
- **Colour script:** plan the palette as an arc across the film. Examples:
  - 47 Tabs goes from cold navy to plum and lamp gold.
  - The Talkies goes from silver to Technicolor.
  - The emotional turn should be visible in the colour alone.
- **One accent colour for the product moment** (for example, an amber key glow). Reuse it
  on the end card.
- **Safe zones on 1080×1920:** essential text and gags between **y 220 and y 1600**, side
  margins of 80–90 px. App UI covers the rest.
- **Type:**
  - Two typefaces at most.
  - Captions 34 px or larger, headlines 70–120 px.
  - Contrast of 4.5:1 or better. Light text on a busy frame needs a soft shadow or a
    plate.
  - Prefer OFL fonts. Use no real brands, logos or UIs other than your own.
- **End card:** the line (springing in word by word), then the lockup (mark + wordmark),
  then a sub line. Leave a quiet 2–3 seconds at the end, and add one small callback gag if
  the story earned it.

---

## 8. Material recipes

- **Film grain:**
  - Pre-render 4–8 seeded noise tiles once.
  - Per frame (or per step), draw one tile, chosen by `hash(frame)`, with
    `globalCompositeOperation = "overlay"` at 6–9% opacity.
- **Paper or papyrus:** a large, soft, seeded noise layer plus a few fibre strokes, with a
  slight vignette.
- **Gold leaf:** a gradient fill plus a moving specular glint (a narrow light band that
  slides diagonally once per beat).
- **Halftone or woodcut:** dot or line patterns clipped to shapes. Keep to one spot colour.
- **CRT:** scanlines every 3 px at 12% opacity, a soft bloom on bright pixels and a slight
  barrel vignette.
- **Clay (Three.js):**
  - `MeshStandardMaterial` with roughness 0.55–0.7.
  - A seeded fingerprint and tool-mark normal map drawn on a canvas.
  - Slightly lumpy geometry: no perfect bevels.
  - A warm key light plus bounce, and soft shadows.
- **Glass, metal, macro** (product shots): render supersampled (2–3×) and resolve with a
  tone-weighted average. Hardware MSAA on HDR makes thin highlights stair-step.

---

## 9. Review checklist (before rendering, and again on the MP4)

- [ ] A full-size still at **every bar line** and **every gag**. Look at each one.
- [ ] The same stills scaled to 360 px wide: does each gag still read?
- [ ] Every hand pose at phone size.
- [ ] Every word legible, inside the safe zone, and spelled right.
- [ ] Determinism: frames rendered out of order are pixel-identical.
- [ ] Exact frame count: `ffprobe -count_frames` equals TOTAL.
- [ ] EVENTS cover every contact, pop, blink, press and card, with measured `x`.
- [ ] The product moment is on its exact frame, and the sound will be too.
- [ ] Write a story doc: treatment, character notes, the bar map as built, and the sound
      handoff.
