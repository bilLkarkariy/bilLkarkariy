#!/usr/bin/env python3
"""Build a self-contained, offline-friendly HTML document. No dependencies."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    template = (ROOT / 'src/template.html').read_text(encoding='utf-8')
    css = (ROOT / 'src/style.css').read_text(encoding='utf-8')
    js = (ROOT / 'src/app.js').read_text(encoding='utf-8')
    if '</script' in js.lower() or '</style' in css.lower():
        raise ValueError('Unsafe inline closing tag in a source file.')
    result = template.replace('/*__CSS__*/', css).replace('/*__JS__*/', js)
    target = ROOT / 'docs/index.html'
    target.parent.mkdir(exist_ok=True)
    target.write_text(result, encoding='utf-8')
    (ROOT / 'docs/.nojekyll').touch()
    print(f'Built {target.name}: {len(result.encode("utf-8")):,} bytes')

if __name__ == '__main__':
    main()
