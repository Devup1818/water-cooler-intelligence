#!/usr/bin/env python3
"""Turn a page built on the kit into one self-contained HTML file.

Inlines tokens.css and kit.css in place of their <link> tags. Fonts come from
Google Fonts by default (small file, needs a network). Use --embed-fonts to base64
the bundled fonts instead (works offline, ~1 MB bigger).

  standalone.py <page.html> <out.html> [--embed-fonts]
"""
import base64, re, sys
from pathlib import Path

GOOGLE = ("@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
          "&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        sys.exit(__doc__)
    src, out = Path(args[0]).resolve(), Path(args[1])
    embed = '--embed-fonts' in sys.argv
    html = src.read_text()

    def inline(match):
        href = match.group(1)
        css_path = (src.parent / href).resolve()
        css = css_path.read_text()
        if css_path.name == 'kit.css':
            faces = re.findall(r'@font-face\s*{[^}]*}', css)
            if embed:
                def embed_face(face):
                    url = re.search(r'url\("([^"]+)"\)', face).group(1)
                    font = (css_path.parent / url).resolve()
                    mime = 'font/woff2' if font.suffix == '.woff2' else 'font/ttf'
                    data = base64.b64encode(font.read_bytes()).decode()
                    return re.sub(r'url\("[^"]+"\)', f'url(data:{mime};base64,{data})', face)
                for f in faces:
                    css = css.replace(f, embed_face(f))
            else:
                for f in faces:
                    css = css.replace(f, '')
                css = GOOGLE + '\n' + css
        return f'<style>\n{css}\n</style>'

    def inline_tag(m):
        href = re.search(r'href=["\']([^"\']+\.css)["\']', m.group(0))
        if not href or href.group(1).startswith(('http:', 'https:', '//')):
            return m.group(0)  # remote stylesheets stay links
        return inline(href)
    html, n = re.subn(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', inline_tag, html)
    out.write_text(html)
    print(f'{out}  ({n} stylesheets inlined, fonts: {"embedded" if embed else "Google Fonts"})')

if __name__ == '__main__':
    main()
