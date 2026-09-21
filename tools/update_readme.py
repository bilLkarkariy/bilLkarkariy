#!/usr/bin/env python3
"""Insert or refresh only the marked Lab block, preserving the existing profile."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- agent-lab:start -->'
END = '<!-- agent-lab:end -->'

def main() -> None:
    for name in ('docs/index.html', 'assets/agent-lab-preview.webp', 'assets/agent-lab-preview.png'):
        if not (ROOT / name).is_file():
            raise FileNotFoundError(f'Build the site and previews before updating README: {name}')
    path = ROOT / 'README.md'
    readme = path.read_text(encoding='utf-8')
    snippet = (ROOT / 'profile-block.md').read_text(encoding='utf-8').strip()
    if START in readme or END in readme:
        if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) >= readme.index(END):
            raise ValueError('Invalid or duplicate Agent Lab markers; refusing to change the profile.')
        updated = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda _: snippet, readme, flags=re.S)
    elif '\n---\n' in readme:
        offset = readme.index('\n---\n')
        updated = readme[:offset] + '\n' + snippet + '\n' + readme[offset:]
    else:
        updated = readme.rstrip() + '\n\n' + snippet + '\n'
    path.write_text(updated, encoding='utf-8')
    print('README updated; existing profile content preserved.')

if __name__ == '__main__':
    main()
