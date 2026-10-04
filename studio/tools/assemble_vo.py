"""Rythme une prise continue sur les pauses du script, sans TTS ni normalisation.

HF_HUB_OFFLINE=1 .venv/bin/python tools/assemble_vo.py script/v01_en.json public/vo/v01_en_brut.wav public/vo/v01_en.wav

Les coupes sont limitées aux intervalles entre segments, sous -60 dBFS.
Chaque intérieur est copié sans retouche, sauf le gain local ourdou documenté.
Le manifeste garde les échantillons source et destination et les empreintes.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from vo_alignment_en import align_words, digest, transcribe


def quiet_runs(audio, sr, start, end, threshold=-60):
    hop = round(.005 * sr)
    a, b = max(0, round(start*sr)), min(len(audio), round(end*sr))
    n = (b-a)//hop
    if n <= 0:
        return []
    rms = np.sqrt(np.mean(audio[a:a+n*hop].reshape(n,hop)**2, axis=1))
    quiet = rms < 10**(threshold/20)
    edges = np.diff(np.r_[False,quiet,False].astype(int))
    return [(int(a+i*hop),int(a+j*hop)) for i,j in zip(np.where(edges==1)[0],np.where(edges==-1)[0]) if (j-i)*hop >= .04*sr]


def assemble(script, source, dest, work, verse_hold=0, lang='en'):
    sc = json.loads(script.read_text())
    if sc.get('language', 'en') != lang:
        raise ValueError('La langue du script doit correspondre à --lang.')
    info = sf.info(source)
    if info.channels != 1:
        raise ValueError('Cette version attend une prise mono.')
    if source.resolve() == dest.resolve():
        raise ValueError('La prise brute ne doit jamais être écrasée.')
    audio, sr = sf.read(source, dtype='float64')
    work.mkdir(parents=True,exist_ok=True)
    heard = transcribe(source,work/'brut.whisper.json',lang=lang)
    # Une reprise Whisper isolée, documentée et liée à la même source, peut
    # corriger une omission de la reconnaissance continue sans forcer le texte.
    review_path=script.with_suffix('.audio-review.json')
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    if review:
        assert review['source_sha256']==digest(source), 'Contrôles liés à une autre prise'
    for c in review.get('retranscribe',[]):
        words=transcribe(source,work/f'{c["id"]}.clip.whisper.json',[[c['start'],c['end']]],lang=lang,gain_db=c.get('analysis_gain_db',0))
        heard=[w for w in heard if not c['start'] <= (w['start']+w['end'])/2 < c['end']]+words
        heard.sort(key=lambda w:(w['start'],w['end']))
    corrections = work/'brut.retranscriptions.json'
    if corrections.exists() and not review:
        data = json.loads(corrections.read_text())
        assert data['sha256'] == digest(source)
        for c in data['clips']:
            heard = [w for w in heard if not c['start'] <= (w['start']+w['end'])/2 < c['end']] + c['words']
        heard.sort(key=lambda w:(w['start'],w['end']))
    aligned,audit = align_words(sc,heard,lang=lang)
    for fix in review.get('word_times',[]):
        seg=next(s for s in aligned if s['id']==fix['segment'])
        word=[w for w in seg['words'] if w['w']==fix['word']][fix['nth']]
        word.update(start=fix['start'],end=fix['end'])
        seg.update(start=seg['words'][0]['start'],end=seg['words'][-1]['end'])
    (work/'brut.aligned.json').write_text(json.dumps({'segments':aligned,'audit':audit},ensure_ascii=False,indent=2)+'\n')
    starts, ends = [0], []
    boundaries = []
    pad = round(.01*sr)
    for left,right in zip(aligned,aligned[1:]):
        # Whisper déborde parfois de 100 ms ; la recherche reste entre les
        # derniers et premiers mots, jamais au milieu d'un segment.
        lo = max(left['words'][-1]['start']+.04,left['end']-.12)
        hi = min(right['words'][0]['end']-.04,right['start']+.12)
        protection=review.get('boundaries',{}).get(left['id'],{})
        lo=max(lo,protection.get('minimum_end',lo))
        hi=min(hi,protection.get('maximum_start',hi))
        threshold=protection.get('threshold_dbfs',-60)
        runs = quiet_runs(audio,sr,lo,hi,threshold)
        expanded = False
        if not runs and not protection:
            # Cas documenté : Whisper inclut toute la respiration dans « The ».
            # Exiger alors 120 ms très faibles entre les deux mots de bord.
            runs = [(a,b) for a,b in quiet_runs(audio,sr,left['words'][-1]['start']+.04,right['words'][0]['end']-.02) if b-a >= .12*sr]
            expanded = True
        if not runs:
            raise ValueError(f'Aucun silence sûr : {left["id"]}/{right["id"]} {lo:.3f}–{hi:.3f}')
        center = (left['end']+right['start'])/2*sr
        a,b = min(runs,key=lambda r:abs((r[0]+r[1])/2-center))
        ends.append(a+pad)
        starts.append(b-pad)
        boundaries.append({'after':left['id'],'quiet_start':a/sr,'quiet_end':b/sr,
                           'expanded_word_window':expanded,
                           'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(audio[a:b]**2))+1e-12))})
    # Conserver la première et dernière attaque, avec une marge dans le silence.
    leading = quiet_runs(audio,sr,0,aligned[0]['start'])
    if leading:
        starts[0] = max(0,leading[-1][1]-pad)
    trailing = quiet_runs(audio,sr,aligned[-1]['end'],len(audio)/sr)
    ends.append(trailing[0][0]+pad if trailing else len(audio))
    chunks = [np.zeros(round(sc['lead']*sr))]
    cursor = len(chunks[0])
    manifest = {'source':str(source),'source_sha256':digest(source),'script_sha256':digest(script),
                'samplerate':sr,'subtype':info.subtype,'format':info.format,'lead':sc['lead'],'tail':sc['tail'],
                'fade_ms':8,'segments':[],'boundaries':boundaries,'inserts':[], 'review':review}
    processed = audio
    if lang == 'ur':
        # Seuls les deux chuchotements déclarés sont remontés, sans normalisation.
        processed = audio.copy()
        manifest.update(language=lang, gains=[])
        for gain in review.get('gains', []):
            a,b=round(gain['start']*sr),round(gain['end']*sr)
            ramp=round(gain['fade_ms']/1000*sr)
            assert 0 <= a < b <= len(audio) and b-a > 2*ramp
            assert 20 <= gain['fade_ms'] <= 50
            assert not any(a < g['source_end'] and b > g['source_start'] for g in manifest['gains'])
            envelope=np.ones(b-a)*gain['db']
            envelope[:ramp]=np.linspace(0,gain['db'],ramp)
            envelope[-ramp:]=np.linspace(gain['db'],0,ramp)
            processed[a:b] *= 10**(envelope/20)
            assert np.max(np.abs(processed[a:b])) < 1, 'Gain saturant interdit'
            manifest['gains'].append({**gain,'source_start':a,'source_end':b,
                'rms_before_dbfs':float(20*np.log10(np.sqrt(np.mean(audio[a:b]**2))+1e-12)),
                'rms_after_dbfs':float(20*np.log10(np.sqrt(np.mean(processed[a:b]**2))+1e-12)),
                'peak_after_dbfs':float(20*np.log10(np.max(np.abs(processed[a:b]))+1e-12))})
    fade_n = round(.008*sr)
    for seg,a,b in zip(sc['segments'],starts,ends):
        assert b>a+fade_n*2
        chunk=processed[a:b].copy()
        chunk[:fade_n] *= np.linspace(0,1,fade_n)
        chunk[-fade_n:] *= np.linspace(1,0,fade_n)
        silence = round(seg['pause']*sr)
        entry={'id':seg['id'],'source_start':a,'source_end':b,'output_start':cursor,'output_end':cursor+len(chunk),
               'pause_samples':silence,'pause':seg['pause'],'interior_sha256':__import__('hashlib').sha256(audio[a+fade_n:b-fade_n].tobytes()).hexdigest()}
        manifest['segments'].append(entry)
        for gain in manifest.get('gains', []):
            if gain['segment'] == seg['id']:
                assert a+fade_n <= gain['source_start'] < gain['source_end'] <= b-fade_n
                gain.update(output_start=cursor+gain['source_start']-a,output_end=cursor+gain['source_end']-a)
        chunks.extend([chunk,np.zeros(silence)])
        cursor += len(chunk)+silence
        if seg['id']=='s63' and verse_hold:
            n=round(verse_hold*sr)
            manifest['inserts'].append({'after':'s63','kind':'silent_verse','start':cursor/sr,'end':(cursor+n)/sr})
            chunks.append(np.zeros(n));cursor+=n
    chunks.append(np.zeros(round(sc['tail']*sr)))
    final=np.concatenate(chunks)
    dest.parent.mkdir(parents=True,exist_ok=True)
    sf.write(dest,final,sr,subtype=info.subtype,format=info.format)
    # Le PCM 24 bits est copié bit pour bit entre les deux fondus.
    actual,_=sf.read(dest)
    for entry in manifest['segments']:
        a,b=entry['source_start'],entry['source_end'];c,d=entry['output_start'],entry['output_end']
        if lang == 'en':
            assert np.array_equal(audio[a+fade_n:b-fade_n],actual[c+fade_n:d-fade_n]),entry['id']
        else:
            # Tolérance d'un seul pas PCM 24 bits dans les zones amplifiées.
            assert np.max(np.abs(processed[a+fade_n:b-fade_n]-actual[c+fade_n:d-fade_n])) <= 2**-23,entry['id']
            mask=np.ones(b-a-2*fade_n,dtype=bool)
            for gain in manifest['gains']:
                if gain['segment'] == entry['id']:
                    mask[gain['source_start']-a-fade_n:gain['source_end']-a-fade_n]=False
            assert np.array_equal(audio[a+fade_n:b-fade_n][mask],actual[c+fade_n:d-fade_n][mask]),entry['id']
        assert not np.any(actual[d:d+entry['pause_samples']]),entry['id']
    manifest.update(output=str(dest),output_sha256=digest(dest),duration=len(final)/sr,samples=len(final))
    # À côté du WAV : vo.py peut contraindre l'alignement aux vraies coupes.
    dest.with_suffix('.assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (work/'assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    detail='intérieurs identiques' if lang == 'en' else 'segments conservés (gain local documenté)'
    print(f'{dest} : {len(final)/sr:.3f} s ; {len(sc["segments"])} {detail} ; pauses vérifiées')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('script',type=Path);p.add_argument('source',type=Path);p.add_argument('dest',type=Path)
    p.add_argument('--lang',choices=['en','ur'],default='en')
    p.add_argument('--work',type=Path)
    p.add_argument('--verse-hold',type=float,default=0,help='Plateau silencieux supplémentaire, après la pause de s63')
    args=p.parse_args()
    assemble(args.script,args.source,args.dest,args.work or Path(f'out/validation/vo-{args.lang}'),args.verse_hold,args.lang)
