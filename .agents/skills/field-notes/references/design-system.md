# Field Notes — Design System V4

Paper and forest. One green. For anything with a screen or a page: tools, apps,
sites, documents, slides, films, SVG motion. It is all interface.

V4 is V3's system in V2's colours, with no brand inside it (lineage: QWEE DS V1 → V3).
Tokens: `tokens/tokens.css`. Components: `kit/kit.css`. Starting points: `examples/`.
Render, PDF, MP4, single-file and contrast tools: `scripts/`.

**Contents:** 0 Read this first · 1 It's all interface · 2 Words · 3 Colour · 4 Type ·
5 Space, layout, geometry · 6 Texture · 7 Components · 8 Motion · 9 Media (9.1 tools ·
9.2 web · 9.3 documents · 9.4 slides · 9.5 film · 9.6 SVG motion · 9.7 stills · 9.8 data) ·
10 Registers · 11 Make it yours · 12 Checklist · 13 Changes from V3 · 14 Files

---

## 0. Read this first

If you read nothing else, these twelve rules produce something on-system.

1. **One job per screen.** One primary action, one rung-1 element, one moving idea.
2. **Show it working, then name it.** The product doing its job comes before the sentence about the job.
3. **Write less.** Use the budgets in §2. If a sentence repeats the figure, heading or label, delete it.
4. **Emphasis ladder:** fill > tint > outline > text.
5. **Rank with grey before size.**
6. **Mono** for data and labels. **Sans** for interface and prose. **Serif** for one first line.
7. **One green. Amber means attention.** No other hues.
8. **Square by default.** Corners only where §5 allows.
9. **Space by the ladder** (§5). Inside < between items < between groups < between sections.
10. **Nothing travels; nothing moves its neighbours.** Reserve space for every state.
11. **Ships finished.** The still frame or no-JS page explains the whole thing.
12. **Every number checkable.** Say where it stops being true, right beside it.

---

## 1. It's all interface

A tool, a PDF page, a film frame and a landing page are the same problem: one
person, one rectangle, a few seconds.

**Attention**
- The first screenful answers the first question. That is "what is this?" for a stranger and "are we on track?" for a user.
- One metaphor per screen. Two ideas on one screen halve each other. The system gives the voice, not the idea: for a title, a cover or an ad, find the one visual metaphor in the subject first, then build it from rules, blocks, mono and the ladder.
- Cut second readouts. If the window footer already says RENDERING, the caption doesn't repeat it.

**Hierarchy**
- The ladder. Rung 1 = solid fill (only one per page). Rung 2 = accent fill (primary data). Rung 3 = hairline outline (supporting). Rung 4 = text ranked by grey. Only true peers share a rung.
- Size jumps are for titles and figures. Inside a card or table keep sizes close; rank with ink → grey → faint.
- Shared edges: labels share a left edge, numbers share a right edge, chips share a baseline.
- Group what belongs together in one frame (§7 group frame). Don't scatter it.

**State**
- Design every state: empty, loading, partial, full, error, disabled, offline.
- Reserve space for them. Min-height = the tallest state; min-width = the longest label.
- Respond within 100 ms. Show progress past 1 s and time left past 10 s.
- Undo beats confirm. Confirm only what can't be undone, and name it: "Delete 3 files".

**Trust**
- A number goes on the page only if someone could reproduce it.
- In a demo, never show a failure state you haven't fixed.

**Access** (not optional)
- Text contrast is ≥ 4.5:1 when small, ≥ 3:1 when large, and UI indicators are ≥ 3:1. §3 has the measured pairs.
- Focus is always visible: 2px ring, forest on light, sage on dark, 2px offset.
- Targets are ≥ 24px for a pointer and ≥ 44px for touch. Everything is reachable by keyboard, and shortcuts are shown.
- Colour never carries meaning alone. Pair it with a label, a shape or a position.
- With reduced motion on, show the finished state. Interactive controls still work.

---

## 2. Words

V3's outputs wrote too much, so V4 sets budgets. They are ceilings, not targets.

| Element | Budget |
|---|---|
| Headline | ≤ 8 words |
| Lede under a headline | 1 sentence, ≤ 20 words |
| Section intro | 0–1 sentence |
| Card / step body | ≤ 2 lines (~20 words) |
| Figure caption (the "receipt") | 1 sentence, ≤ 14 words |
| Button | verb (+ object), ≤ 3 words; facts go in the mono sub-line |
| Label, eyebrow, chip | ≤ 3 words |
| Tooltip | ≤ 10 words |
| Toast | ≤ 6 words + one action |
| Error | what happened + what to do, ≤ 15 words |
| Empty state | 1 line + 1 action |
| Web first screen | ≤ 40 words in total |
| Document page | ≤ 60 words of prose; the rest is tables, figures, labels |
| Slide | ≤ 15 words outside the figure |
| Film / motion | ≤ 7 words in the main line; small mono labels (≤ 3 words each) and numbers don't count. Hold 0.3 s per word + 1 s |
| Share card | ≤ 12 words |

**Rules**
- Write it, then cut it in half. If the figure still makes sense, cut again.
- Delete intros ("In this section…"), outros, restatements, hedges, and any adjective a number could replace.
- Prefer a mono label to a sentence: `12 DAYS · BRIEF TO DELIVERY` beats a line of prose.
- Buttons are verbs: "Export", "Start queue". Facts go in the sub-line: `PDF · 4 PAGES`.
- Describe the situation before the feature: "You have 40 files to rename", not "Batch rename utility".
- Say where it stops being true, next to the number: "48 h — longer past 20 min of footage."
- Placeholder copy is real copy: short and plausible. Never lorem ipsum, never filler paragraphs.
- Sentence case everywhere. UPPERCASE only for mono labels.
- Banned: game-changer, seamless, effortless, supercharge, unlock, elevate, "excited to announce", "in today's world", any unqualified "faster".

---

## 3. Colour

The light theme and every accent use V2's palette, hex for hex. Two changes:
- **Faint is ink at 62%.** V2's 45% measures 2.79:1, which is too low to read.
- **Dark mode has its own deep grounds.** V2's forest at full-page size reads olive and muddy. Dark grounds are forest-950 pulled toward neutral; the V2 greens stay as accents.

### Palette

| Token | Hex | Role |
|---|---|---|
| `forest-950` | `#14180F` | Darkest ink, terminals, a dark band on a light page |
| `forest` | `#1E2618` | Solid fill (rung 1 on light), title bars |
| `sage-dim` | `#8FB07C` | Secondary on dark, swarm field, data ramp |
| `sage` | `#B8D4A4` | The accent fill (rung 2); text on forest |
| `sage-bright` | `#D2E6C2` | Rung 1 on dark, large text on forest |
| `paper` | `#FAF9F4` | Light ground |
| `card` | `#FFFFFF` | Light panels, lifted by a hairline |
| `ink-paper` | `#1B2015` | Text on paper |
| `grey-paper` | `#71716A` | Secondary text on paper |
| `amber` | `#A8741D` | Attention only. A marker or fill, never small text |
| `deep-0 / 1 / 2` | `#0F120E` `#161A14` `#1D2219` | Dark ground / panel / raised |
| `ink-dark` | `#E8F0DE` | Text on dark (sage-bright pulled toward paper) |
| `grey-dark` | `#A9B59E` | Secondary text on dark |

### Roles (what components use)

| Role | Light | Dark |
|---|---|---|
| `surface` | paper | deep-0 |
| `panel` | card | deep-1 |
| `inset` | ink 4% into paper | between deep-0 and deep-1 |
| `ink` | ink-paper — 15.8:1 | ink-dark — 15.1:1 |
| `grey` | grey-paper — 4.7:1 | grey-dark — 8.2:1 |
| `faint` | ink 62% — 4.6:1 | ink 56% — 5.5:1 |
| `ahead` (ledes) | ink 74% — 6.9:1 | ink 76% — 9.1:1 |
| `hairline` / `-soft` | ink 12% / 6% | sage 16% / 8% |
| `solid` / `on-solid` (rung 1) | forest / sage | sage-bright / forest-950 |
| `accent` / `on-accent` (rung 2) | sage / forest | sage / forest |
| `tint` | sage 18% into card | sage 10% into deep-1 |
| `focus` | forest | sage |
| `band-tint` | sage 14% into paper | sage 6% into deep-0 |

### Rules
- On paper, text is ink, grey or faint. On a dark ground, text is ink-dark or grey-dark, and sage only for an accent.
- **Sage is never text on paper** (1.53:1). Nor is sage-dim (2.30:1). On paper they are fills, rules and bullets. When a fill carries meaning, give it a forest hairline or a label.
- **Amber is the only signal hue.** It covers warnings, errors and destructive actions. Severity lives in the words and the rung, not in more hues. Amber is a marker (5–6px square) or a fill. The words beside it are ink.
- In dark mode, panels separate by hairline, not fill (deep-1 vs deep-0 is 1.07:1). That keeps big areas calm.
- **A dark band on a light page is a dark-theme island.** Put `data-theme="dark"` on it and set its ground to `forest-950`. Never hand-pick colours inside it.
- One tinted band per page. One "light" per page: a radial of sage at 26% behind the one lit object.
- Theme is the person's choice. Default to paper (or whatever was asked for), offer a switch, persist it, and apply it on `<html>` before first paint.
- **Data:** the ramp is `data-1…4`: forest → sage-dim → sage → sage 40% on light; sage-bright → sage-dim → sage 45% → sage 22% on dark, so neighbours stay distinct. Amber marks the one value that needs attention. Label directly instead of using a legend. Four series at most; beyond that, use small multiples.

---

## 4. Type

Three roles. The defaults are OFL and bundled in `assets/fonts`. Swap them by role, not by taste.

| Role | Default | Job |
|---|---|---|
| `sans` | Space Grotesk 400–700 | Interface, prose, titles in tools and data pages |
| `mono` | JetBrains Mono 400–700 | Labels, data, numbers, code, chips |
| `serif` | Instrument Serif 400 + italic | The first line a stranger reads: web heroes, covers, film titles, section slides |

**The turn.** A serif headline puts its second clause in italic: *Plan the shoot.
Ship the cut.* The italic is the payoff, never a random word. Weight 400,
tracking −0.02 to −0.03em, never under 24px. Never in tools, tables or body text.

| Role | Tool px | Web | Print pt | Slide px | Film px (1080w) |
|---|---|---|---|---|---|
| Hero (serif) | — | clamp(3.4rem, 8vw, 6rem), lh .92 | 44–56 | 120 | 132–150 |
| Section | 20 sans 600 | clamp(2.2rem, 4.4vw, 3.5rem) serif | 26–30 serif / 20–22 sans | 72–84 | 88 |
| Title | 15 | 21 | 13–15 | 40 | — |
| Body | 13, lh 1.45 | 17–18, lh 1.6 | 10–12 | 28–30 | — |
| Figure (mono 600–700) | 24 | clamp(1.9rem, 3.4vw, 2.6rem) | 20–26 | 96 | 140 |
| Eyebrow (mono 500, 0.18em) | 10 | 11 | 8–9 | 18 | 30 |
| Micro / chip (mono 500, 0.12em) | 9.5 | 10 | 6–6.5 | 16 | 26 |

- Units keep their real case inside uppercase labels: `Mb/s`, `kB`, `ms`. Wrap them in `<span class="unit">` (the kit turns the transform off), or write them in words.
- Faint is never under 62% on light or 56% on dark. Small mono seen at a distance (slides, film, a phone at arm's length) uses `label-far` (72%).
- Any number that changes or lines up gets tabular figures.
- Prose runs 45–75 characters per line. A lede runs 30–38.
- Numbered eyebrows: `01_TIMELINE`, `GRP_02 // CUTDOWNS`, `NOTE :: SCOPE`.
- A solid caret means "about to continue". A blinking caret means idle. Typed text gets one hesitation per piece; a constant rate reads as a machine.

---

## 5. Space, layout, geometry

### The spacing ladder
Scale: `4 · 8 · 12 · 16 · 20 · 24 · 32 · 48 · 64 · 96 · 128`. Hairlines are always 1px.

Space says what belongs together. Each step up is **at least 1.5×** the one below:

| Step | Tool | Web | Print (px @96dpi) | Film (1080w) |
|---|---|---|---|---|
| Inside an item (label → value) | 4–8 | 8–12 | 6–8 | 12–16 |
| Between items in a list | 8–12 | 12–16 | 10–14 | 22–28 |
| Between groups | 20 | 32–48 | 24–32 | 60 |
| Between sections | 32 | 96–128 | a page | a shot |

- Lists: card-like items get ≥ 12px between them and ≥ 12px padding inside. Rows run 38px in tools (52px when two lines), 44–52px on the web, and 40–46px in print.
- If two lists sit side by side, the gutter between them is larger than the gap inside either.
- When in doubt, add space between groups, not inside items.

### Layout by medium
- **Tool:** top rail 48 · sidebar 232 · canvas · inspector 300–320 · status bar 28. Gutter 16–28.
- **Web:** wrap 74rem · bar max 62rem · stage 52rem · side gutter 16 (phone) / 24 / 48. No horizontal scroll at 320px.
- **Print:** 960 × 540 pt (16:9), or A4/Letter portrait. Margins 48pt, rail 52pt, footer 26pt. 12 columns; splits 7/5, 8/4, 3-up.
- **Slides:** 1920 × 1080, margins 120 / 84. One claim, one figure.
- **Film:** 1080 × 1920 first. Keep words inside the central 4:5 (1080 × 1350) so feed crops keep them. On Reels, TikTok and Shorts, the app's own UI also covers the bottom ~420px (caption, audio), the right ~140px (buttons) and the top ~220px. Keep text and faces clear of those. Wide is a second composition, not a crop.

### Radius by medium
`data-medium` on any container switches it.

| Token | Value | Web | Tool | Print · Film · Slides |
|---|---|---|---|---|
| `r-0` | 0 | chips, swatches, cells | everything, switches too | everything |
| `r-sm` | .55rem | buttons, inputs | 0 | 0 |
| `r` | 1.1rem | cards, windows, the bar | 0 | 0 (Editorial film windows may use it) |
| `r-lg` | 2.25rem | bands, figure grids | 0 | 0 |
| `r-pill` | 999px | segmented controls, switches, cite chips | 0 | 0 |

Softness on a landing page reads as considered. In a tool it reads as a toy.

**Shadows:** none in tools or print, where hairlines do the work. On the web, a lifted
window gets `0 30px 70px` ink 14%, and the sticky bar gets a soft shadow once the page scrolls.

---

## 6. Texture

Texture goes in the margins, never under data or body text. It is seeded, so
re-renders are identical. Use one texture per surface, plus grain on the web.

- **Dot grid.** The paper itself, for documents and empty tool canvases. It may run under page titles; cards are solid, so they mask it. 30px pitch on screen, 26–34pt in print, dots r 0.6–0.8pt at ink 10–14%.
- **Swarm field.** For covers and dark pages. Walk a grid (pitch 6–9) and drop a square (about half the pitch) with probability `0.045 + Σ gaussian clusters`. One dominant cluster and two weak ones. Use sage-dim at a varied opacity of 0.07–0.26. Exclude every content box and the headline (+8–12px). Compute those boxes from the layout, never by hand.
- **Plus-field.** `+` marks in a 4-tone ramp, arm ~3pt, spacing ~16pt, filling a card's empty corner. One per document.
- **Pixel cluster.** 3×3 squares with 1–2 knocked out. Used for bullets, brand marks and pins. Documents and films use these instead of icons. Tools may use a 16px line icon set at 1.5px stroke.
- **Grain** (web). A fixed feTurbulence layer at 4.5%. It never scrolls.
- **Halftone** (Loud register) over a colour block, never over type. **Dot density** (Ambient register): density is value.

---

## 7. Components

Every component reads role tokens only (`kit/kit.css`), so the same markup works
light or dark, in a tool or on the web.

- **Rail (tool).** 48px tall, inset fill, bottom hairline. Brand on the left (pixel cluster + wordmark + mono sub-line), tabs in the centre (the active tab is ink with a 2px focus-colour underline on the rail's edge), status chip and ⌘K search on the right.
- **Bar (web).** A floating card, not a strip. Sticky 0.75rem from the top, max 62rem, panel at 86% with a 16px blur, hairline, `r`. Holds the brand, 3–4 links, a theme switch and one compact primary button.
- **Buttons.** Primary = rung 1. Secondary = hairline. Ghost = text. Attention = secondary + amber marker + an explicit verb. Disabled = faint, no fill. Heights: tool 32, web 44. The web hero button is a glyph box plus a two-line label (sans verb over a mono sub-line of facts at 72%). Loading keeps the label and the width; only the glyph changes.
- **Chips.** Square, mono uppercase 9.5–10px, 20px tall. Variants: solid / accent / tint / outline. Live chips get a 5px breathing square. Owner coding is fixed: studio/us = solid, client/them = outline, both = tint.
- **Kbd.** Mono 10px in a hairline box, 2px bottom border. Show shortcuts next to the actions they trigger.
- **Field.** Mono micro label above, control below (32 tool / 44 web), panel fill, hairline. Focus = 2px focus ring. Error = amber border + amber marker + one ink sentence under it.
- **Segmented control.** One container, fixed width. The active segment is an ink fill. Use it instead of a row of loose chips whose widths could change.
- **Switch / checkbox.** A real `<button aria-pressed>`. Square in tools, pill on the web. Checkboxes are always square. The kit pads the tool switch's hit area to at least 24px.
- **Slider, select, number.** `.range` is a 2px track with a square thumb, its value shown in mono beside it. `.select` and `.input.num` share the field's height, fill and hairline; numbers are right-aligned and tabular. A slider that drives a number keeps both in step.
- **Setting row.** `.setting`: label and hint on the left, the control on the right, a soft hairline between rows.
- **Table.** Mono. Faint uppercase header, hairline under it, soft hairlines between rows. Rank cells by grey. Numbers right-aligned and tabular; the key column is ink 600. A selected row gets a tint plus a 2px focus marker on the left. Sticky header. A total is a rung-1 band under the table, not a row.
- **KPI / figure.** A mono value plus a micro label. No code tags (`KPI_01`), and no padding tiles to fill a row. **Figures grid**: 3-up on hairlines (1px gap on a hairline ground). Each figure gets one sentence that makes it a receipt.
- **Card / group frame.** Panel, hairline, padding 20–30. A group frame has a rung-1 header tab, 28px tall: mono label on the left, meta at 70% on the right. Members tile inside it.
- **Phase band.** Flush segments sized in proportion to the data. They walk tint → sage → forest so the sequence reads as progress. Labels sit inside.
- **Window** (redrawn UI for web, slides, film). Forest title bar with a mono 10px label and three square dots. On dark the title bar lightens (sage 13% into panel). Min-height = its tallest state. **Redraw UI; never screenshot it.**
- **Command block.** forest-950, mono, block caret, `pre-wrap` + `overflow-wrap: anywhere`. The copy button sits outside the `<pre>`.
- **Toast.** Inverse (ink ground, surface text), ≤ 6 words + Undo, 4 s. Never use a toast for an error that needs action.
- **Tooltip.** Inverse, mono 10px, square, 400 ms delay, ≤ 10 words.
- **Empty state.** Pixel cluster + one line + one primary action.
- **Skeleton.** Boxes at their final size, hairline fill, breathing opacity (sine, 1.6 s). No shimmer travelling across.
- **Progress.** A 2px bar plus `12 / 40` in mono. Determinate whenever possible.
- **Status bar.** Mono 9.5px uppercase, faint. Context on the left, live state on the right.
- **Dialog.** Native `<dialog>`, one primary action, Escape closes it, focus returns to the trigger.
- **Fold.** Put answers nobody needs until they need them behind `<details>`, with a count chip.

---

## 8. Motion

### Rules
1. **Nothing travels.** State changes happen in place. Words fade in where they will stay; bars grow from their own baseline. If the eye has to chase it, it says nothing.
2. **Nothing moves its neighbours.** Lay out at the final size, then reveal.
3. **Ships finished.** The markup is the last frame and the script rewinds it. Scope every hiding rule under `:root.js`. Reduced motion gets the end state.
4. **One gesture per event.** Words arrive at word rate, never per character.
5. **A payoff needs silence in front of it.** Things stop; they don't just get quieter.
6. **Play only while visible.** Loops pause off-screen.
7. **Observe the parent, animate the children.** A clipped or zero-opacity element can report zero size forever.
8. **Absolute labels when two things overlap in time.** A container must never sit empty mid-transition.

### Curves (GSAP name → CSS)

| Gesture | Curve | CSS |
|---|---|---|
| Reveal, falling away | `expo.out` | `cubic-bezier(.16,1,.3,1)` |
| Decisive: type, wipes | `power4.out` | `cubic-bezier(.22,1,.36,1)` |
| Arrives under its own weight | `back.out(1.7)` | `cubic-bezier(.34,1.56,.64,1)` |
| Depth, group moves | `power3.inOut` | `cubic-bezier(.76,0,.24,1)` |
| Reflow (unremarkable on purpose) | `power2.inOut` | `cubic-bezier(.65,0,.35,1)` |
| Leaving | `power2.in` | `cubic-bezier(.32,0,.67,0)` |
| A word fading in | `power1.out` | `cubic-bezier(.5,1,.89,1)` |
| Drift, breath | `sine.inOut` | `cubic-bezier(.37,0,.63,1)` |
| Clocks, counters | `none` | `linear` |

### Timings

| Thing | Value |
|---|---|
| Hover / press (tools) | 120–150 ms, colour/border/opacity only |
| State swap | out 0.2 s `power2.in`, in 0.3 s `power2.out` |
| Scroll reveal | 720 ms `expo.out`, 18px rise, 70 ms stagger, max 8 |
| Word cadence (speech pace) | one every 0.29 s |
| Word fade | 0.28–0.30 s, 5px rise out of a 5px blur |
| Typing | ~20 chars/s, one hesitation per piece |
| Hold to read | 0.3 s per word + 1 s (a sentence ≈ 2.4–2.6 s) |
| Counter steps | ≥ 8 frames apart |
| Loud beat | 12 frames at 30 fps, no fades, 2-frame snaps |
| Pacing between neighbours | each step ≥ 25% shorter, or it doesn't read as accelerating |

**A live meter is a signal, not a dice roll.** Drive the bars every frame from a
level and a pulse, never from random heights on a timer:
`h = 0.18 + level·(0.15 + 0.7·talk) + pulse·0.3·centre`, where
`talk = (0.35 + 0.65·slow·fast)·(0.55 + 0.45·centre)`,
`slow = ½ + ½·sin(2.1t + 0.9i)`, `fast = ½ + ½·sin(7.3t + 1.53i)`, `centre = 1 − |i − mid| / mid`
(1 at the middle bar, 0 at the ends). `level` runs 0–1, eased up while the sound is on and
down when it stops. `pulse` is kicked to 1 on each beat or word and multiplied by 0.92 every frame.

### By medium
- **Tool:** only feedback and live status. No entrance animation on routine screens.
- **Web:** reveal once on scroll; replay a figure while it is in view.
- **Film / frame-indexed renderers** (HyperFrames, Remotion, SVG): every frame is a pure function of `t`. Seed any randomness, bundle the fonts, no network. Frame 0 is already moving. Every `fromTo` needs `immediateRender: false`. Show depth with blur, not only scale. Do perspective by hand: `scale = P/(P+z)`.
- **SVG motion:** design in a fixed viewBox. Animate `transform`, `opacity`, `stroke-dasharray` (with `pathLength="1"`) and filter blur. The file's static markup is the last frame. Support `?t=` so any frame can be rendered (see `examples/11-motion.svg`).

---

## 9. Media

### 9.1 Tools and apps
- Density: body 13px, labels 9.5–10px mono, rows 38px, controls 32px. Square everything.
- Layout: rail → sidebar (views, filters, saved views with counts) → canvas (eyebrow, title, primary action at top right, 3–4 KPIs, then the work) → inspector (the selected thing: preview, key–value rows, progress, log, actions) → status bar.
- Keyboard first. ⌘K for commands, single-key shortcuts shown as kbd chips, Enter for the primary action.
- Direct manipulation over forms. Undo over confirm. Errors go inline, next to their cause.
- Remember view, filters, selection and theme.
- Selected = tint + focus marker. Focused = ring. Hover = hairline-soft tint. They never look the same.
- **Settings screens.** A sidebar lists the sections, each with its live value ("Nightly", "3 folders"). Each setting is a row: label plus a one-line hint on the left, the control on the right, rows 52px apart. Changes apply as you make them, with an undo toast; add a Save button only when changes must go together. Destructive settings get the attention marker and a named verb. The page's one primary action (e.g. "Sync now") lives in the status panel or header, not in every section.
- Controls that show state (an on switch, a checked box, the selected segment) and group-frame tabs are not "rung 1". The one-rung-1 rule is about what the page is about: a total, a deadline, the primary action.
- Inner-scroll layouts: render at the window size for the real view, then once at a tall height to check everything below the fold.

### 9.2 Web pages
Default order for a product page:
1. The bar.
2. First screen (≤ 40 words): eyebrow → serif headline with the turn → one sentence → one primary button (facts in the sub-line) + one text link → the product working, lit by the one light. Everything fits in the first 900px.
3. How it works: three cards on the tinted band.
4. One scene per job, alternating copy and figure. Each figure ships finished.
5. Proof: a figures grid (each number with its caveat), often on a dark band.
6. Close: a short FAQ with folds, beside a sticky CTA card (3px forest→sage rule, a serif one-liner, the facts in mono, one button).
7. Footer.

Render every section at build time; JavaScript only enhances. Default to paper, with a theme switch applied before first paint. Alternate bands: paper → tint → paper → dark → paper.

### 9.3 Documents and PDF
- Canvas 960 × 540 pt (16:9), or A4/Letter portrait. Two build routes, both deterministic:
  - **HTML + CSS → `scripts/pdf.sh`** (Chrome print) with `@page { size: 960pt 540pt; margin: 0 }`. Design in px at 96 dpi (1280 × 720). See `examples/07-document.html`.
  - **PyMuPDF**, absolute layout in points, static font instances (`assets/fonts/*.ttf`), `subset_fonts()`, `save(garbage=4, deflate=True)`.
- **Separate content from drawing.** All copy and numbers live in one data block. Totals, percentages and bar widths are derived from it, never typed by hand.
- Every page shares a frame: rail (brand, section tabs with the active one underlined, a status chip) and a footer strip (`ISSUER // PROJECT // CONFIDENTIAL` · `PAGE 02 / 03`). A one-pager drops the tabs: the rail holds the brand, the document title and the date.
- Portrait A4 (595 × 842 pt) or Letter (612 × 792 pt) uses the same frame and rules. Margins become 40pt, and content stacks in one or two columns.
- Page types:
  - Cover: forest-950 + swarm, eyebrow, serif title with the turn, 2–3 KPIs (one rung 2), and a transparent outline meta card.
  - Narrative: serif section title, sans body.
  - Data (timeline, deliverables, cost): sans + mono only, tables in white sheets on a dot-grid page.
  - Numbers: a figures grid.
- One rung-1 element per page: a deadline chip, the delivery phase, or the total band. Phases walk tint → sage → forest across both the band and the row markers.
- The logo comes from the product, not the system. Key out its background, centre it optically in the meta card at ≤ 55% of the card's width, never on a white plate.

### 9.4 Slides
The title is the claim: "Cutting the intro *doubled watch time*". Then one figure,
1–2 side figures, a source line in `label-far`, and a page number. ≤ 15 words
outside the figure. Section slides use the serif; data slides use mono numbers at 96px.

### 9.5 Film and video
- Portrait 1080 × 1920 first, 30 fps. Wide is a second composition. Stills and motion cards are the same composition at a single frame.
- Frame 0 is moving: a film doesn't open on a static title card or a fade-up. One idea per shot. When someone asks for a title card or cover frame, that's a still (§9.7): compose it as the film's first or last frame at a single moment.
- Pass the muted test: it must make sense without sound.
- Redraw the UI at film scale; never upscale a screenshot. The product does the work, not the edit.
- ≤ 7 words in the main line (labels and numbers don't count); words stay inside the 4:5 safe zone and clear of the platform's UI (§5); small labels at `label-far`.
- Measure the silence before the payoff, and leave it alone.

### 9.6 SVG motion
Use it for self-contained loops, explainers, and "SVG movies". Rules: §8. A fixed viewBox,
system fonts via `@font-face`, the static markup as the last frame, a `?t=` scrub for
export (`node scripts/render-motion.cjs` → MP4), and `prefers-reduced-motion` → end state.

### 9.7 Stills and cards
Share card 1200 × 630 · carousel 1080 × 1350 · square 1080. Editorial register:
eyebrow, serif headline, one product element, the brand in a mono footer. ≤ 12 words.

### 9.8 Data visualisation
- One chart, one claim, and the title states the finding.
- Ramp `data-1…4`. Amber marks the one value that needs attention. Before and after uses the ramp (light outlined → solid forest), with the change marked by a dashed forest line and a mono label.
- Label directly; no legend. Gridlines in hairline-soft, the baseline in hairline. Mono tabular numbers.
- Line charts: 1.5–3px line, area at 25%, the last point marked with a square.
- Every chart has a source line that says what wasn't measured.

---

## 10. Registers

Four looks, one palette. Each piece picks one. A campaign interleaves them so the
format isn't recognisable before it's read.

| | **Quiet** | **Editorial** | **Loud** | **Ambient** |
|---|---|---|---|---|
| For | tools, apps, documents, demos | websites, covers, launch films, cards | announcements, hooks, plates | loops, backgrounds, mood |
| Ground | paper / deep, dot grid | paper, grain, one light | sage field, edge to edge | paper, ink-dot world |
| Colour | one soft accent on neutral | one accent + one tinted band | colour is the field; forest is the type | one solid sage thing |
| Type | sans + mono | serif headline, sans, mono | sans 700 uppercase, −0.05em; mono 700 | none until the end line (≤ 7 words, ≥ 88px) |
| Shape | squares, hairlines | radius scale | 16px forest rules, solid blocks, halftone | dots; density is value |
| Motion | in place, eased, 12–20 frames | `expo.out` reveals | no fades; 2-frame snaps on a 12-frame beat | slow; decohere rather than fade |

---

## 11. Make it yours

The system is structure; the green is a default. To fit another brand, swap the
palette tokens in `tokens.css` and keep these relationships:
- A dark neutral tinted toward the accent (`forest-950`, `forest`), one light accent fill plus a lighter and a dimmer step (`sage`, `sage-bright`, `sage-dim`), a warm-neutral paper and card, an ink and a grey tinted the same way, and one attention hue.
- Dark grounds are the dark neutral pulled toward grey (`deep-0…2`), never the accent at full size.
- Check every pair: ink on paper ≥ 12:1, grey and faint ≥ 4.5:1, accent text on the dark fill ≥ 4.5:1, focus ≥ 3:1.
- Fonts swap by role. Keep one sans, one mono and one display face, with the display face used for one line only.
- No logos live in the system. A product puts its mark in the rail or bar brand slot, or in the cover meta card.

---

## 12. Checklist

**Any medium**
- [ ] One job, one rung-1 element, one light, one tinted band.
- [ ] Words within the §2 budgets. Nothing restates its figure.
- [ ] Spacing ladder holds: lists breathe, groups are clearly apart.
- [ ] No hue but green and amber. Sage is never text on paper.
- [ ] Every number reproducible, its limit beside it.
- [ ] Every state designed. Space reserved. Nothing travels.
- [ ] Contrast measured; focus visible; keyboard works; reduced motion = end state.

**Tool:** square, 13px, rail → sidebar → canvas → inspector → status bar, shortcuts shown, undo over confirm.
**Web:** first screen ≤ 40 words, builds without JS, theme set before paint, no horizontal scroll at 320px.
**Document:** content block separate, numbers derived, rail + footer on every page, texture masked from computed boxes.
**Film / SVG:** frame 0 moving, deterministic, muted test, 4:5 safe, last frame = static markup.

---

## 13. What changed from V3

| V3 said | V4 says | Why |
|---|---|---|
| Brand-specific: the pill, the live preview, download card, star ask, one product's site | Generic components only; no logos, no product | Anyone can use it, for anything |
| PRESS orange/riso green, FIELD cream | V2's palette only; the registers are rebuilt in it | Colours from V2, as asked |
| Dark: `#0E130C` / `#192217` / `#E0EDD6` | Deep grounds `#0F120E` / `#161A14`, ink `#E8F0DE`, grey `#A9B59E` | Less olive, calmer big areas, 15:1 text |
| A dark band = forest `#1E2618` + sage text | A dark band = `data-theme="dark"` on forest-950 | Muddy at band size; one source of truth |
| `cursor` `#688A54` for small green text | Removed; focus is forest/sage | 3.72:1 was too low for small text; V2 didn't need it |
| Faint 62% everywhere | Light 62%, dark 56% (5.5:1) | Each measured on its own ground |
| No word limits | §2 budgets per element and medium | Outputs were too wordy |
| Web, app, document, film | Plus tools in depth, slides, SVG motion, data viz, stills | It's all interface |
| No spacing rule beyond a scale | The spacing ladder (§5), ≥ 1.5× per step | Lists sat too close together |
| Radius per surface by prose | `data-medium` switches geometry in CSS | Same markup everywhere |

---

## 14. Files

```
v4/
  DESIGN_SYSTEM.md        this file (in the skill: references/design-system.md)
  tokens/tokens.css       palette, roles (light + dark), space, radius, motion; data-medium switches
  tokens/tokens.json      the same, machine-readable (DTCG)
  kit/kit.css             fonts, base, every component in §7
  assets/fonts/           Space Grotesk, JetBrains Mono, Instrument Serif — static TTF, all OFL
  examples/               a finished starting point per medium (HTML + one SVG)
  scripts/                render.sh (PNG) · pdf.sh · render-motion.cjs (MP4) · standalone.py · contrast.py
  skill/                  SKILL.md + build.sh → dist/field-notes.zip (the shareable Claude skill)
  renders/ gallery.html   what the examples look like (render-all.sh rebuilds them)
```
