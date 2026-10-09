# Field Notes — a design system as a Claude skill

Paper and forest, one green, mono labels, very few words. Use it for app and tool UI,
websites, PDFs, slides, social cards, film frames, SVG animation and charts.

## Install

**Claude (claude.ai or the desktop app):** Customize → Skills → Add, then upload
`field-notes.zip`. Code execution must be on in your settings.

**Claude Code, just you:** unzip into `~/.claude/skills/` so you have
`~/.claude/skills/field-notes/SKILL.md`. Claude Code finds it on its own.

**Claude Code, a whole team:** put the folder in a repo at `.claude/skills/field-notes/`
and commit it. Everyone who opens the repo gets it.

**Other AI tools or people:** everything here is plain files. Point the tool at
`references/design-system.md` (in AGENTS.md, a Cursor rule or a system prompt) and use
`tokens/` and `kit/`. Designers can import `tokens/tokens.json` with a Figma tokens plugin.

## Use

Ask for the thing, for example "a settings screen for my app" or "a one-page PDF of
these results". To use your own brand, say so: "use field-notes with our colours
#0B3D91 / #F2C14E and the font Inter". Claude swaps the palette and checks contrast
with `scripts/contrast.py`.

## What's inside

```
SKILL.md                     how Claude uses it (short)
references/design-system.md  the full spec
tokens/  kit/                CSS variables (light + dark) and components
assets/fonts/                Space Grotesk, JetBrains Mono, Instrument Serif (OFL)
examples/                    a finished starting point per medium
scripts/                     render to PNG / PDF / MP4, single-file HTML, contrast check
```

Rendering scripts need Google Chrome. The MP4 export also needs ffmpeg and
`npm i puppeteer-core`. PDF page previews use `pip install pymupdf`.
