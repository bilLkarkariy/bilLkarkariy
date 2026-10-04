"""Alignement provisoire (anglais, arabe), hors ligne et sans audio.

python3 tools/vo_estime.py script/v01_en.json
python3 tools/vo_estime.py script/v01_ar.json
Durées = 0,09 s par mot + 0,18 s par syllabe estimée, plus ponctuation.
Pauses entre segments, lead et tail repris exactement du script français.
Les mots gardent les IDs s1…s79, comme le futur tools/vo.py align.

Arabe : le texte n'est pas vocalisé, on ne peut pas compter les voyelles brèves. Une syllabe arabe est
presque toujours consonne + voyelle (+ consonne) : on compte une syllabe pour deux lettres, au moins une
par voyelle longue (ا و ي ى آ). Les signes (harakat, shadda, tanwin) font partie du mot mais ne comptent pas.
"""
import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r"\[[^\]]*\]")
# Les harakat (U+064B…U+065F, U+0670) ne sont pas des lettres pour \w : sans elles, « وزرٌّ » serait coupé en deux.
TOKEN = re.compile(r"[\wؐ-ًؚ-ٰٟۖ-ۭ'’-]+")
AR_LETTER = re.compile(r"[ء-غف-يٱ]")
AR_LONG = re.compile(r"[اآويى]")
EXCEPTIONS = {"people": 2, "every": 2, "fire": 1, "our": 1, "hours": 1,
              "science": 2, "quietly": 3, "diary": 3, "different": 3,
              "khalwa": 2, "dhikr": 1, "karkariya": 4, "astaghfirullah": 5,
              "alghazali": 4, "mohamed": 3, "faouzi": 2, "alkarkari": 4}


def syllables_ar(word):
    letters = len(AR_LETTER.findall(word))
    return max(1, math.ceil(letters / 2), len(AR_LONG.findall(word[1:])))


def syllables(word):
    if AR_LETTER.search(word):
        return syllables_ar(word)
    parts = word.split('-')
    if len(parts) > 1:
        return sum(syllables(p) for p in parts)
    word = re.sub(r"[^a-z]", "", word.lower())
    if word in EXCEPTIONS:
        return EXCEPTIONS[word]
    n = len(re.findall(r"[aeiouy]+", word))
    if len(word) > 3 and word.endswith('e') and not re.search(r"[^aeiou]le$", word):
        n -= 1
    if word.endswith('ed') and not word.endswith(('ted', 'ded')):
        n -= 1
    return max(1, n)


def estimate(script):
    time = float(script['lead'])
    segments = []
    for s in script['segments']:
        text = re.sub(r"\s+", " ", TAG.sub('', s['text'])).strip()
        matches = list(TOKEN.finditer(text))
        words = []
        for i, match in enumerate(matches):
            w = match.group()
            end = time + .09 + .18 * syllables(w)
            words.append({'w': w, 'start': round(time, 3), 'end': round(end, 3)})
            punct = text[match.end():matches[i+1].start() if i+1 < len(matches) else len(text)]
            time = end + (.18 if re.search(r'[.!?…؟]', punct) else .08 if re.search(r'[,;:،؛]', punct) else .025)
        if not words:
            raise ValueError(f"Segment vide : {s['id']}")
        # Réserve silencieuse, pas une traduction religieuse choisie implicitement.
        reserved = 0
        if s.get('_pending'):
            reserved = 3.5
            time += reserved
        segments.append({'id': s['id'], 'text': text, 'start': words[0]['start'],
                         'end': words[-1]['end'], 'words': words,
                         **({'reserved_after': reserved} if reserved else {})})
        time += float(s['pause'])
    language = script.get('language', 'en')
    return {'audio': None, 'duration': round(time + script['tail'], 3),
            'estimated': True, 'language': language,
            '_doc': 'PROVISOIRE : syllabes estimées, pauses FR conservées. Aucun son généré. Remplacer avec tools/vo.py align.',
            'segments': segments}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    script = json.loads(args.script.read_text())
    output = args.out or ROOT / 'src/data' / (args.script.stem + '.vo.json')
    result = estimate(script)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"{output}: {len(result['segments'])} segments, {result['duration']:.2f} s — PROVISOIRE, sans audio")


if __name__ == '__main__':
    main()
