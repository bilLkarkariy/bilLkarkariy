"""Miniatures en écriture de droite à gauche (ourdou, arabe), sur les mêmes images que le français et l'anglais.

/usr/bin/python3 tools/miniatures_rtl.py ur
Il faut un Pillow avec raqm (mise en forme des lettres liées) : celui du système en a un, pas celui du .venv.
Les images brutes et les sorties restent hors git.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

ROOT = Path(__file__).resolve().parent.parent
CREAM, INK = (250, 243, 228), (28, 26, 23)

# (fichier de police, index dans la collection), interligne
FONTS = {
    'ur': ('/System/Library/Fonts/NotoNastaliq.ttc', 2, 1.45),  # Noto Nastaliq Urdu Bold
    'ar': ('/System/Library/Fonts/GeezaPro.ttc', 1, 1.15),      # Geeza Pro Bold
}
# n, lignes, couleur, bord droit du bloc, haut, tailles, largeur maximale
JOBS = {
    'ur': [
        (1, ['آپ بھی', 'دبا دیتے۔'], CREAM, 602, 150, [118, 118], 550),
        (2, ['پندرہ منٹ۔', 'اکیلے۔'], INK, 634, 40, [132, 132], 570),
        (3, ['جھٹکا ہی', 'بہتر؟'], CREAM, 652, 140, [118, 130], 600),
    ],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lang', choices=sorted(JOBS))
    parser.add_argument('--source', type=Path, default=ROOT / '../../billkarkariy/studio/out/miniatures_brouillons')
    args = parser.parse_args()
    if not features.check('raqm'):
        raise SystemExit('Pillow sans raqm : les lettres ne seraient pas liées. Lance /usr/bin/python3.')
    out_dir = ROOT / f'out/package_{args.lang}/miniatures'
    out_dir.mkdir(parents=True, exist_ok=True)
    path, index, lead = FONTS[args.lang]
    font = lambda size: ImageFont.truetype(path, size, index=index, layout_engine=ImageFont.Layout.RAQM)
    kw = {'direction': 'rtl', 'language': args.lang}
    for n, lines, col, right, y, sizes, max_width in JOBS[args.lang]:
        im = Image.open(args.source / f'v3_brut_{n}.png').convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
        shadow = Image.new('L', im.size, 0)
        text = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(text)
        yy = y
        for line, size in zip(lines, sizes):
            f = font(size)
            while dt.textlength(line, font=f, **kw) > max_width:
                size -= 2
                f = font(size)
            x = right - dt.textlength(line, font=f, **kw)  # aligné à droite du bloc
            bbox = dt.textbbox((x, yy), line, font=f, **kw)
            assert 0 <= bbox[0] < bbox[2] <= 1280 and 0 <= bbox[1] < bbox[3] <= 720, (line, bbox)
            ds.text((x + 4, yy + 6), line, font=f, fill=200 if col == CREAM else 70, **kw)
            dt.text((x, yy), line, font=f, fill=col, **kw)
            yy += int(size * lead)
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        im = Image.composite(Image.new('RGB', im.size, (0, 0, 0)), im, shadow)
        im.paste(text, (0, 0), text)
        out = out_dir / f'v01_{args.lang}_{n}.png'
        im.save(out, optimize=True)
        print(out)


if __name__ == '__main__':
    main()
