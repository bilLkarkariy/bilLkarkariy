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

# Lettres homophones en ourdou : seulement dans les petits blocs non reconnus,
# jamais pour fabriquer des ancres globales. Le rapprochement reste audité.
HOMOPHONES = str.maketrans({'ذ':'ز','ظ':'ز','ض':'ز','ث':'س','ص':'س','ط':'ت','ح':'ہ'})


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


def match_replacement(a, b, phonetic=False):
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
                    if phonetic:
                        ratio=max(ratio,difflib.SequenceMatcher(None,x.translate(HOMOPHONES),y.translate(HOMOPHONES),autojunk=False).ratio())
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


def align_assembled(sc, heard, manifest, work, samplerate):
    """Choisit par segment la reconnaissance la plus complète, sans forcer de mot.

    La prise source et sa copie ont les mêmes échantillons de parole : leurs
    timings sont transférables par la translation exacte du manifeste. Cette
    seconde observation récupère les omissions propres aux clips Whisper.
    Chaque choix et chaque mot non reconnu restent dans l'audit.
    """
    from vo_alignment_en import align_words, digest, transcribe
    source=manifest['source']
    assert digest(source)==manifest['source_sha256'], 'Prise source différente du manifeste'
    raw=transcribe(source,work/'brut.whisper.json',lang='ur')
    for clip in manifest.get('review',{}).get('retranscribe',[]):
        words=transcribe(source,work/f'{clip["id"]}.clip.whisper.json',[[clip['start'],clip['end']]],
                         lang='ur',gain_db=clip.get('analysis_gain_db',0))
        raw=[w for w in raw if not clip['start'] <= (w['start']+w['end'])/2 < clip['end']]+words
    raw.sort(key=lambda w:(w['start'],w['end']))
    out,audit,choices=[],[],[]
    for ref,clip in zip(sc['segments'],manifest['segments']):
        assert ref['id']==clip['id']
        a,b,c,d=[clip[k]/samplerate for k in ('source_start','source_end','output_start','output_end')]
        candidates=[]
        errors=[]
        for origin,words,lo,hi,shift in [('assembled',heard,c,d,0),('source',raw,a,b,c-a)]:
            local=[w for w in words if w['end']>lo and w['start']<hi]
            try:
                # Les variantes homophones sont permises une fois les coupes
                # connues, dans un seul segment ; jamais pour décider une coupe.
                segs,checks=align_words({'segments':[ref]},local,{ref['id']:(lo,hi)},lang='ur',phonetic=True)
                seg=segs[0]
                for w in seg['words']:
                    w.update(start=round(w['start']+shift,3),end=round(w['end']+shift,3))
                ws=seg['words']
                assert all(w['end']>w['start'] for w in ws)
                assert all(x['end']<=y['start'] for x,y in zip(ws,ws[1:]))
                seg.update(start=ws[0]['start'],end=ws[-1]['end'])
                for item in checks:
                    for key in ('start','end'):
                        if key in item: item[key]=round(item[key]+shift,3)
                    item['recognition']=origin
                score=tuple(sum(x['status']==status for x in checks)
                            for status in ('interpolated','recognized_split','substituted'))
                candidates.append((score,seg,checks,origin))
            except (ValueError, AssertionError) as error:
                errors.append(f'{origin}: {error}')
        if not candidates:
            raise ValueError(f'{ref["id"]} : aucun alignement monotone : {errors}')
        # En cas d'égalité, garder l'observation du WAV final.
        score,seg,checks,origin=min(candidates,key=lambda x:x[0])
        out.append(seg);audit.extend(checks)
        choices.append({'segment':ref['id'],'recognition':origin,'uncertainty_counts':list(score),
                        **({'rejected':errors} if errors else {})})
    return out,audit,choices
