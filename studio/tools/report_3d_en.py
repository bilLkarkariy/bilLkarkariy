"""Prépare les plages et repères 3D EN sans importer ni lancer Blender.

HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py
Les commandes de rendu sortent vers out/3d-en, jamais dans les assets FR.
"""
import ast
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
# Repères exclusivement utilisés par Blender, en plus des 278 repères Remotion.
EXTRA={
    'p10':{'remettre|0':'another shock'},
    'p18':{'bouton|0':'button'},
    'p35':{'cherches|0':'looking','entres|0':'walk in','porte|0':'door',
           'quoi|0':'What do you do','tournes|0':'Walk around'},
    'p36':{'pièce|0':'that room'},
    'p44':{'retire|0':'withdraw'},
    'p51':{'part|0':{'phrase':'wanders','nth':0},'repart|0':{'phrase':'wanders','nth':1}},
}


def all_anchors():
    result=json.loads((ROOT/'src/data/v01_en.anchors.json').read_text())
    for pid,items in EXTRA.items():result.setdefault(pid,{}).update(items)
    return result


def norm(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()))


def cues(lang, source=None):
    vo=json.loads((source or ROOT/f'src/data/{"v01_en" if lang=="en" else "v01"}.vo.json').read_text())
    segments={s['id']:s for s in vo['segments']}
    groups=json.loads((ROOT/'src/data/v01_en.groups.json').read_text())
    anchors=all_anchors()
    def at(pid,w=None,edge='start',nth=0):
        if pid in segments:
            parts=[segments[pid]]
        else:
            parts=[segments[s] for s in groups[pid]]
        if w is None:
            t=parts[0]['start'] if edge=='start' else parts[-1]['end']
        else:
            words=[w for s in parts for w in s['words']]
            target=anchors[pid][f'{w}|{nth}'] if lang=='en' else w
            phrase=target if isinstance(target,str) else target['phrase']
            occurrence=(0 if isinstance(target,str) else target['nth']) if lang=='en' else nth
            ns=[norm(t) for t in phrase.split()]
            hits=[i for i in range(len(words)) if [norm(x['w']) for x in words[i:i+len(ns)]]==ns]
            index=hits[occurrence]
            t=words[index if edge=='start' else index+len(ns)-1][edge]
        return 24+math.floor(t*30+.5)
    return at


def specs(at):
    # Mêmes expressions que les séquences Remotion et tools/plans3d.py.
    return {
        'maquette':(at('p1','Seul')-3,at('p2')-10,2),
        'seuls':(at('p10')-4,at('p11')-4+2,2),
        'bouton':(at('p18')-4,at('p19')-1+2,2),
        'salon':(at('p16','chez')-3,at('p16','Un')-4+2,2),
        'vide':(at('p35')-4,at('p36',None,'end')+24,2),
        'khalwa':(at('p44')-6,at('p44',None,'end')+24,2),
        'dhikr':(at('p51',"L'idée")-6,at('p51',None,'end')+30,2),
        'meublee':(at('p67','meublé')-10,at('p68')+30,3),
    }


def main():
    en,fr=cues('en'),cues('fr')
    estimated=ROOT/'out/validation/vo-en/v01_en.estime.json'
    old=specs(cues('en',estimated)) if estimated.exists() else None
    out=ROOT/'out/validation';out.mkdir(parents=True,exist_ok=True)
    anchors=all_anchors()
    groups=json.loads((ROOT/'src/data/v01_en.groups.json').read_text())
    table={}
    for pid in groups:
        for edge in ('start','end'):
            table[f'{pid}||{edge}|0']=en(pid,None,edge)
        for key in anchors.get(pid,{}):
            w,nth=key.rsplit('|',1)
            for edge in ('start','end'):
                table[f'{pid}|{w}|{edge}|{nth}']=en(pid,w,edge,int(nth))
    (out/'3d-en-cues.json').write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n')
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
    shots={}; lines=['# V01 EN — préparation 3D sur la voix réelle','',
        'Aucun calcul Blender lancé. Images vidéo à 30 i/s, bornes inclusives dans le tableau ; images Blender locales numérotées depuis 1. Estimation indicative : 7 s par image calculée, hors initialisation.','',
        '| Plan | Images vidéo EN | Images locales | Pas | PNG à calculer | Temps GPU | Décalage début / fin depuis estimation EN |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for shot,(a,b,step) in specs(en).items():
        n=b-a; count=math.ceil(n/step);fa,fb,_=specs(fr)[shot]
        actual=len(list((ROOT/'public/3d'/shot).glob('f[0-9][0-9][0-9][0-9].png')))
        words=[]
        for args in word_calls[shot]:
            words.append({'cue':list(args),'fr_global':fr(*args),'en_global':en(*args),
                          'fr_local':fr(*args)-fa+1,'en_local':en(*args)-a+1})
        shots[shot]={'from':a,'to_exclusive':b,'frames':n,'step':step,'render_count':count,
                     'gpu_seconds':7*count,'fr_png_present':actual,'words':words}
        delta=f'{a-old[shot][0]:+d} / {b-old[shot][1]:+d}' if old else '—'
        lines.append(f'| {shot} | {a}–{b-1} | 1–{n} | {step} | {count} | {7*count/60:.1f} min | {delta} |')
    lines+=['','## Repères déplacés (FR → EN, images locales)','']
    for name,s in shots.items():
        lines.append(f'- **{name}** ({s["fr_png_present"]} PNG FR présents) : '+ '; '.join(f'{w["cue"]}: {w["fr_local"]} → {w["en_local"]}' for w in s['words'])+'.')
    total=sum(s['gpu_seconds'] for k,s in shots.items() if k!='maquette')
    lines+=['','## Réemploi proposé','',
        'La maquette initiale est une caméra sans action liée à un mot : réutiliser les images FR et atteindre l’image de vue verticale 138 au nouveau repère de fin. Les annotations téléphone/lecture sont déjà recalées par Remotion. Aucun recalcul nécessaire pour ce plan.',
        'Pour les sept autres plans, une correspondance linéaire par morceaux entre les repères locaux du tableau peut réutiliser les PNG FR : fermer la porte, faire tomber le pion ou poser le point d’or exactement sur les mots EN. Vérifier la monotonie de chaque correspondance, la continuité des vitesses et les fondus. Un étirement global unique ne garantit pas ces actions. Les plans très ralentis risquent une cadence visible ; les changements de vitesse doivent être lissés entre les actions.',
        'Aucun réemploi ni nouveau rendu n’est branché automatiquement : les cartons 3D EN restent actifs jusqu’à inspection des aperçus. Le plan dhikr conserve ensuite son dernier état pendant la traduction parlée, avant le verset silencieux.',
        f'Option recalcul intégral des sept plans animés : environ {total/60:.1f} min ({total/3600:.2f} h) à 7 s/image. Le rendu GPU réel peut différer.',
        '','## Commandes prêtes pour Claude, à lancer hors de ce bac à sable','','```bash',
        'HF_HUB_OFFLINE=1 python3 tools/report_3d_en.py']
    for name,s in shots.items():
        if name=='maquette':continue
        base=f'python3 tools/plans3d.py {name} --cues out/validation/3d-en-cues.json --out-root out/3d-en --step {s["step"]} --samples 32 --gpu'
        lines.append(f'{base} --test 1,{s["frames"]//2},{s["frames"]} --pct 50')
        lines.append(base)
    lines+=['```','','Ces commandes écrivent les PNG et leur registre dans `out/3d-en/`. Après inspection, Claude devra prévoir leur copie vers des assets EN séparés et leur branchement Remotion, dans une session autorisant cette écriture. Ne pas remplacer le registre ni les PNG FR.','']
    (out/'3d-en-plan.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'docs/v01-en-3d.md').write_text('\n'.join(lines))
    print('Plans 3D préparés : aucun moteur de rendu chargé.')


if __name__=='__main__':main()
