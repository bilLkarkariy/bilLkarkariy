"""Unités de comparaison ourdoues ; le texte du script n'est jamais réécrit.

Whisper sépare souvent les noms composés ou écrit les nombres en chiffres.
Ces équivalences ne servent qu'au rapprochement avec le texte enregistré.
"""
import difflib

from vo import norm_arabic, tokens


NUMBERS = {
    15: 'پندرہ', 2014: 'دو ہزار چودہ', 18: 'اٹھارہ', 12: 'بارہ',
    24: 'چوبیس', 6: 'چھ', 190: 'ایک سو نوے', 42: 'بیالیس',
    2010: 'دو ہزار دس', 2250: 'دو ہزار دو سو پچاس', 80: 'اسی',
    20: 'بیس', 350: 'تین سو پچاس', 1095: 'ایک ہزار پچانوے',
    300: 'تین سو', 2007: 'دو ہزار سات', 40: 'چالیس', 77: 'ستتر',
}

# Découpages orthographiques/translittérations constatés dans la reconnaissance.
# La comparaison conserve les lettres ourdoues (norm_arabic) et les mots livrés
# restent strictement ceux du script, y compris les noms religieux.
SPELLINGS = {
    'استغفراللہ': 'استغفر اللہ', 'میڈیامیٹری': 'میڈیا میٹری',
    'university': 'یونیورسٹی', 'of': 'آف', 'virginia': 'ورجینیا', 'phone': 'فون',
}
SPELLINGS = {norm_arabic(k):v for k,v in SPELLINGS.items()}


def units_ur(word):
    parts = tokens(word, 'ur')
    out = []
    for part in parts:
        if part.isdecimal() and int(part) in NUMBERS:
            out.extend(norm_arabic(t) for t in NUMBERS[int(part)].split())
        else:
            normal = norm_arabic(part.lower())
            out.extend(norm_arabic(t) for t in SPELLINGS.get(normal, normal).split())
    return out


def match_replacement(a, b):
    """Rapproche localement les variantes, entre deux ancres exactes.

    Un coût d'édition monotone autorise jusqu'à trois unités accolées (Whisper
    change les espaces). Pas de correspondance faible forcée : sous 0,72 de
    similitude, on laisse un vrai trou pour l'interpolation et son audit.
    Renvoie les tranches d'unités appariées ; aucun changement du texte.
    """
    n,m=len(a),len(b)
    costs={(0,0):0.0}
    prev={}
    for i in range(n+1):
        for j in range(m+1):
            if (i,j) not in costs:
                continue
            moves=[]
            if i<n: moves.append((i+1,j,1,None))
            if j<m: moves.append((i,j+1,1,None))
            for p in range(1,min(3,n-i)+1):
                for q in range(1,min(3,m-j)+1):
                    x,y=''.join(a[i:i+p]),''.join(b[j:j+q])
                    ratio=difflib.SequenceMatcher(None,x,y,autojunk=False).ratio()
                    if ratio >= .72:
                        moves.append((i+p,j+q,(1-ratio)*(p+q)+.08*(p+q-2),(i,i+p,j,j+q,ratio)))
            for ni,nj,cost,match in moves:
                value=costs[i,j]+cost
                if value < costs.get((ni,nj),float('inf')):
                    costs[ni,nj]=value
                    prev[ni,nj]=((i,j),match)
    out=[]
    point=(n,m)
    while point != (0,0):
        point,match=prev[point]
        if match: out.append(match)
    return list(reversed(out))
