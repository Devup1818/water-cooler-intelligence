#!/usr/bin/env python3
"""Check the pairs that matter, straight from tokens.css. Run it after any re-skin.

  contrast.py [path/to/tokens.css]

It reads the palette hexes from :root (forest-950, forest, sage, sage-bright, sage-dim,
paper, card, ink-paper, grey-paper, amber, deep-0/1/2, ink-dark, grey-dark) and the
faint opacities, then prints each pair's WCAG ratio against what it is used for.
Exit code 1 if anything fails.
"""
import re, sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'tokens' / 'tokens.css'
css = path.read_text()
DARK = ':root[data-theme="dark"]'
root, dark = (css.split(DARK, 1) + [''])[:2]
P = dict(re.findall(r'--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})', root))

def faint(block, default):
    m = re.search(r'--faint:\s*color-mix\(in srgb, var\(--[a-z-]+\) (\d+)%', block)
    return int(m.group(1)) / 100 if m else default
FAINT_L = faint(root, .62)
FAINT_D = faint(dark, .56)

rgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
lum = lambda c: .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2])
mix = lambda fg, bg, a: [f * a + b * (1 - a) for f, b in zip(rgb(fg), rgb(bg))]
def ratio(fg, bg, a=1.0):
    x, y = lum(mix(fg, bg, a)), lum(rgb(bg))
    return (max(x, y) + .05) / (min(x, y) + .05)

TEXT, LARGE, FILL = 4.5, 3.0, None
pairs = [
    ('ink on paper',            'ink-paper', 'paper', 1, 12.0),
    ('grey on paper',           'grey-paper', 'paper', 1, TEXT),
    (f'faint {FAINT_L:.0%} on paper', 'ink-paper', 'paper', FAINT_L, TEXT),
    ('accent text on solid',    'sage', 'forest', 1, TEXT),
    ('solid text on accent',    'forest', 'sage', 1, TEXT),
    ('focus ring on paper',     'forest', 'paper', 1, LARGE),
    ('amber marker on paper',   'amber', 'paper', 1, LARGE),
    ('ink on dark panel',       'ink-dark', 'deep-1', 1, 12.0),
    ('grey on dark panel',      'grey-dark', 'deep-1', 1, TEXT),
    (f'faint {FAINT_D:.0%} on dark panel', 'ink-dark', 'deep-1', FAINT_D, TEXT),
    ('rung-1 text on dark',     'forest-950', 'sage-bright', 1, TEXT),
    ('focus ring on dark',      'sage', 'deep-0', 1, LARGE),
    ('amber marker on dark',    'amber', 'deep-0', 1, LARGE),
    ('sage on paper (info)',    'sage', 'paper', 1, FILL),
]
bad = 0
print(f'{path}\n')
for name, fg, bg, a, need in pairs:
    if fg not in P or bg not in P:
        print(f'  ?     {name:32s} missing token'); continue
    r = ratio(P[fg], P[bg], a)
    ok = need is None or r >= need
    bad += not ok
    note = 'fill only — never text' if need is None else f'needs {need}:1'
    print(f'  {"ok " if ok else "LOW"}  {name:32s} {r:5.2f}:1   {note}')
sys.exit(1 if bad else 0)
