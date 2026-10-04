// Vérifications hors ligne + liste d'images à rendre ; aucun audio, aucun appel réseau.
// node tools/check_v01_en.mjs [--baseline <répertoire src FR>]
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {prepareStills, htmlStills} from './stills_html.mjs';
const read = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const [fr, en, vo, groups, anchors] = await Promise.all([
  read('script/v01.json'), read('script/v01_en.json'), read('src/data/v01_en.vo.json'),
  read('src/data/v01_en.groups.json'), read('src/data/v01_en.anchors.json'),
]);
const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
assert.deepEqual(en.segments.map(({id, pause}) => ({id, pause})), fr.segments.map(({id, pause}) => ({id, pause})));
assert.deepEqual(en.segments.map((s) => s.text.match(/\[[^\]]*\]/g)), fr.segments.map((s) => s.text.match(/\[[^\]]*\]/g)));
assert.deepEqual(vo.segments.map((s) => s.id), en.segments.map((s) => s.id));
const segments = Object.fromEntries(vo.segments.map((s) => [s.id, s]));
const words = vo.segments.flatMap((s) => s.words);
for (let i = 0; i < words.length; i++) {
  assert(words[i].start < words[i].end, `Durée du mot ${i}`);
  if (i) assert(words[i-1].end <= words[i].start, `Ordre des mots ${i}`);
}
assert.deepEqual(Object.values(groups).flat(), en.segments.map((s) => s.id));
let anchorCount = 0;
for (const [id, targets] of Object.entries(anchors)) {
  const ws = groups[id].flatMap((s) => segments[s].words).map((w) => norm(w.w));
  for (const [key, target] of Object.entries(targets)) {
    const phrase = (typeof target === 'string' ? target : target.phrase).split(' ').map(norm);
    const nth = typeof target === 'string' ? 0 : target.nth;
    const hits = ws.map((_, i) => i).filter((i) => phrase.every((w, j) => w === ws[i+j]));
    assert(hits.length > nth, `${id}:${key}`); anchorCount++;
  }
}
const outDir = 'out/validation';
const render = await prepareStills({outDir: path.join(outDir, 'check')});
const duration = render('V01_EN', 0).durationInFrames;
const at = (p) => 24 + Math.round(segments[groups[p][0]].start * 30);
const end = (p) => 24 + Math.round(segments[groups[p].at(-1)].end * 30);
const frames = new Set();
for (let f = 0; f < duration; f += 30) frames.add(f);
for (const s of vo.segments) for (const t of [s.start, s.end]) for (const d of [-1, 0, 1, 10]) frames.add(24 + Math.round(t * 30) + d);
const texts = new Set();
for (const f of [...frames].sort((a, b) => a-b)) {
  const {markup} = render('V01_EN', f);
  for (const [, text] of markup.matchAll(/>([^<>]+)</g)) if (/[a-zà-ÿ]/i.test(text)) texts.add(text);
  // Ces captures et étiquettes ne doivent pas revenir dans la version EN.
  assert(!/captures\/(?:mm_3h|mm_mobile|arcep_2025|pascal_chambre|pascal_solitude|pascal_ro139|pascal_ro210)\.png/.test(markup));
  assert(!/PUBMED CENTRAL|WILSON ET AL\.|TRAD\. W\. M\. WATT|PENSEESDEPASCAL/.test(markup));
}
await fs.writeFile(path.join(outDir, 'rendered-text.txt'), [...texts].join('\n'));
// Même texte uthmani, police Amiri Quran, et aucun mouvement pendant le plateau du fondu.
const verseA = render('V01_EN', at('p52') + 30).markup;
const verseB = render('V01_EN', at('p52') + 60).markup;
assert.equal(verseA, verseB, 'Le verset doit être immobile entre ses fondus');
assert(verseA.includes('Amiri Quran'));
assert(verseA.includes('أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ'));
const boundaries = [0, at('p7')-8, at('p20')-4, at('p35')-4, at('p54')-6, duration];
const pairs = boundaries.slice(0, -1).flatMap((a, i) => [
  {name: `p${i+1}_debut`, frame: a+30},
  {name: `p${i+1}_milieu`, frame: Math.round((a+boundaries[i+1])/2)},
  {name: `p${i+1}_fin`, frame: boundaries[i+1]-35},
]);
for (const [name, p] of Object.entries({consigne:'p8', ecrans:'p27', pascal:'p29', solitude:'p30', khalwa:'p44', carte:'p46', ghazali:'p47', dhikr:'p51', verset:'p52', fondements:'p53', point:'p58', retour:'p59', revelation:'p65'})) {
  pairs.push({name, frame: Math.round((at(p)+end(p))/2)});
}
await htmlStills({outDir:path.join(outDir, 'en'), pairs, composition:'V01_EN'});
const shortDurations = {};
for (const id of ['short-bouton-en', 'short-pascal-en', 'short-exercice-en']) {
  const n = render(id, 0).durationInFrames; shortDurations[id] = n;
  for (let f = 0; f < n; f += 30) render(id, f);
  await htmlStills({outDir:path.join(outDir, id), composition:id, pairs:[{name:'debut', frame:60}, {name:'milieu', frame:Math.round(n/2)}, {name:'fin', frame:n-30}]});
}
let frenchComparison;
const baselineIndex = process.argv.indexOf('--baseline');
if (baselineIndex !== -1) {
  const sourceRoot = process.argv[baselineIndex+1];
  assert(sourceRoot, '--baseline attend un répertoire src FR');
  const before = await prepareStills({outDir:path.join(outDir,'compare-before'), sourceRoot});
  frenchComparison = {count:0, different:[]};
  for (const id of ['V01', 'short-bouton', 'short-pascal', 'short-exercice']) {
    const n = before(id, 0).durationInFrames;
    assert.equal(render(id, 0).durationInFrames, n);
    for (let f=0; f<n; f+=30) {
      if (before(id,f).markup !== render(id,f).markup) frenchComparison.different.push(`${id}:${f}`);
      frenchComparison.count++;
    }
  }
  assert.deepEqual(frenchComparison.different, []);
}
const report = {segments:en.segments.length, anchors:anchorCount, durationInFrames:duration, checkedEnglishFrames:frames.size,
  shortDurations, frenchComparison, pngInspection:'NOT_PERFORMED: this check renders HTML, not PNG; inspect stills.mjs PNG output separately', stills:pairs};
await fs.writeFile(path.join(outDir,'v01-en-report.json'),JSON.stringify(report,null,2)+'\n');
await fs.writeFile(path.join(outDir,'render-en-stills.txt'), 'node tools/stills.mjs out/validation/en-png --composition V01_EN '+pairs.map(({name,frame})=>`${name}:${frame}`).join(' ')+'\n');
console.log(JSON.stringify({...report,stills:`${pairs.length} vues EN + 9 vues Shorts, HTML`},null,2));
