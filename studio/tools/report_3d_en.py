"""Prépare les plages et repères 3D d'une langue (EN par défaut) sans importer ni lancer Blender.

HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py [--lang en|ur]
Sorties : out/validation/3d-<langue>-cues.json, out/validation/3d-<langue>-plan.json (lu par tools/remap3d_en.py)
et docs/v01-<langue>-3d.md. Les commandes de rendu éventuelles sortent vers out/3d-<langue>, jamais dans les assets FR.
"""
import argparse
import ast
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
# Repères exclusivement utilisés par Blender, en plus des repères Remotion (src/data/v01_<langue>.anchors.json).
EXTRA={
  'en':{
    'p10':{'remettre|0':'another shock'},
    'p18':{'bouton|0':'button'},
    'p35':{'cherches|0':'looking','entres|0':'walk in','porte|0':'door',
           'quoi|0':'What do you do','tournes|0':'Walk around'},
    'p36':{'pièce|0':'that room'},
    'p44':{'retire|0':'withdraw'},
    'p51':{'part|0':{'phrase':'wanders','nth':0},'repart|0':{'phrase':'wanders','nth':1}},
  },
  # Ourdou : le verbe vient en fin de phrase. Quand deux mots français s'inversent, le premier garde le premier mot
  # ourdou de la tournure, pour que l'image ne recule jamais (« دروازہ ڈھونڈنے » = « cherches la porte »).
  'ur':{
    'p10':{'remettre|0':'دوبارہ'},
    'p18':{'bouton|0':'بٹن'},
    'p35':{'cherches|0':'دروازہ','entres|0':'اندر','porte|0':'ڈھونڈنے',
           'quoi|0':'کیا کرتے','tournes|0':'چکر'},
    'p36':{'pièce|0':'کمرہ'},
    'p44':{'retire|0':'انسان'},
    'p51':{'part|0':{'phrase':'بھٹکتا','nth':0},'repart|0':{'phrase':'بھٹکتا','nth':1}},
  },
}
ARABIC_SCRIPT={'ur','ar'}
LANG='en'


def all_anchors(lang=None):
    lang=lang or LANG
    result=json.loads((ROOT/f'src/data/v01_{lang}.anchors.json').read_text())
    for pid,items in EXTRA[lang].items():result.setdefault(pid,{}).update(items)
    return result


def norm(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()))


def norm_arabic(s):
    """Même règle que src/cues.ts : sans signes (voyelles brèves, hamza suscrite), lettres et chiffres seulement."""
    s=unicodedata.normalize('NFD',s)
    return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')


def cues(lang, source=None):
    vo=json.loads((source or ROOT/f'src/data/{"v01" if lang=="fr" else "v01_"+lang}.vo.json').read_text())
    segments={s['id']:s for s in vo['segments']}
    groups=json.loads((ROOT/f'src/data/v01_{LANG}.groups.json').read_text())
    anchors=all_anchors()
    nrm=norm_arabic if lang in ARABIC_SCRIPT else norm
    def at(pid,w=None,edge='start',nth=0):
        if pid in segments:
            parts=[segments[pid]]
        else:
            parts=[segments[s] for s in groups[pid]]
        if w is None:
            t=parts[0]['start'] if edge=='start' else parts[-1]['end']
        else:
            words=[w for s in parts for w in s['words']]
            target=anchors[pid][f'{w}|{nth}'] if lang!='fr' else w
            phrase=target if isinstance(target,str) else target['phrase']
            occurrence=(0 if isinstance(target,str) else target['nth']) if lang!='fr' else nth
            ns=[nrm(t) for t in phrase.split()]
            hits=[i for i in range(len(words)) if [nrm(x['w']) for x in words[i:i+len(ns)]]==ns]
            index=hits[occurrence]
            t=words[index if edge=='start' else index+len(ns)-1][edge]
        return 24+math.floor(t*30+.5)
    return at


def specs(at, lang='en'):
    # Mêmes expressions que les séquences Remotion et tools/plans3d.py.
    return {
        'maquette':(at('p1','Seul')-3,at('p2')-10,2),
        'seuls':(at('p10')-4,at('p11')-4+2,2),
        'bouton':(at('p18')-4,at('p19')-1+2,2),
        'salon':(at('p16','chez')-3,at('p16','Un')-4+2,2),
        'vide':(at('p35')-4,at('p36',None,'end')+24,2),
        'khalwa':(at('p44')-6,at('p44',None,'end')+24,2),
        'dhikr':(at('p51',"L'idée")-6,at('p52')-10 if lang=='ur' else at('p51',None,'end')+30,2),
        'meublee':(at('p67','meublé')-10,at('p68')+30,3),
    }


def main():
    global LANG
    parser=argparse.ArgumentParser()
    parser.add_argument('--lang',default='en',choices=sorted(EXTRA))
    LANG=parser.parse_args().lang
    L=LANG.upper()
    en,fr=cues(LANG),cues('fr')
    estimated=ROOT/f'out/validation/vo-{LANG}/v01_{LANG}.estime.json'
    old=specs(cues(LANG,estimated),LANG) if estimated.exists() else None
    out=ROOT/'out/validation';out.mkdir(parents=True,exist_ok=True)
    anchors=all_anchors()
    groups=json.loads((ROOT/f'src/data/v01_{LANG}.groups.json').read_text())
    voice=json.loads((ROOT/f'src/data/v01_{LANG}.vo.json').read_text())
    real='voix estimée (en attente de la vraie voix)' if voice.get('estimated') else 'voix réelle'
    table={}
    for pid in groups:
        for edge in ('start','end'):
            table[f'{pid}||{edge}|0']=en(pid,None,edge)
        for key in anchors.get(pid,{}):
            w,nth=key.rsplit('|',1)
            for edge in ('start','end'):
                table[f'{pid}|{w}|{edge}|{nth}']=en(pid,w,edge,int(nth))
    (out/f'3d-{LANG}-cues.json').write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n')
    tree=ast.parse((ROOT/'tools/plans3d.py').read_text())
    word_calls={}
    for node in ast.walk(tree):
        if not isinstance(node,ast.If) or not isinstance(node.test,ast.Compare):continue
        if not isinstance(node.test.left,ast.Name) or node.test.left.id!='SHOT':continue
        shot=ast.literal_eval(node.test.comparators[0]);calls=set()
        for statement in node.body:
            for call in ast.walk(statement):
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id in ('at','F'):
                    try: args=tuple(ast.literal_eval(a) for a in call.args)
                    except ValueError:continue
                    if len(args)>1 and args[1] is not None:calls.add(args)
        word_calls[shot]=sorted(calls,key=str)
    word_calls['maquette']=[('p1','Seul'),('p1','téléphone'),('p1','lire')]
    shots={}; lines=[f'# V01 {L} — préparation 3D sur la {real}','',
        'Aucun calcul Blender lancé. Images vidéo à 30 i/s, bornes inclusives dans le tableau ; images Blender locales numérotées depuis 1. Estimation indicative : 7 s par image calculée, hors initialisation.','',
        f'| Plan | Images vidéo {L} | Images locales | Pas | PNG à calculer | Temps GPU | Décalage début / fin depuis estimation {L} |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for shot,(a,b,step) in specs(en,LANG).items():
        n=b-a; count=math.ceil(n/step);fa,fb,_=specs(fr)[shot]
        actual=len(list((ROOT/'public/3d'/shot).glob('f[0-9][0-9][0-9][0-9].png')))
        words=[]
        for args in word_calls[shot]:
            words.append({'cue':list(args),'fr_global':fr(*args),f'{LANG}_global':en(*args),
                          'fr_local':fr(*args)-fa+1,f'{LANG}_local':en(*args)-a+1})
        shots[shot]={'from':a,'to_exclusive':b,'frames':n,'step':step,'render_count':count,
                     'gpu_seconds':7*count,'fr_png_present':actual,'words':words}
        delta=f'{a-old[shot][0]:+d} / {b-old[shot][1]:+d}' if old else '—'
        lines.append(f'| {shot} | {a}–{b-1} | 1–{n} | {step} | {count} | {7*count/60:.1f} min | {delta} |')
    lines+=['',f'## Repères déplacés (FR → {L}, images locales)','']
    for name,s in shots.items():
        lines.append(f'- **{name}** ({s["fr_png_present"]} PNG FR présents) : '+ '; '.join(f'{w["cue"]}: {w["fr_local"]} → {w[LANG+"_local"]}' for w in s['words'])+'.')
    total=sum(s['gpu_seconds'] for k,s in shots.items() if k!='maquette')
    lines+=['','## Réemploi proposé','',
        'La maquette initiale est une caméra sans action liée à un mot : réutiliser les images FR et atteindre l’image de vue verticale 138 au nouveau repère de fin. Les annotations téléphone/lecture sont déjà recalées par Remotion. Aucun recalcul nécessaire pour ce plan.',
        f'Pour les sept autres plans, une correspondance linéaire par morceaux entre les repères locaux du tableau peut réutiliser les PNG FR : fermer la porte, faire tomber le pion ou poser le point d’or exactement sur les mots {L}. Vérifier la monotonie de chaque correspondance, la continuité des vitesses et les fondus. Un étirement global unique ne garantit pas ces actions. Les plans très ralentis risquent une cadence visible ; les changements de vitesse doivent être lissés entre les actions.',
        f'Aucun réemploi ni nouveau rendu n’est branché automatiquement : les cartons 3D {L} restent actifs jusqu’à inspection des aperçus. Le plan dhikr conserve ensuite son dernier état pendant la traduction parlée, avant le verset silencieux.',
        f'Option recalcul intégral des sept plans animés : environ {total/60:.1f} min ({total/3600:.2f} h) à 7 s/image. Le rendu GPU réel peut différer.',
        '','## Commandes prêtes pour Claude, à lancer hors de ce bac à sable','','```bash',
        'HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py'+('' if LANG=='en' else f' --lang {LANG}')]
    for name,s in shots.items():
        if name=='maquette':continue
        base=f'python3 tools/plans3d.py {name} --cues out/validation/3d-{LANG}-cues.json --out-root out/3d-{LANG} --step {s["step"]} --samples 32 --gpu'
        lines.append(f'{base} --test 1,{s["frames"]//2},{s["frames"]} --pct 50')
        lines.append(base)
    lines+=['```','',f'Ces commandes écrivent les PNG et leur registre dans `out/3d-{LANG}/`. Après inspection, Claude devra prévoir leur copie vers des assets {L} séparés et leur branchement Remotion, dans une session autorisant cette écriture. Ne pas remplacer le registre ni les PNG FR.','']
    if LANG == 'ur':
        # Décision éditoriale : uniquement le réemploi FR, jamais de Blender.
        lines=['# V01 UR — réemploi 3D sur la voix réelle','',
            'Aucun calcul Blender. Les images françaises sont lues par `Shot3D`, avec les correspondances de `src/data/remap3d_ur.json`. Images vidéo à 30 i/s ; fin exclusive ; images locales depuis 1. Le plan dhikr finit à `at("p52") - 10`, quand le verset apparaît pendant la voix.','',
            '| Plan | Images vidéo UR [début, fin[ | Durée (images) | PNG FR présents | Décalage début / fin depuis estimation |',
            '|---|---:|---:|---:|---:|']
        for name,s in shots.items():
            delta=f'{s["from"]-old[name][0]:+d} / {s["to_exclusive"]-old[name][1]:+d}' if old else '—'
            lines.append(f'| {name} | {s["from"]} → {s["to_exclusive"]} | {s["frames"]} | {s["fr_png_present"]} | {delta} |')
        lines+=['','## Repères locaux FR → UR','']
        for name,s in shots.items():
            lines.append(f'- **{name}** : '+ '; '.join(f'{w["cue"]}: {w["fr_local"]} → {w["ur_local"]}' for w in s['words'])+'.')
        lines+=['','## Reproduction sans rendu 3D','',
            '```bash','HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py --lang ur',
            'HF_HUB_OFFLINE=1 python3 tools/remap3d_en.py --lang ur','```','',
            'Contrôler les PNG Remotion avec `WITH3D=1 FACELESS=1`, selon `docs/v01-ur-images-fixes.md`. Vérifier les changements de vitesse, les fondus et les éventuelles images tenues. Aucun PNG français n’est modifié.','']
    (out/f'3d-{LANG}-plan.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2)+'\n')
    (ROOT/f'docs/v01-{LANG}-3d.md').write_text('\n'.join(lines))
    print('Plans 3D préparés : aucun moteur de rendu chargé.')


if __name__=='__main__':main()
