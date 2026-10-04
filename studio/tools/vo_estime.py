"""Alignement provisoire, hors ligne et sans audio (anglais, ourdou, arabe).

python3 tools/vo_estime.py script/v01_en.json
python3 tools/vo_estime.py script/v01_ur.json --verse-hold 6
Durées = 0,09 s par mot + 0,18 s par syllabe estimée, plus ponctuation
(écriture arabe : 0,06 s par mot + 0,15 s par syllabe, mots courts et débit plus serré, environ 4,5 syllabes/s).
Pauses entre segments, lead et tail repris exactement du script (mêmes valeurs que le français).
Les mots gardent les IDs s1…s79, comme le futur tools/vo.py align.

Écriture arabe (ourdou, arabe) : les voyelles brèves ne s'écrivent pas. Une syllabe par voyelle longue écrite
(ا آ و ی ے ي ى ئ ۓ, sauf و/ی en tête de mot, consonnes), plus une par paire de consonnes restantes ;
ھ (aspiration) et ں (nasale) ne comptent pas. Un mot = une suite de lettres, signes et chiffres
(les voyelles brèves et le tanwīn restent collés au mot : « تقریباً », « ردِعمل »).
--verse-hold : le plateau silencieux du verset après s63, comme tools/assemble_vo.py --verse-hold.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r"\[[^\]]*\]")
TOKEN = re.compile(r"[\w'’-]+")
EXCEPTIONS = {"people": 2, "every": 2, "fire": 1, "our": 1, "hours": 1,
              "science": 2, "quietly": 3, "diary": 3, "different": 3,
              "khalwa": 2, "dhikr": 1, "karkariya": 4, "astaghfirullah": 5,
              "alghazali": 4, "mohamed": 3, "faouzi": 2, "alkarkari": 4}
ARABIC_SCRIPT = {'ur', 'ar'}
LONG = set('اآویےيىئۓ')
SILENT = set('ھں')
SENTENCE_END = '.!?…۔؟'
CLAUSE = ',;:،؛'


def syllables(word):
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


def syllables_arabic(word):
    """Syllabes approchées d'un mot en écriture arabe : voyelles longues écrites + consonnes restantes / 2,5."""
    letters = [c for c in unicodedata.normalize('NFC', word) if unicodedata.category(c).startswith('L')]
    vowels = consonants = 0
    for i, c in enumerate(letters):
        if c in SILENT:
            continue
        if c in LONG and not (i == 0 and c in 'وی'):
            # « او », « ای » en tête de mot : une seule voyelle (aur, ek)
            if i == 1 and letters[0] in 'اآ' and c in 'وی':
                continue
            vowels += 1
        else:
            consonants += 1
    return max(1, vowels + round(max(0, consonants - vowels) / 2.5))


def tokens(text, lang):
    """Mots du texte (balises retirées), avec la ponctuation qui suit chacun."""
    if lang not in ARABIC_SCRIPT:
        matches = list(TOKEN.finditer(text))
        spans = [(m.start(), m.end()) for m in matches]
    else:
        spans, start = [], None
        for i, c in enumerate(text + ' '):
            inside = unicodedata.category(c)[0] in 'LMN'
            if inside and start is None:
                start = i
            elif not inside and start is not None:
                spans.append((start, i))
                start = None
    out = []
    for k, (a, b) in enumerate(spans):
        punct = text[b:spans[k + 1][0] if k + 1 < len(spans) else len(text)]
        out.append((text[a:b], punct))
    return out


def estimate(script, verse_hold=0.0):
    lang = script.get('language', 'en')
    count = syllables_arabic if lang in ARABIC_SCRIPT else syllables
    per_word, per_syllable = (.06, .15) if lang in ARABIC_SCRIPT else (.09, .18)
    time = float(script['lead'])
    segments = []
    silences = []
    for s in script['segments']:
        text = re.sub(r"\s+", " ", TAG.sub('', s['text'])).strip()
        words = []
        for w, punct in tokens(text, lang):
            end = time + per_word + per_syllable * count(w)
            words.append({'w': w, 'start': round(time, 3), 'end': round(end, 3)})
            time = end + (.18 if any(c in SENTENCE_END for c in punct) else .08 if any(c in CLAUSE for c in punct) else .025)
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
        if s['id'] == 's63' and verse_hold:
            silences.append({'after': 's63', 'kind': 'silent_verse', 'start': round(time, 3), 'end': round(time + verse_hold, 3)})
            time += verse_hold
    return {'audio': None, 'duration': round(time + script['tail'], 3),
            'estimated': True, 'language': lang,
            '_doc': 'PROVISOIRE : syllabes estimées, pauses du script conservées. Aucun son généré. Remplacer avec tools/vo.py align.',
            **({'silences': silences} if silences else {}),
            'segments': segments}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--verse-hold', type=float, default=0, help='Plateau silencieux après s63 (secondes)')
    args = parser.parse_args()
    script = json.loads(args.script.read_text())
    output = args.out or ROOT / 'src/data' / (args.script.stem + '.vo.json')
    result = estimate(script, args.verse_hold)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"{output}: {len(result['segments'])} segments, {result['duration']:.2f} s — PROVISOIRE, sans audio")


if __name__ == '__main__':
    main()
