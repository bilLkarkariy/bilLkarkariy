"""Contrôle reproductible de la copie audio, des pauses et des mots EN.

HF_HUB_OFFLINE=1 .venv/bin/python tools/check_vo_en.py
Ce contrôle numérique ne remplace pas une écoute humaine.
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from vo import tokens
from vo_alignment_en import digest


def main():
    root=Path(__file__).resolve().parent.parent
    raw=root/'public/vo/v01_en_brut.wav'; final=root/'public/vo/v01_en.wav'
    manifest=json.loads(final.with_suffix('.assembly.json').read_text())
    script=json.loads((root/'script/v01_en.json').read_text())
    vo=json.loads((root/'src/data/v01_en.vo.json').read_text())
    source,sr=sf.read(raw); audio,fs=sf.read(final)
    assert digest(raw)==manifest['source_sha256']==manifest['review']['source_sha256']
    assert digest(final)==manifest['output_sha256']
    assert digest(root/'script/v01_en.json')==manifest['script_sha256']
    assert sf.info(raw).subtype==sf.info(final).subtype=='PCM_24'
    assert sf.info(raw).format==sf.info(final).format=='WAVEX'
    assert sr==fs==48000 and source.ndim==audio.ndim==1
    assert len(script['segments'])==len(vo['segments'])==len(manifest['segments'])==79
    assert abs(vo['duration']-len(audio)/sr)<=.0005
    assert vo['audio']=='vo/v01_en.wav'
    fade=round(manifest['fade_ms']/1000*sr)
    assert not np.any(audio[:round(script['lead']*sr)])
    assert not np.any(audio[-round(script['tail']*sr):])
    previous=0;gaps=[]
    for ref,seg,clip in zip(script['segments'],vo['segments'],manifest['segments']):
        assert ref['id']==seg['id']==clip['id']
        assert [w['w'] for w in seg['words']]==tokens(ref['text'])
        a,b,c,d=clip['source_start'],clip['source_end'],clip['output_start'],clip['output_end']
        assert b-a==d-c
        assert np.array_equal(source[a+fade:b-fade],audio[c+fade:d-fade]),seg['id']
        assert clip['pause_samples']==round(ref['pause']*sr)
        assert not np.any(audio[d:d+clip['pause_samples']]),seg['id']
        for i,w in enumerate(seg['words']):
            assert previous<=w['start']<w['end'],(seg['id'],w,previous)
            assert c/sr-.001<=w['start']<w['end']<=d/sr+.001,(seg['id'],w)
            if i and w['start']-previous>1.2:gaps.append({'segment':seg['id'],'before':w['w'],'gap':round(w['start']-previous,3)})
            previous=w['end']
    whispers=[]
    for fix in manifest['review']['word_times']:
        seg=next(s for s in manifest['segments'] if s['id']==fix['segment'])
        offset=seg['output_start']-seg['source_start']
        a,b=round(fix['start']*sr),round(fix['end']*sr)
        assert a>=seg['source_start']+fade and b<=seg['source_end']-fade
        assert np.array_equal(source[a:b],audio[a+offset:b+offset])
        whispers.append({'raw':[fix['start'],fix['end']],'final':[(a+offset)/sr,(b+offset)/sr],
                         'duration':(b-a)/sr,'identical':True,
                         'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(source[a:b]**2))))})
    for s in manifest['inserts']:
        assert not np.any(audio[round(s['start']*sr):round(s['end']*sr)])
    # Extraits locaux pour le contrôle à l'oreille ; la brute reste intacte.
    work=root/'out/validation/vo-en'
    for name,a,b in [('dhikr',404,408),('chuchotements',512.5,516.9),('pascal',230,241)]:
        sf.write(work/f'{name}-brut.wav',source[round(a*sr):round(b*sr)],sr,subtype='PCM_24')
    s=next(s for s in manifest['segments'] if s['id']=='s69');offset=s['output_start']-s['source_start']
    sf.write(work/'chuchotements-final.wav',audio[round(512.5*sr)+offset:round(516.5*sr)+offset],sr,subtype='PCM_24')
    report={'source_sha256':digest(raw),'output_sha256':digest(final),'duration':len(audio)/sr,
            'segments_identical_between_fades':79,'pauses_verified':79,'word_count':sum(len(s['words']) for s in vo['segments']),
            'whispers':whispers,'verse_insert_zero_samples':True,'internal_gaps_over_1_2s':gaps,
            'human_listening_performed':False,'alignment_review':vo['alignment']['interpolated']}
    (work/'audio-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
