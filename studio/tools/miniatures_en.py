"""Miniatures EN, adaptation de titres_v3.py sans modifier les images FR.

python3 tools/miniatures_en.py
Les images brutes et les sorties restent hors git.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
FONT = '/System/Library/Fonts/Avenir Next Condensed.ttc'
CREAM, INK = (250, 243, 228), (28, 26, 23)


def heavy(size):
    for i in range(12):
        try:
            f = ImageFont.truetype(FONT, size, index=i)
        except OSError:
            break
        if f.getname()[1] == 'Heavy':
            return f
    raise SystemExit('Avenir Next Condensed Heavy introuvable')


JOBS = [
    (1, ['YOU WOULD', 'HAVE', 'PRESSED IT.'], CREAM, 52, 165, [102, 102, 116], 550),
    (2, ['15 MIN.', 'ALONE.'], INK, 64, 60, [150, 150], 570),
    (3, ['RATHER THE', 'SHOCK?'], CREAM, 52, 150, [118, 145], 600),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / '../../billkarkariy/studio/out/package/miniatures/brouillons')
    parser.add_argument('--out', type=Path, default=ROOT / 'out/package_en/miniatures')
    args = parser.parse_args()
    if not args.out.resolve().is_relative_to((ROOT / 'out').resolve()):
        raise SystemExit('Les miniatures doivent rester dans studio/out/.')
    args.out.mkdir(parents=True, exist_ok=True)
    for n, lines, col, x, y, sizes, max_width in JOBS:
        im = Image.open(args.source / f'v3_brut_{n}.png').convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
        shadow = Image.new('L', im.size, 0)
        text = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(text)
        yy = y
        for line, size in zip(lines, sizes):
            font = heavy(size)
            while dt.textbbox((0, 0), line, font=font)[2] > max_width:
                size -= 1
                font = heavy(size)
            bbox = dt.textbbox((x, yy), line, font=font)
            assert 0 <= bbox[0] < bbox[2] <= 1280 and 0 <= bbox[1] < bbox[3] <= 720
            ds.text((x + 4, yy + 6), line, font=font, fill=200 if col == CREAM else 70)
            dt.text((x, yy), line, font=font, fill=col)
            yy += int(size * .98)
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        im = Image.composite(Image.new('RGB', im.size, (0, 0, 0)), im, shadow)
        im.paste(text, (0, 0), text)
        out = args.out / f'v01_en_{n}.png'
        im.save(out, optimize=True)
        print(out)


if __name__ == '__main__':
    main()
