"""Contrôles numériques de la voix AR (sans réseau, TTS ni écoute humaine).

HF_HUB_OFFLINE=1 .venv/bin/python tools/check_vo_ar.py
Vérifie la copie PCM hors fondus, toutes les pauses, sans gain,
le texte complet et l'ordre des mots ; écrit les extraits de contrôle locaux.
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from vo import tokens
from vo_alignment_en import digest


def main():
    root = Path(__file__).resolve().parent.parent
    raw, final = [root/f'public/vo/v01_ar{suffix}.wav' for suffix in ('_brut', '')]
    manifest = json.loads((root/'src/data/v01_ar.assembly.json').read_text())
    assert manifest == json.loads(final.with_suffix('.assembly.json').read_text())
    sc = json.loads((root/'script/v01_ar.json').read_text())
    vo = json.loads((root/'src/data/v01_ar.vo.json').read_text())
    source, sr = sf.read(raw)
    audio, fs = sf.read(final)
    assert digest(raw) == manifest['source_sha256']
    assert digest(final) == manifest['output_sha256']
    assert digest(root/'script/v01_ar.json') == manifest['script_sha256']
    assert sf.info(raw).subtype == sf.info(final).subtype == 'PCM_24'
    assert sf.info(raw).format == sf.info(final).format == 'WAVEX'
    assert sr == fs == 48000 and source.ndim == audio.ndim == 1
    assert len(sc['segments']) == len(vo['segments']) == len(manifest['segments']) == 79
    assert vo['audio'] == 'vo/v01_ar.wav' and vo['language'] == 'ar'
    assert abs(vo['duration'] - len(audio)/sr) <= .0005
    assert manifest['inserts'] == vo['silences'] == []
    assert not np.any(audio[:round(sc['lead']*sr)])
    assert not np.any(audio[-round(sc['tail']*sr):])
    fade = round(manifest['fade_ms']/1000*sr)
    assert 5 <= manifest['fade_ms'] <= 10
    cursor = round(sc['lead']*sr)
    previous = 0
    gaps = []
    for ref, seg, clip in zip(sc['segments'], vo['segments'], manifest['segments']):
        assert ref['id'] == seg['id'] == clip['id']
        assert [w['w'] for w in seg['words']] == tokens(ref['text'], 'ar')
        a,b,c,d = [clip[k] for k in ('source_start','source_end','output_start','output_end')]
        assert b-a == d-c and c == cursor
        mask = np.ones(b-a-2*fade, dtype=bool)
        for g in manifest['gains']:
            if g['segment'] == seg['id']:
                mask[g['source_start']-a-fade:g['source_end']-a-fade] = False
        assert np.array_equal(source[a+fade:b-fade][mask], audio[c+fade:d-fade][mask]), seg['id']
        assert clip['pause_samples'] == round(ref['pause']*sr)
        assert not np.any(audio[d:d+clip['pause_samples']])
        cursor = d+clip['pause_samples']
        for i,w in enumerate(seg['words']):
            assert previous <= w['start'] < w['end'], (seg['id'], w, previous)
            assert c/sr-.001 <= w['start'] < w['end'] <= d/sr+.001, (seg['id'],w)
            if i and w['start']-previous > 1.2:
                gaps.append({'segment':seg['id'],'before':w['w'],'gap':round(w['start']-previous,3)})
            previous = w['end']
    assert cursor+round(sc['tail']*sr) == len(audio)
    assert len(manifest['boundaries']) == 78
    for b in manifest['boundaries']:
        x = source[round(b['quiet_start']*sr):round(b['quiet_end']*sr)]
        assert abs(20*np.log10(np.sqrt(np.mean(x*x))+1e-12)-b['rms_dbfs']) < .001
        threshold=manifest['review'].get('boundaries',{}).get(b['after'],{}).get('threshold_dbfs',-60)
        assert b['rms_dbfs'] < threshold
    assert manifest['gains'] == []
    assert not gaps, gaps
    work = root/'out/validation/vo-ar'
    clip = next(s for s in manifest['segments'] if s['id']=='s69')
    shift = clip['output_start']-clip['source_start']
    for name,x in [('brut',source[round(553*sr):round(558.5*sr)]),
                   ('final',audio[round(553*sr)+shift:round(558.5*sr)+shift])]:
        sf.write(work/f'chuchotements-{name}.wav',x,sr,subtype='PCM_24')
    audit=vo['alignment']['interpolated']
    report={'source_sha256':digest(raw),'output_sha256':digest(final),'duration':len(audio)/sr,
            'segments_identical_between_fades':79,'pauses_verified':79,
            'word_count':sum(len(s['words']) for s in vo['segments']),
            'interpolated_words':sum(w['status']=='interpolated' for w in audit),
            'gains':manifest['gains'],'internal_gaps_over_1_2s':gaps,
            'human_listening_performed':False}
    (work/'audio-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
