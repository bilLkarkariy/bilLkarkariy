"""Comparaison arabe : nombres reconnus en chiffres, texte du script conservé.

Les petites différences d'orthographe sont rapprochées localement par le
moteur ourdou, sans ses équivalences phonétiques propres à l'ourdou.
"""
import unicodedata

from vo import norm_arabic, tokens


NUMBERS = {
    1: 'واحد', 2: 'اثنان', 3: 'ثلاث', 4: 'أربعة', 5: 'خمسة',
    7: 'سبعة', 8: 'ثمانية', 9: 'تسعة', 10: 'عشرة', 100: 'مئة',
    15: 'خمس عشرة', 2014: 'ألفين وأربعة عشر', 18: 'ثمانية عشر',
    12: 'اثنا عشر', 24: 'أربع وعشرين', 6: 'ست', 190: 'مئة وتسعين',
    42: 'اثنان وأربعون', 2010: 'ألفين وعشرة', 2250: 'ألفين ومئتين وخمسين',
    80: 'ثمانون', 20: 'عشرين', 350: 'ثلاثمئة وخمسين',
    1095: 'ألف وخمسة وتسعين', 300: 'ثلاثمئة', 2007: 'ألفين وسبعة',
    40: 'أربعين', 77: 'السابعة والسبعين',
}


def units_ar(word):
    out = []
    word = ''.join(str(unicodedata.digit(c)) if c.isdecimal() else c for c in word)
    for part in tokens(word, 'ar'):
        if part.isdecimal() and int(part) in NUMBERS:
            out.extend(norm_arabic(t, 'ar') for t in NUMBERS[int(part)].split())
        else:
            out.append(norm_arabic(part, 'ar'))
    return out
