"""Recalcule chapitres, finition et liste d'images sur la vraie voix arabe.

Après check_v01_ar.mjs et srt.py. Méthode reprise du paquet ourdou.
HF_HUB_OFFLINE=1 .venv/bin/python tools/update_v01_ar_docs.py
"""
import json
import math
import re
from pathlib import Path

from remap3d import cues
from vo import norm, tokens


def main():
    at, vo = cues('ar')
    assert vo['audio'] == 'vo/v01_ar.wav' and not vo.get('estimated')
    seg = {s['id']: s for s in vo['segments']}
    report = json.loads(Path('out/validation-ar/v01-ar-report.json').read_text())
    assert report['audioSource'] == vo['audio'] and not report['estimated']

    def frame(t):
        return 24 + math.floor(t * 30 + .5)

    def tc(t):
        ms = round(t * 1000)
        return f'{ms // 60000:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}'

    def interval(sid, phrase=None, nth=0):
        s = seg[sid]
        if phrase is None:
            return s['start'], s['end']
        ws = s['words']
        parts = [norm(t) for t in tokens(phrase, 'ar')]
        hits = [i for i in range(len(ws)) if [norm(w['w']) for w in ws[i:i+len(parts)]] == parts]
        assert len(hits) > nth, (sid, phrase, nth)
        i = hits[nth]
        return ws[i]['start'], ws[i+len(parts)-1]['end']

    def row(label, sid, phrase=None, nth=0):
        a, b = interval(sid, phrase, nth)
        return f'| {label} | `{sid}` | {a:.3f} → {b:.3f} | {tc(a+.8)} → {tc(b+.8)} | {frame(a)} → {frame(b)} |'

    head = ['| Repère | Segment | Voix (s) | Temps vidéo | Images vidéo |', '|---|---|---:|---:|---:|']
    windows = [
        ('Film muet', frame(interval('s31', 'أن تفكر وحدك')[0])-9, at('p21')-4, '« أن تفكر وحدك » − 9 images → p21 − 4'),
        ('Nuit au crayon', at('p32')-6, at('p33')-6, 'p32 − 6 → p33 − 6'),
        ('Khalwa VHS', at('p41')-4, at('p42')-4, 'p41 − 4 → p42 − 4'),
        ('Exercice 1', at('p54')-6, at('p57')-6, 'p54 − 6 → p57 − 6'),
        ('Exercice 2', at('p59')-6, at('p61')-6, 'p59 − 6 → p61 − 6'),
        ('Veste, fenêtre 6', at('p53')-6, at('p53', 'Et')-4, 'aroll6 → fondIn, src/montage/p4.tsx'),
    ]
    sfx = [[0, 30]] + [[a, b] for _, a, b, _ in windows[:5]]
    lines = ['# V01 AR — repères de finition', '',
        'Calculés sur `src/data/v01_ar.vo.json` et `public/vo/v01_ar.wav`, à 30 i/s. Temps voix du WAV **assemblé**, pas de la brute. Vidéo = voix + **0,8 s** ; image = `24 + Math.round(voix × 30)`. Fins de fenêtres exclusives. Les fins de mots sont arrondies à l’image la plus proche.', '',
        'Référence des six remplacements : `../../billkarkariy-en/studio/docs/v01-finition.md`. Méthode reprise de la finition ourdoue : chaque fenêtre suit les mots arabes et les transitions du montage. Aucun insert rendu ou posé ici.', '',
        '## Intro Pixar', '',
        'Garder la voix arabe seule jusqu’au fondu, puis recaler les bruitages propres à l’intro. Couper la source française avant le crédit « Wilson et al. », visible vers 13,7 s.', '', *head]
    for sid, phrase in [('s1', 'خمس عشرة دقيقة'), ('s2', 'وحدك'), ('s3', 'لا هاتف'),
                        ('s4', 'أنت وأفكارك'), ('s5', 'وزرٌّ'), ('s5', 'بشحنة كهربائية'),
                        ('s6', 'ضغط عليه رجلان من كل ثلاثة')]:
        lines.append(row(phrase, sid, phrase))
    lines += ['', '## Six fenêtres à remplacer', '',
        '| Passage | Voix (s, fenêtre complète) | Temps vidéo | Images [début, fin[ | Calcul |',
        '|---|---:|---:|---:|---|']
    for label, a, b, rule in windows:
        assert a < b
        lines.append(f'| {label} | {a/30-.8:.3f} → {b/30-.8:.3f} | {tc(a/30)} → {tc(b/30)} | **{a} → {b}** | {rule} |')
    lines += ['', 'La fenêtre film commence 9 images avant « أن تفكر وحدك » ; les autres suivent les transitions du montage. Les tableaux suivants donnent les bornes de parole, sans les marges.', '']
    sections = [
        ('Film muet', [('Début : أن تفكر وحدك', 's31', 'أن تفكر وحدك'), ('Décrochage : وما إن يتعب', 's31', 'وما إن يتعب'), ('Fin', 's31', 'حتى يتشتت الفيلم في كل اتجاه')]),
        ('Nuit au crayon', [('Passage entier', 's43', None), ('تستيقظ', 's43', 'تستيقظ'), ('أول ردّ فعل', 's43', 'أول ردّ فعل'), ('الشاشة', 's43', 'الشاشة')]),
        ('Khalwa VHS', [('Passage entier', 's52', None), ('كلمة تعني', 's52', 'كلمة تعني'), ('الانفراد', 's52', 'الانفراد')]),
        ('Exercice 1', [('Invitation, début', 's65', None), ('أربعين', 's65', 'أربعين'), ('دقيقتين', 's65', 'دقيقتين'), ('واحد', 's66', 'واحد'), ('اثنان', 's67', 'اثنان'), ('Fin : يكفي كرسي', 's67', 'يكفي كرسي')]),
        ('Exercice 2', [('Étape 5, début', 's70', None), ('خمسة', 's70', 'خمسة'), ('Suite et fin', 's71', None), ('أربعين ثانية', 's71', 'أربعين ثانية'), ('فقط لأعرف الساعة', 's71', 'فقط لأعرف الساعة')]),
        ('Veste, fenêtre 6', [('Début de p53', 's64', 'الطريق الذي أسلكه اسمه الطريقة الكركرية'), ('Veste', 's64', 'وهذه المرقّعة هي لباسها'), ('Sortie vers les fondements', 's64', 'ومن بين الأسس التي يصفها الشيخ')]),
    ]
    for title, items in sections:
        lines += [f'### {title}', '', *head]
        lines.extend(row(*item) for item in items)
        lines.append('')
    lines += ['## Bruitages à couper', '',
        'Les cinq passages animés, plus `[0, 30]`. La veste reste hors de cette liste. Bornes en images de la vidéo longue.', '',
        '```json', json.dumps({'sfxOff': sfx}, separators=(',', ':')), '```', '',
        'Propriétés de rendu pour la finition sans visage :', '', '```json',
        json.dumps({'clean': True, 'no3d': False, 'faceless': True, 'sfxOff': sfx}, separators=(',', ':')), '```', '',
        '## Verset et chuchotements', '', *head,
        row('Introduction et verset récité', 's63'),
        row('Premier أستغفرُ الله chuchoté', 's69', 'أستغفرُ الله', 1),
        row('Second أستغفرُ الله chuchoté', 's69', 'أستغفرُ الله', 2), '',
        f'Verset affiché sur les images **{report["verse"][0]} → {report["verse"][1]}** : dès `at("p52") - 10`, récitation comprise, puis environ une seconde. Uthmani exact, Amiri Quran, fondu seul, rien dessous. Voix audible, musique et bruitages coupés. Aucun silence ajouté (`--verse-hold 0`).', '',
        'Chuchotements sans gain, échantillons d’origine conservés. Les vérifications numériques et Whisper ne remplacent pas l’écoute humaine du mix final.', '']
    Path('docs/v01-ar-finition.md').write_text('\n'.join(lines))

    duration = report['durationInFrames']/30
    p = Path('docs/v01-ar-description.md')
    text = p.read_text()
    start = text.index('\n\n') + 2
    end = text.index('\nTitre proposé')
    intro = f'Voix enregistrée assemblée et alignée (`vo/v01_ar.wav`). Chapitres calculés sur `src/data/v01_ar.vo.json` : début du groupe + 0,8 s, arrondi à la seconde inférieure. Durée de `V01-AR` : **{tc(duration)}** ({report["durationInFrames"]} images à 30 i/s). Les points éditoriaux restants sont dans `v01-ar-questions.md`.\n'
    text = text[:start] + intro + text[end:]
    groups = json.loads(Path('src/data/v01_ar.groups.json').read_text())
    chapters = iter(['p7', 'p18', 'p28', 'p34', 'p41', 'p50', 'p54', 'p62'])

    def chapter(match):
        t = math.floor(seg[groups[next(chapters)][0]]['start']+.8)
        return f'{t//60:02d}:{t%60:02d} {match[2]}'

    text = re.sub(r'^(?!00:00)(\d\d:\d\d) (.+)$', chapter, text, flags=re.M)
    text = re.sub(r'- Chapitres :.*?(?=\n- Titres)', '- Chapitres : p7, p18, p28, p34, p41, p50, p54, p62, comme l’anglais. Temps du vrai alignement + 0,8 s, arrondis à la seconde inférieure.', text, flags=re.S)
    count = len(re.findall(r'^\d+$', Path('docs/v01-ar.srt').read_text(), re.M))
    text = re.sub(r'- Sous-titres :.*', f'- Sous-titres : `python3 tools/srt.py src/data/v01_ar.vo.json docs/v01-ar.srt` ({count} entrées sur la vraie voix, temps vidéo, chiffres occidentaux et marque RTL).\n', text, flags=re.S)
    p.write_text(text)

    pairs = report['stills']
    faceless = [p for p in pairs if re.search(r'^page_|^p1_debut$|^revelation$|^meublee$|^retours$|^consigne$|^ecran_final$', p['name'])]
    lines = ['# V01 AR — images fixes sur le vrai alignement', '',
        f'Liste recalculée sur `src/data/v01_ar.vo.json` et `vo/v01_ar.wav` : **{report["durationInFrames"]} images**, 30 i/s, **{tc(duration)}**. Vidéo = voix + 0,8 s.', '',
        'Le contrôle HTML/styles et audio simulé est décrit dans `v01-ar-etat.md`. Les PNG et le rendu complet restent à inspecter ; cette liste ne constitue pas une preuve d’inspection visuelle.', '',
        f'## Vidéo longue : {len(pairs)} vues (+ {len(faceless)} sans visage)', '',
        '| Vue | Image | Temps vidéo |', '|---|---:|---:|']
    lines.extend(f'| {p["name"]} | {p["frame"]} | {tc(p["frame"]/30)} |' for p in pairs)
    lines += ['', 'Version sans visage : ' + ', '.join(p['name'] for p in faceless) + '.', '',
        '## Shorts : 9 vues', '', '| Short | Durée (images) | Vues |', '|---|---:|---|']
    for name, n in report['shortDurations'].items():
        lines.append(f'| {name} | {n} | debut:60 milieu:{math.floor(n/2+.5)} fin:{n-30} |')
    lines += ['', '## Commandes pour Claude', '', 'Réemploi des images 3D françaises, aucun Blender.', '',
        '```bash', 'node tools/bundle_local.mjs out/bundle-ar',
        "export CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'", 'export BUNDLE=out/bundle-ar']
    for folder, selected in [('ar-png', pairs), ('ar-sans-visage-png', faceless)]:
        lines.append(f'FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/{folder} --composition V01-AR ' + ' '.join(f'{p["name"]}:{p["frame"]}' for p in selected))
    for name, n in report['shortDurations'].items():
        lines.append(f'FACELESS=1 CLEAN=1 WITH3D=1 node tools/stills.mjs out/validation-ar/{name}-png --composition {name} debut:60 milieu:{math.floor(n/2+.5)} fin:{n-30}')
    lines += ['```', '', '## Points à regarder', '',
        '- Arabe en Amiri : droite à gauche, chiffres dans l’ordre, petites étiquettes lisibles, interlignes, fiches empilées et colonne de l’exercice sans débordement.',
        '- Verset : uthmani exact, Amiri Quran, fondu seul, rien dessous ; voix seule pendant toute sa fenêtre.',
        '- Plans 3D : vide, khalwa, dhikr, meublee ; raccords de vitesse et continuité des images françaises remappées.',
        '- Repères d’intro, inserts, veste et bruitages : `v01-ar-finition.md`.',
        '- La comparaison FR/EN `--baseline out/validation/ar-baseline/src` vérifie HTML, styles et audio simulé ; elle ne remplace pas une écoute ni le contrôle du rendu vidéo.', '']
    Path('docs/v01-ar-images-fixes.md').write_text('\n'.join(lines))
    print('Description, finition et images fixes recalculées.')


if __name__ == '__main__':
    main()
