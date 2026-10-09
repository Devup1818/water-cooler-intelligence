---
name: field-notes
description: "Field Notes design system for anything visual: app or tool UI, dashboards, websites, PDFs, slides, social cards, film frames, SVG animation, charts. Use it for any design work, even unnamed."
metadata:
  version: "4.0"
---

# Field Notes

A design system for anything with a screen or a page. Paper and forest, one green,
mono labels for data, very few words. It works because it is restrained: one accent,
hierarchy carried by grey instead of size, and the product shown working instead
of described. Tools, websites, PDFs, slides and films all follow the same rules,
because they are the same problem: one person, one rectangle, a few seconds.

**When the project already has a design system or brand, use theirs.** Use Field Notes
when nothing exists, when the person asks for it, or re-skin it with their colours
and fonts (see *Re-skin*).

## What's in this folder

| Path | What it is |
|---|---|
| `references/design-system.md` | The full spec (§0–§14). Read the sections the table below points to. |
| `tokens/tokens.css` | Every colour, space, radius and motion value as CSS variables, light and dark |
| `tokens/tokens.json` | The same, machine-readable (DTCG), for Figma plugins, native apps, Python |
| `kit/kit.css` | Base styles and every component (buttons, chips, tables, windows…) |
| `assets/fonts/` | Space Grotesk, JetBrains Mono, Instrument Serif (all OFL) |
| `examples/` | A finished starting point for each medium (below) |
| `scripts/` | Render to PNG/PDF/MP4, build a single-file HTML, check contrast |

## The rules that matter most

1. **One job per screen.** One primary action, one rung-1 element, one moving idea.
2. **Show it working, then name it.** A redrawn window, a real table or a chart beats a paragraph.
   For marketing pieces with no product to show, find one visual idea in the subject and
   build it from the system's own parts. A podcast called "Off the Record" becomes mono
   transcript lines with redaction bars. The system sets the voice; it doesn't supply the idea.
3. **Write less.** Use the budgets below. If a sentence repeats the figure, heading or label, cut it.
4. **Emphasis ladder.** Rung 1 = solid fill (once per page), rung 2 = accent fill, rung 3 = hairline outline, rung 4 = text.
5. **Rank with grey before size:** ink → grey → faint at the same size. Save size jumps for titles and figures.
6. **Three voices.** Mono for data and labels. Sans for interface and prose. Serif only for one first line, with its second clause in italic ("Plan the shoot. *Ship the cut.*").
7. **One green; amber means attention.** No other hues. Sage is never text on paper (1.5:1).
8. **Square by default.** Tools, print and film are square; on the web, cards and buttons get the radius scale.
9. **Space by the ladder.** Inside an item < between items < between groups < between sections, each step ≥ 1.5×. Lists that touch read as one blob.
10. **Nothing travels; nothing moves its neighbours.** Motion is a change in place. Reserve space for every state.
11. **Ships finished.** The still frame or no-JS page must explain everything.
12. **Every number checkable.** Put the caveat beside it: "48 h — longer past 20 min of footage."

### Word budgets (ceilings)

| Headline | Lede | Card | Button | Label | Toast | Web first screen | Doc page prose | Slide | Film main line |
|---|---|---|---|---|---|---|---|---|---|
| ≤ 8 words | 1 sentence ≤ 20 | ≤ 20 | ≤ 3 | ≤ 3 | ≤ 6 | ≤ 40 total | ≤ 60 | ≤ 15 outside the figure | ≤ 7 (labels and numbers don't count) |

Prefer a mono label (`12 DAYS · BRIEF TO DELIVERY`) over a sentence. Use realistic
short copy, never lorem ipsum. Banned: seamless, effortless, supercharge, unlock,
elevate, game-changer, "excited to announce".

## Workflow

**1. Pick the medium, read its sections, start from its example.**

| Making… | Read in `references/design-system.md` | Start from |
|---|---|---|
| Tool, app, dashboard, admin panel, settings screen | §9.1, §7, §5 | `examples/04-tool.html` (`?dark` for dark) |
| Website, landing page | §9.2, §4, §7 | `examples/06-web.html` |
| PDF: proposal, report, one-pager | §9.3, §6 | `examples/07-document.html` |
| Slide deck | §9.4, §9.8 | `examples/08-slide.html` |
| Film or video frames, reels, title cards | §9.5, §9.7, §10, §5 (platform safe zones) | `examples/09-film.html` |
| SVG animation, motion graphic | §9.6, §8 | `examples/11-motion.svg` |
| Share card, carousel, still | §9.7 | `examples/10-social.html` |
| Chart or data figure | §9.8, §3 (data ramp) | `examples/08-slide.html` |
| Component sheet, style guide | §7, §3, §4 | `examples/01–03-*.html` |

The examples are complete, so reading one is the fastest way to see the system
applied. Copy its structure and replace the content. Don't rebuild from scratch.
Their names and numbers are illustrative. Never carry them into real work, and never
invent data to fill a chart: if only two numbers exist, chart two numbers.

**2. Set up the files.** The examples link `../tokens/tokens.css` and `../kit/kit.css`,
and the kit loads fonts from `../assets/fonts/`. Pick one:
- **Folder output:** copy `tokens/`, `kit/` and `assets/` into the output folder. If the page sits beside them rather than one level down, change its two stylesheet links from `../tokens/…` to `tokens/…`. The kit's own font paths still work.
- **One-file output** (artifacts, email, sharing): build normally, then run
  `python3 scripts/standalone.py page.html out.html`. Add `--embed-fonts` if it must work offline.
- **Framework** (React, Tailwind, Vue, SwiftUI, Flutter): import `tokens.css`, or translate
  `tokens.json` into the framework's theme. Keep the role names (`surface`, `panel`, `ink`,
  `grey`, `faint`, `hairline`, `solid`, `accent`, `tint`, `focus`, `attention`) and never hardcode hex.
  Tailwind: map theme colours to `var(--ink)` etc.

**3. Build with role tokens and kit classes.**
- `data-medium="tool|web|print|slides|film"` on any container sets geometry and density. Tools are 13px and square; the web is 17px with radii.
- `data-theme="dark"` on `<html>` or on any block makes it dark. A dark band on a light page is just a block with `data-theme="dark"` and a `forest-950` background; don't hand-pick colours inside it.
- Don't reuse kit class names (`.card`, `.window`, `.table`…) for custom elements. They bring padding and borders with them.

**4. Write the words last, then cut to budget.**

**5. Render it, look at it, fix it, then show it.** Most real defects are only visible
in the render: a cut-off bottom, an orphaned word, a column pushed off-screen,
text the same colour as its ground.
- `scripts/render.sh page.html out.png <width> <height> [?dark]`. Set the height to the full page height or the bottom gets cut. Output is 2× pixels; use `SCALE=1` for an exact-size deliverable such as a 1080 × 1920 frame.
- `scripts/pdf.sh doc.html out.pdf` writes the PDF plus one PNG per page. The PNGs need PyMuPDF (`pip install pymupdf`).
- `node scripts/render-motion.cjs anim.svg out.mp4 [seconds]` exports animations whose `frame(t)` is a pure function of time. Needs `puppeteer-core` and `ffmpeg`.

Then run the checklist below.

## Re-skin for another brand

The system is structure; the green is a default. To use someone's brand:
1. Change only the palette block at the top of `tokens/tokens.css`. Keep the slots:
   - a dark neutral tinted toward their accent (`forest-950`, `forest`)
   - one light accent with brighter and dimmer steps (`sage`, `sage-bright`, `sage-dim`)
   - paper and card
   - ink and grey for text
   - one attention hue (`amber`)
   - dark grounds (`deep-0…2`) that are their dark neutral pulled toward grey, never their accent at full size
2. Run `python3 scripts/contrast.py`. Every line must say `ok`.
3. Swap fonts by role in `kit/kit.css` and `tokens.css`: one sans, one mono, and one display face used for a single line.
4. Their logo goes in the rail or bar brand slot, or the cover meta card. The system ships with no logos.

## Other outputs

- **PDF via Python:** PyMuPDF with `assets/fonts/*.ttf` (static instances), values from `tokens.json`, all measurements in points. Keep content in one data block and derive totals and percentages from it (spec §9.3).
- **Native apps:** map the roles to the platform's colour assets, radius 0, the tool density, and the spacing ladder.
- **Frame-based video** (HyperFrames, Remotion): every frame a pure function of time, seeded randomness, bundled fonts, frame 0 already moving (spec §8).
- **Figma:** import `tokens/tokens.json` with a tokens plugin.

## Before showing work

- [ ] One job, one rung-1 element, one tinted band, one light.
- [ ] Words within budget; nothing restates its figure; no filler.
- [ ] Lists breathe; groups are clearly apart (spacing ladder).
- [ ] Only green and amber. Sage never text on paper. Contrast passes.
- [ ] Every state designed, space reserved, nothing travels.
- [ ] Rendered and looked at: nothing cut off, overflowing or orphaned.
