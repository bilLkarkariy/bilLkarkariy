"""Alignement EN auditable avec le même Whisper small que vo.py, sans TTS.

On rapproche les mots du script de ceux reconnus ; une interpolation reste
explicitement signalée. Les traits d'union et nombres n'ajoutent pas de mots
au script. Aucun rognage par énergie : il détruirait les chuchotements.
"""
import difflib
import hashlib
import json
import re
from pathlib import Path

from vo import norm, spoken, tokens


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integer_en(n):
    units = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
    tens = 'zero ten twenty thirty forty fifty sixty seventy eighty ninety'.split()
    if n < 20:
        return units[n]
    if n < 100:
        return tens[n // 10] + (' ' + units[n % 10] if n % 10 else '')
    if n < 1000:
        return units[n // 100] + ' hundred' + (' and ' + integer_en(n % 100) if n % 100 else '')
    if n < 1000000:
        return integer_en(n // 1000) + ' thousand' + (' ' + ('and ' if n % 1000 < 100 else '') + integer_en(n % 1000) if n % 1000 else '')
    raise ValueError(f'Nombre hors plage : {n}')


def units(word):
    if word == '%':
        return ['percent']
    if norm(word)=='untutored':
        return ['untutored']
    percent=word.endswith('%')
    if norm(word) == '17th':
        return ['seventeenth']
    # Les dates sont écrites dans le script selon leur prononciation enregistrée.
    if re.fullmatch(r'[\d,]+[.!?:;%]?', word):
        n = int(re.sub(r'\D', '', word))
        word = {2014: 'twenty fourteen', 2010: 'twenty ten', 1095: 'ten ninety five'}.get(n) or integer_en(n)
    aliases = {'practice': 'practise', 'center': 'centre', 'chalwa':'khalwa',
               'mediammetry':'mediametrie','mohammed':'mohamed','fawzi':'faouzi'}
    return [aliases.get(norm(t), norm(t)) for t in word.replace('-', ' ').split() if norm(t)] + (['percent'] if percent else [])


def transcribe(path, cache, windows=None):
    from faster_whisper import WhisperModel
    windows = [list(pair) for pair in windows] if windows else None
    fingerprint = digest(path)
    cache = Path(cache)
    if cache.exists():
        data = json.loads(cache.read_text())
        if data.get('sha256') == fingerprint and data.get('windows') == windows:
            return data['words']
    model = WhisperModel('small', device='cpu', compute_type='int8', local_files_only=True)
    options = {'clip_timestamps': [t for pair in windows for t in pair], 'condition_on_previous_text': False} if windows else {}
    segs, _ = model.transcribe(str(path), language='en', word_timestamps=True, **options)
    words = []
    for s in segs:
        words.extend({'word': w.word.strip(), 'start': w.start, 'end': w.end,
                      'probability': w.probability} for w in s.words)
        print(f'Whisper : {s.end:.2f} s', flush=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({'engine': 'faster-whisper/small/cpu/int8', 'sha256': fingerprint, 'windows':windows, 'words': words}, ensure_ascii=False, indent=2) + '\n')
    return words


def align_words(sc, heard, bounds=None):
    """Interpole chaque série manquante une seule fois, entre ses deux voisins.

    bounds peut limiter chaque segment à sa copie exacte dans le WAV assemblé.
    L'audit distingue reconnaissance, substitution et timing interpolé.
    """
    refs = [(s['id'], t) for s in sc['segments'] for t in tokens(s['text'])]
    a = [(i, u) for i, (_, t) in enumerate(refs) for u in units(t)]
    merged = []
    for w in heard:
        if merged and re.fullmatch(r',\d+',w['word']) and re.fullmatch(r'\d+',merged[-1]['word']):
            merged[-1] = {**merged[-1], 'word':merged[-1]['word']+w['word'], 'end':w['end']}
        elif merged and w['word'][:1] in "'’-" and len(w['word']) > 1:
            merged[-1] = {**merged[-1], 'word': merged[-1]['word'] + w['word'], 'end': w['end']}
        else:
            merged.append(dict(w))
    b = []
    for j, w in enumerate(merged):
        us = units(w['word'])
        for k, u in enumerate(us):
            b.append((j, u, w['start'] + (w['end']-w['start'])*k/len(us),
                      w['start'] + (w['end']-w['start'])*(k+1)/len(us)))
    slots = [[] for _ in refs]
    for tag, i0, i1, j0, j1 in difflib.SequenceMatcher(None, [x[1] for x in a], [x[1] for x in b], autojunk=False).get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i0, i1), range(j0, j1)):
                slots[a[i][0]].append((b[j][2], b[j][3], merged[b[j][0]]['word']))
    times = [(min(v[0] for v in x), max(v[1] for v in x)) if x else None for x in slots]
    audit = []
    offset = 0
    out = []
    for seg in sc['segments']:
        count = len(tokens(seg['text']))
        lo, hi = offset, offset + count
        limits = bounds[seg['id']] if bounds else (0, max(w['end'] for w in heard))
        for i in range(lo, hi):
            if times[i]:
                times[i] = (max(limits[0], times[i][0]), min(limits[1], times[i][1]))
                if times[i][1] <= times[i][0]:
                    times[i] = None
        i = lo
        while i < hi:
            if times[i] is not None:
                i += 1
                continue
            j = i + 1
            while j < hi and times[j] is None:
                j += 1
            prev = times[i-1][1] if i else limits[0]
            nxt = next((times[k][0] for k in range(j, len(times)) if times[k]), limits[1])
            prev, nxt = max(limits[0], prev), min(limits[1], nxt)
            # Si Whisper colle les voisins, redistribuer une petite portion du
            # mot voisin ; ne jamais inventer une durée nulle ou un chevauchement.
            if nxt - prev < .03 * (j-i):
                need = .04 * (j-i)
                if i > lo and times[i-1][1] - times[i-1][0] > need + .02:
                    prev -= need
                    times[i-1] = (times[i-1][0], prev)
                elif j < hi and times[j][1] - times[j][0] > need + .02:
                    nxt += need
                    times[j] = (nxt, times[j][1])
                else:
                    raise ValueError(f'Pas de durée pour {seg["id"]} : {refs[i:j]}')
            weights = [max(1, len(norm(refs[k][1]))) for k in range(i,j)]
            cursor = prev
            for k, weight in zip(range(i,j), weights):
                end = cursor + (nxt-prev)*weight/sum(weights)
                times[k] = (cursor, end)
                audit.append({'segment': seg['id'], 'index': k-lo, 'word': refs[k][1],
                              'start': round(cursor,3), 'end': round(end,3), 'status':'interpolated'})
                cursor = end
            i = j
        words = []
        for i in range(lo,hi):
            start, end = times[i]
            # Les timestamps Whisper nuls (articles, élisions) sont répartis
            # avec le mot suivant, sans changer la durée du segment.
            if end <= start:
                next_time = times[i+1] if i+1 < hi else None
                if next_time and next_time[1] > start+.04:
                    end = min(start+.04, (start+next_time[1])/2)
                    times[i+1] = (max(end,next_time[0]),next_time[1])
                elif words and start-words[-1]['start'] > .06:
                    words[-1]['end'] = round(start-.03,3)
                    start, end = start-.03, start
                else:
                    raise ValueError(f'Timestamp nul : {seg["id"]} {refs[i][1]}')
                audit.append({'segment':seg['id'],'index':i-lo,'word':refs[i][1], 'status':'zero_redistributed'})
            words.append({'w':refs[i][1], 'start':round(start,3),'end':round(end,3)})
        out.append({'id':seg['id'],'text':spoken(seg['text']),'start':words[0]['start'],'end':words[-1]['end'],'words':words})
        offset = hi
    return out, audit


def align_recording(script_path, audio_path):
    import soundfile as sf
    script_path, audio_path = Path(script_path), Path(audio_path)
    root=Path(__file__).resolve().parent.parent
    sc=json.loads(script_path.read_text())
    info=sf.info(audio_path)
    manifest_path=audio_path.with_suffix('.assembly.json')
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    bounds=None
    if manifest:
        assert manifest['output_sha256']==digest(audio_path), 'Manifeste audio périmé'
        assert manifest['script_sha256']==digest(script_path), 'Manifeste script périmé'
        bounds={s['id']:(s['output_start']/info.samplerate,s['output_end']/info.samplerate) for s in manifest['segments']}
    work=root/'out/validation/vo-en'
    heard=transcribe(audio_path,work/'final.whisper.json',list(bounds.values()) if bounds else None)
    segments,audit=align_words(sc,heard,bounds)
    if manifest:
        for fix in manifest.get('review',{}).get('word_times',[]):
            s=next(s for s in segments if s['id']==fix['segment'])
            clip=next(c for c in manifest['segments'] if c['id']==s['id'])
            shift=(clip['output_start']-clip['source_start'])/info.samplerate
            w=[w for w in s['words'] if w['w']==fix['word']][fix['nth']]
            w.update(start=round(fix['start']+shift,3),end=round(fix['end']+shift,3))
            s.update(start=s['words'][0]['start'],end=s['words'][-1]['end'])
            audit.append({**fix,'start':w['start'],'end':w['end'],'status':'reviewed_signal_envelope'})
    out={'audio':audio_path.resolve().relative_to((root/'public').resolve()).as_posix(),
         'language':'en','segments':segments,'duration':round(info.duration,3),
         'alignment':{'engine':'faster-whisper/small/cpu/int8','interpolated':audit},
         'silences':manifest['inserts'] if manifest else []}
    dst=root/'src/data'/script_path.name.replace('.json','.vo.json')
    dst.write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n')
    (work/'alignment-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(f'Alignement -> {dst} : {len(segments)} segments, {len(audit)} timings à contrôler')
