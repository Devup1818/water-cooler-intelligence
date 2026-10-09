# Sound reference: Prompt Pictures

Read this before writing the score. It has:
- the engine core, as runnable code
- recipes for each instrument and sound effect, with the parameters our films used
- the mix chain and its numbers
- scoring patterns
- the commands that prove the result

Everything runs at **48 kHz**, is **seeded**, and renders to a 24-bit stereo WAV. Two runs
give byte-identical audio, the same contract the picture keeps.

---

## 1. The engine core (runnable)

Put this in `scripts/lib/studio.mjs`. Every instrument below builds on it.

```js
export const SR = 48000;
const TAU = Math.PI * 2;

/* deterministic randomness: mulberry32 */
export function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export const secs = (n) => Math.max(1, Math.round(n * SR));
export const midiHz = (m) => 440 * Math.pow(2, (m - 69) / 12);
export const expDecay = (i, tau) => Math.exp(-i / (tau * SR));
export const sat = (x, drive = 1) => Math.tanh(x * drive) / Math.tanh(drive);
export function declick(buf, ms = 3) { const n = Math.min(buf.length, secs(ms / 1000));
  for (let i = 0; i < n; i++) { const g = i / n; buf[i] *= g; buf[buf.length - 1 - i] *= g; } return buf; }
/** Peak-normalise one-shots so a gain of 0.5 means the same thing for every instrument. */
export function norm(buf, peak = 0.9) { let m = 0; for (const v of buf) m = Math.max(m, Math.abs(v));
  if (m > 0) for (let i = 0; i < buf.length; i++) buf[i] *= peak / m; return buf; }
export function dcBlock(buf) { let x1 = 0, y1 = 0; for (let i = 0; i < buf.length; i++) { const y = buf[i] - x1 + 0.9995 * y1; x1 = buf[i]; y1 = y; buf[i] = y; } return buf; }

/* RBJ biquad: lp hp bp peak highshelf */
export function biquad(type, f, q = 0.707, gainDb = 0) {
  const w = TAU * Math.min(f, SR * 0.45) / SR, cs = Math.cos(w), sn = Math.sin(w), al = sn / (2 * q), A = Math.pow(10, gainDb / 40);
  let b0, b1, b2, a0, a1, a2;
  if (type === "lp") { b0 = (1 - cs) / 2; b1 = 1 - cs; b2 = b0; a0 = 1 + al; a1 = -2 * cs; a2 = 1 - al; }
  else if (type === "hp") { b0 = (1 + cs) / 2; b1 = -(1 + cs); b2 = b0; a0 = 1 + al; a1 = -2 * cs; a2 = 1 - al; }
  else if (type === "bp") { b0 = al; b1 = 0; b2 = -al; a0 = 1 + al; a1 = -2 * cs; a2 = 1 - al; }
  else if (type === "peak") { b0 = 1 + al * A; b1 = -2 * cs; b2 = 1 - al * A; a0 = 1 + al / A; a1 = -2 * cs; a2 = 1 - al / A; }
  else if (type === "highshelf") { const s = 2 * Math.sqrt(A) * al;
    b0 = A * ((A + 1) + (A - 1) * cs + s); b1 = -2 * A * ((A - 1) + (A + 1) * cs); b2 = A * ((A + 1) + (A - 1) * cs - s);
    a0 = (A + 1) - (A - 1) * cs + s; a1 = 2 * ((A - 1) - (A + 1) * cs); a2 = (A + 1) - (A - 1) * cs - s; }
  else throw new Error(type);
  b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0;
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  return (x) => { const y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x; y2 = y1; y1 = y; return y; };
}
/* zero-delay-feedback state-variable filter: stable under fast cutoff sweeps */
export function svf() { let ic1 = 0, ic2 = 0;
  return (x, cutoff, res = 0.2) => { const g = Math.tan(Math.PI * Math.min(cutoff, SR * 0.45) / SR), k = 2 - 2 * Math.min(res, 0.98);
    const a1 = 1 / (1 + g * (g + k)), a2 = g * a1, a3 = g * a2, v3 = x - ic2, v1 = a1 * ic1 + a2 * v3, v2 = ic2 + a2 * ic1 + a3 * v3;
    ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2; return { lp: v2, bp: v1, hp: x - k * v1 - v2 }; }; }

/* band-limited oscillators (polyBLEP) */
function blep(t, dt) { if (t < dt) { t /= dt; return t + t - t * t - 1; } if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; } return 0; }
export function sawOsc() { let p = 0; return (f) => { const dt = f / SR; p += dt; if (p >= 1) p -= 1; return 2 * p - 1 - blep(p, dt); }; }
export function sqrOsc(pw = 0.5) { let p = 0; return (f) => { const dt = f / SR; p += dt; if (p >= 1) p -= 1;
  let v = p < pw ? 1 : -1; v += blep(p, dt); v -= blep((p + 1 - pw) % 1, dt); return v; }; }
export function adsr(n, { a = 0.005, d = 0.1, s = 0.7, r = 0.2 } = {}) {
  const e = new Float32Array(n), A = secs(a), D = secs(d), R = secs(r), H = n - R;
  for (let i = 0; i < n; i++) e[i] = i < A ? i / A : i < A + D ? 1 - (1 - s) * (i - A) / D : i < H ? s : s * Math.max(0, 1 - (i - H) / R);
  return e;
}

/* the session: buses → sends → master. put() places a buffer at a time in seconds. */
export class Session {
  constructor(seconds) { this.n = secs(seconds); this.buses = {}; }
  bus(name, { gain = 1, reverb = 0, delay = 0, duck = 0, hp = 0, lp = 0 } = {}) {
    this.buses[name] = { L: new Float32Array(this.n), R: new Float32Array(this.n), gain, reverb, delay, duck, hp, lp }; return this; }
  put(bus, buf, at, gain = 1, pan = 0) {   // equal-power pan, −1..1
    const b = this.buses[bus], s = Math.round(at * SR), gl = gain * Math.cos((pan + 1) * Math.PI / 4) * Math.SQRT2, gr = gain * Math.sin((pan + 1) * Math.PI / 4) * Math.SQRT2;
    for (let i = 0; i < buf.length; i++) { const k = s + i; if (k < 0) continue; if (k >= this.n) break; b.L[k] += buf[i] * gl; b.R[k] += buf[i] * gr; } }
}
```

The mixdown (section 4) and the reverb, delay, glue and limiter (section 5) complete it.

## 2. Timing: score and picture share one clock

```js
const BPM = 120, BEAT = 60 / BPM;
const T = (bar, beat = 1) => ((bar - 1) * 4 + (beat - 1)) * BEAT;        // seconds
const SW = (bar, beat) => { const f = Math.floor(beat), r = beat - f;      // swing: an offbeat eighth lands at 2/3
  return T(bar, f + (Math.abs(r - 0.5) < 1e-6 ? 2 / 3 : r)); };
const F = (frame) => frame / 30;                                           // picture frame → seconds
```

- Read the picture's `EVENTS` from the shared timing file, and place foley at `F(e.frame)`
  panned by `(e.x − 0.5) × 1.6`.
- Compose the music on `T(bar, beat)`.

---

## 3. Instrument recipes

Add these to the same `studio.mjs`, because they use its private `TAU`. Every one-shot returns a
`Float32Array`. Normalise with `norm()` and `declick()`.

### Drums

| Sound | Recipe |
|---|---|
| **Kick** | Sine whose pitch falls from 150 Hz to 46 Hz with τ 45 ms, amplitude τ 0.2 s. Add a 6 ms high-passed noise click at 0.35, then `sat(drive 1.6)`. |
| **Snare** | A 190 Hz body sine (a +50% pitch blip with τ 10 ms, amplitude τ 60 ms), plus high-passed noise (1.8 kHz) with a +5 dB peak at 5.2 kHz (τ 120 ms). |
| **Clap** | Four noise bursts 9 ms apart (τ 4.5 ms each), then a 110 ms tail. Band-pass at 1.3 kHz, high-pass at 700 Hz. |
| **Hat** | Six square waves at 808 metal ratios (205.3, 304.4, 369.6, 522.7, 540, 800 Hz, ×1.72), band-passed at 10.2 kHz and high-passed at 7.2 kHz, plus noise. τ 18 ms closed, 140 ms open. |
| **Crash** | Eight square waves (311–1873 Hz ×3.1) plus noise, high-passed at 3.2 kHz, two-stage decay (0.28 s / 0.9 s). |
| **Frame drum** | "Doum": a kick at 120→68 Hz with τ 0.2 plus low-passed noise. "Tek": noise band-passed at 1.9 kHz (τ 18 ms) plus a short 420 Hz sine. |
| **Boom** (cuts, titles) | Sine falling 90→32 Hz (τ 0.18) with amplitude τ 0.55, plus low-passed noise, `sat 1.4`. |

```js
export function kick({ f0 = 150, f1 = 46, pitchTau = 0.045, len = 0.55, tau = 0.2, click = 0.35, drive = 1.6, seed = 1 } = {}) {
  const n = secs(len), out = new Float32Array(n), R = rng(seed), hp = biquad("hp", 2500); let ph = 0;
  for (let i = 0; i < n; i++) { ph += (f1 + (f0 - f1) * expDecay(i, pitchTau)) / SR;
    let v = Math.sin(TAU * ph) * expDecay(i, tau); if (i < secs(0.006)) v += hp(R() * 2 - 1) * click * (1 - i / secs(0.006));
    out[i] = sat(v, drive); }
  return declick(out, 1);
}
```

### Pitched

**FM bell / glockenspiel.** The modulator ratio is **3.01**. A ratio of 3.5 reads an
octave low; the extra 0.01 adds shimmer.

```js
export function bell(f, { len = 2.2, ratio = 3.01, index = 2, tau = 0.7 } = {}) {
  const n = secs(len), out = new Float32Array(n);
  for (let i = 0; i < n; i++) { const t = i / SR, I = index * expDecay(i, tau * 0.35);
    out[i] = Math.sin(TAU * f * t + I * Math.sin(TAU * f * ratio * t)) * expDecay(i, tau) * 0.6; }
  return declick(out, 0.5);
}
```

**FM electric piano**
- A 1:1 body with modulation index 1.1 that decays with τ 0.6 s, and amplitude τ 1.1 s.
- Plus a 1:14 "tine" (index 0.9, τ 0.05 s) at 0.35 level, with amplitude τ 0.18 s.
- Tremolo: 6% at 4.6 Hz.

**Modal percussion.** Sum sines at the bar's modes, each with its own decay:

| Instrument | Partial ratios | Decays τ (s) | Extra |
|---|---|---|---|
| Marimba | 1 · 3.93 · 9.25 | 0.42 · 0.11 · 0.035 | 4 ms mallet noise |
| Vibraphone | 1 · 3.93 · 9.2 | 0.9 · 0.2 · 0.05 | tremolo 5.5 Hz, depth 0.35 |
| Kalimba | 1 · 1.003 · 5.4 · 11.8 | 0.55 · 0.5 · 0.06 · 0.02 | the 1.003 beat is the charm |
| **Steel pan** | 1 · 2 · 3 · 4.01 · 5.02 (gains 1 · .62 · .26 · .1 · .05) | 0.5 · 0.32 · 0.16 · 0.07 · 0.04 | pitch starts 1.2% sharp and settles in 12 ms; 3 ms stick ping band-passed at 3.2 kHz |
| Church bell | hum 0.5 · prime 1 · **tierce 1.2** · quint 1.5 · nominal 2 · 2.51 · 3.01 | 2.6 · 1.6 · 1.1 · 0.8 · 0.6 · 0.35 · 0.2 | the minor-third tierce *is* the bell sound |

**Karplus–Strong pluck.** This is the source for guitar, harp, lute, harpsichord and
upright bass.

```js
export function pluck(f, { len = 1.4, damping = 0.5, bright = 0.6, seed = 25 } = {}) {
  const n = secs(len), out = new Float32Array(n), R = rng(seed), D = SR / f, N = Math.floor(D), frac = D - N, line = new Float32Array(N + 2);
  const lp = biquad("lp", 1500 + bright * 7000); for (let k = 0; k < line.length; k++) line[k] = lp(R() * 2 - 1);
  let idx = 0, prev = 0; const fb = 0.996 - damping * 0.012;
  for (let i = 0; i < n; i++) { const a = line[idx], b = line[(idx + 1) % line.length], y = a + (b - a) * frac;
    line[idx] = (y + prev) * 0.5 * fb; prev = y; idx = (idx + 1) % (N + 1); out[i] = y; }
  return norm(dcBlock(declick(out, 0.5)), 0.9);      // filtered noise carries DC: always block it
}
```

Settings for each instrument:

| Instrument | Settings |
|---|---|
| Nylon guitar | damping 0.55, bright 0.3 |
| Harp | damping 0.18, bright 0.28, then low-pass at 6× f |
| Lute | damping 0.5, bright 0.45 |
| Upright bass | damping 0.35, bright 0.15, low-pass at 900 Hz, plus 10 ms finger noise |
| Harpsichord | damping 0.15, bright 1, plus the same note an octave up at 0.5 (the 4′ stop), high-pass at 140 Hz |

**Additive acoustic piano.** Use this for ragtime and music-hall.
- Up to 18 partials, with stiff-string inharmonicity: `B = 0.00011 × (f/130)^0.8` and
  `f_k = k·f·√(1 + B·k²)`.
- Hammer comb: `a_k = (0.25 + |sin(π·k/7.5)|) / k^(1.3 − 0.65·bright·vel)`.
- Two-stage decay per partial: 70% decays at 0.27·τ_k and 30% at τ_k, where
  `τ0 = clamp(2.3·(220/f)^0.55, 0.35, 4) s` and `τ_k = τ0 / (1 + 0.32·(k−1))`.
- **Two strings per note, detuned ±detune/2 cents.** Use 1–2 cents for a concert piano
  and **8–12 cents for honky-tonk**.
- A 14 ms low-passed felt thump, a body peak at 220 Hz +2.5 dB, and a 100 ms damper release.
- Don't normalise the piano. Its level should follow velocity.

**Bass synth**
- Saw plus a sub sine (0.6), into a resonant low-pass whose cutoff starts at 280 Hz + 1400
  and falls back with τ 0.12 s.
- `sat(drive 1.8)`.

**808**
- A sine whose pitch starts at 2.2× the note and drops to it with τ 35 ms.
- `sat(drive 2.2)`, with amplitude decay τ of 0.55 × the note length.

**Supersaw pad**
- Seven saws per note, detuned across ±1.2% and spread across the stereo field.
- Random starting phases, attack 0.25 s, low-pass at 2.2 kHz.

**Brass and woodwinds**

| Voice | Recipe |
|---|---|
| **Brass** | Saw into a low-pass at `f × (1.2 + 7 × wah × env)`. Scoop up 4% into the pitch over 40 ms; vibrato 0.8% at 5.6 Hz, arriving after 0.3 s. `wah` is a 0..1 path: `[[0,.3],[.3,.9],[1,.5]]` is a "wah-wah". |
| **Muted "talking" trumpet** | The brass recipe plus a +7 dB peak at 1.7 kHz (Harmon mute), following a **pitch path** and an **opening path** over a syllable. "Din-" is 0.26 s near A4. "-ner?" is 0.46 s rising B4→E5 with the opening going 0.15→0.95→0.5→0.8. |
| **Clarinet** | Square wave into a low-pass at `f × (2.2 + 3.5 × bright)`, with vibrato 0.6% at 5.2 Hz arriving late. "Yes!" is 0.42 s scooping E5→A5 then falling slightly. |
| **Sax** | Saw plus breath noise, low-pass following the envelope, a +6 dB peak at 1.25 kHz, vibrato after 120 ms. |

**Formant voice.** This is the voice as an instrument: vocal chops, chants, cartoon speech
and animals.
- A saw source, or noise for a whisper, into **three band-passes at the vowel formants**
  with gains 1, 0.5 and 0.25.

| Vowel | F1 | F2 | F3 |
|---|---|---|---|
| a | 850 | 1220 | 2810 |
| e | 610 | 1900 | 2600 |
| i | 320 | 2500 | 3300 |
| o | 560 | 880 | 2540 |
| u | 370 | 950 | 2670 |

- **Vocal chop:** one vowel, 0.24 s, a 6% scoop, vibrato 1.2% at 5.4 Hz. Play hooks on a
  pentatonic scale.
- **Chant / crowd of tiny voices:** five voices, ±1.2% detune, 7 ms apart, one syllable
  each. Put a key click under the hard consonants.
- **Cartoon speech (babble):** syllables of 0.11–0.23 s with random vowels and a pitch that
  falls across each 1.6 s phrase. Low-pass it at about 1.9 kHz so it reads as "talking"
  without words.
- **Goat bleat:** "e" at about 380 Hz falling to 0.86×, with amplitude pulsing at 8.5 Hz.
- **Meow:** pitch rises 1.35× then falls; the vowel goes i→a→o→u.
- **Whisper:** breath = 1, no saw.
- **Megaphone (process any voice):** high-pass at 480 Hz, low-pass at 3.2 kHz, +6 dB at
  1.6 kHz, `tanh × 3.2`, plus a 1.3 ms comb at 0.35.

---

## 4. Foley recipe book

| Sound | Recipe |
|---|---|
| **Mechanical key** | A high-passed noise click (τ 1.8 ms), a band-passed body at 2.3 kHz (τ 12 ms), a low 170 Hz "thock" (τ 30 ms × weight) and a faint 4.2 kHz ring. For key-up: 3.8 kHz click, 3.1 kHz body, shorter. **Give the product ONE seeded key sound and reuse it in every film.** |
| **Knock / wood** | A noise click plus wood modes at 185 / 392 / 820 / 1480 Hz (τ 50 / 30 / 14 / 8 ms) plus a 70 Hz thump, saturated. |
| **Clock tick** | Noise band-passed at 2.6 kHz (Q 6), τ 6 ms. For the tock, 1.8 kHz. |
| **Footstep** | A soft knock (hard 0.15–0.3), low-passed at 1.5 kHz. Clay feet: add a tiny key click. |
| **Pop / bubble** | A sine chirp 280→1500 Hz in the first third, τ 30 ms. |
| **Boop** (cute character beats) | Sine plus 20% triangle, a bend of −18%, τ 70 ms. Pitch it in the song's key. |
| **Squeak** | An FM tone (index 2.2 at 2×) sliding f0→f1, with 30 Hz vibrato at 17 Hz, band-passed at 1.4 kHz. |
| **Slide whistle** | A sine on a smoothstep glide f0→f1, with 1.2% vibrato at 7 Hz. |
| **Whoosh / brush / paper / peel** | Noise into a band-pass whose centre sweeps exponentially, with shape `rise`, `swell` or `fall`. `grain 0.4–0.8` randomly gates it for paper and bristles. |
| **Record scratch** | Two strokes of band-passed noise (centre 500→3100 Hz) with a pitched glide underneath. |
| **Electric zap** | 60 Hz and 120 Hz saws plus noise, `tanh 2.5`, chopped by random 2–12 ms gates, band-passed at 2.4 kHz. |
| **Snore** | A breathy inhale (band-passed noise rising), then a 78 Hz saw rattling at 32 Hz. Pitch it ×3 for a tiny character. |
| **Purr** | Low-passed noise pulsed at 26 Hz, plus a 52 Hz voiced rumble. |
| **Typewriter** | A key click (weight 0.75) plus a bell at 2350 Hz (ratio 2.76) at line end, plus ratchet ticks for the return. |
| **Projector** | 24 Hz gate clicks (high-passed noise, ±3% jitter), 50 and 100 Hz hum, and fan noise band-passed at 900 Hz. |
| **Crowd walla** | About 18 formant voices at 110–290 Hz with random vowels and breath 0.25. Scale energy to the action. |
| **Morse** | A 640 Hz sine with 3 ms edges. Dot = 1 unit, dash = 3 units; the gap inside a letter is 1 unit, between letters 3. |

---

## 5. Mix chain and its numbers

```
buses (gain · high/low-pass · sidechain amount) ──┬─► sum
                                                  ├─ send ─► Freeverb ─► high-pass 220 ─┐
                                                  └─ send ─► ping-pong delay ───────────┤
sum + returns ─► master EQ ─► PRE (headroom) ─► glue compressor ─► LUFS gain ─► limiter ─► zero the cuts ─► WAV
```

- **Freeverb** (Jezar): 8 damped combs (1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617
  samples at 44.1 kHz, scaled to 48k) and 4 allpasses (556, 441, 341, 225). We used
  room 0.76–0.82, damp 0.35–0.45, wet 2.4–2.8, predelay 20 ms. Sends: dry percussion
  0.1–0.16, melodic 0.2–0.3, chant and choir 0.5.
- **Delay:** ping-pong at a dotted eighth (0.75 beat), feedback 0.2–0.25, tone 3 kHz.
  Send 0.06–0.12 on leads only.
- **Sidechain:** an envelope from the kick times. Depth 0.4–0.55, attack 4 ms,
  release 0.16 s. Apply it to bass (0.35–0.45) and pads (0.4–0.5).
- **Master EQ:** high shelf at 3.2 kHz +1.5 to +2 dB, and a peak at 250–300 Hz −1.5 dB
  (Q 1) to remove mud.
- **Gain staging (the lesson that matters most):**
  - `PRE ≈ 0.45–0.5` (about −6 dB) *before* the glue. The limiter should catch peaks, not
    set the level.
  - Then the glue: RMS, 2:1 above −18 dBFS, 10 ms / 200 ms, no makeup.
  - Then raise `LUFS gain` until the integrated loudness reads about −14.
  - Then the look-ahead limiter: 4 ms look-ahead, 80 ms release, ceiling about 0.75–0.78
    linear, so true peak stays at −1 dBTP or lower after AAC.
- **Cuts (designed silence):** compute reverb and delay **per segment**, and choke the
  tails at the cut with a 40 ms fade. Otherwise the reverb resumes underneath the silence.
  Zero the cut range *after* the limiter so it's true digital zero.

---

## 6. Scoring patterns that tell the story

- **Change the band on the bar where the story changes.** In an era montage that's every
  bar, at one tempo.
- **Count the tension.** A clock on the eighths, a heartbeat that quickens, and a minor pad
  whose filter opens bar by bar.
- **Make the pile-up rise.** Each new item pops on the next note of a climbing minor
  pentatonic.
- **Resolve to major and make the release a melody.** Each thing that's fixed or tidied
  plays the next note.
- **Stop dead before the reveal.** The old sound ends on the exact frame, then a breath,
  then about 0.3 s of digital zero, then the first new sound alone and dry.
- **Let instruments talk.** A muted trumpet or clarinet says the one word that matters.
  Nobody needs real dialogue.
- **Give every gag a stinger.** A brass hit, a slide whistle or a boop, in key.
- **Hide a musical joke.** For example, the printing-press bar plays its phrase backwards.
- **The product's signature sound plays on the frame it's used.** Take it from the
  animation curve: the first frame the key reaches its full travel, not the frame the
  finger starts moving.
- **The payoff is the loudest bar.** The intro sits about 3–6 dB lower, so the arc is
  audible.

### From EVENTS to foley

```js
const counts = {};
for (const e of EVENTS) {
  const t = e.frame / 30, pan = Math.max(-0.8, Math.min(0.8, (e.x - 0.5) * 1.6)), c = (counts[e.kind] = (counts[e.kind] ?? 0) + 1);
  switch (e.kind) {
    case "key-down": sess.put("foley", norm(keyClack({ weight: 1, seed: 501 })), t, 0.75, pan); break;
    case "pop": sess.put("fx", norm(pop()), t, 0.3, pan); break;
    // … one case per kind. Use c to vary the seed or pitch; dedupe events that share a frame.
    default: console.warn("unhandled kind", e.kind);   // add a case for every kind it prints
  }
}
```

- Place a voice about 60 ms *before* its word appears on screen.
- When many characters stomp on the same frame, play one sound, not twenty.

---

## 7. Prove it (measure, don't guess)

**Integrated loudness and true peak.** Target about −14 LUFS and −1 dBTP or lower:

```bash
ffmpeg -hide_banner -nostats -i out/film.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
```

**Loudness per bar.** The payoff bar must be the loudest. Use `bar` seconds, `n` bars:

```bash
ffmpeg -hide_banner -nostats -i out/film.mp4 -af ebur128=metadata=1,ametadata=print:key=lavfi.r128.M -f null - 2>&1 | \
awk -v bl=2.0 -v nb=12 '/pts_time/{split($0,a,"pts_time:");t=a[2]+0} /lavfi.r128.M=/{split($0,b,"=");m=b[2]+0;if(m>-70){i=int(t/bl);s[i]+=10^(m/10);c[i]++}}
END{for(i=0;i<nb;i++) printf "b%d %.1f  ", i+1, (c[i]?10*log(s[i]/c[i])/log(10):-99); print ""}'
```

**Band balance.** dB RMS per band. Our films sat around −19 (40–250 Hz), −20 (250 Hz–2 kHz),
−29 (2–8 kHz) and −34 to −40 (8 kHz and up). If the lows run more than ~3 dB over the mids,
the mix is muddy.

```bash
for b in "lowpass=f=250,highpass=f=40" "highpass=f=250,lowpass=f=2000" "highpass=f=2000,lowpass=f=8000" "highpass=f=8000"; do
  ffmpeg -hide_banner -nostats -i out/score.wav -af "$b,astats=measure_overall=RMS_level:measure_perchannel=none" -f null - 2>&1 | grep -m1 "RMS level"; done
```

**Silence is zero.** Read the WAV samples across the cut. The maximum absolute value must
be exactly 0.

**Sync.** Print the peak in 5 ms windows around the cue's time. The transient must start in
the window at `frame / 30`.

**See the structure.** This shows gaps, mud and missing sections at a glance:

```bash
ffmpeg -i out/score.wav -lavfi "showspectrumpic=s=1200x360:legend=0:scale=log:fscale=log" out/spectrogram.png
```
