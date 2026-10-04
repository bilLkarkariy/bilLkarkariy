// Vérifications hors ligne + liste d'images à rendre ; aucun audio, aucun appel réseau.
// node tools/check_v01_en.mjs [--lang en|ur] [--baseline <répertoire src FR>]
// Sans --lang : l'anglais, comme avant. Avec --baseline, le français (et l'anglais, pour une autre langue)
// doit sortir à l'identique de la source de référence.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {prepareStills, htmlStills} from './stills_html.mjs';
const arg = (name) => { const i = process.argv.indexOf(name); return i === -1 ? undefined : process.argv[i+1]; };
const lang = arg('--lang') ?? 'en';
// Pour chaque langue : traduction du verset affichée sous l'arabe, écriture (latine ou arabe).
const LANGS = {
  en: {verse: 'Verily in the remembrance of Allah do hearts find rest!', arabicScript: false},
  ur: {verse: 'سن لو، اللہ کی یاد ہی میں دلوں کا چین ہے', arabicScript: true, frozen: 'script/v01_texte_playground_balises_ur.txt'},
};
const cfg = LANGS[lang];
assert(cfg, `Langue inconnue : ${lang} (${Object.keys(LANGS).join(', ')})`);
const L = lang.toUpperCase();
const COMP = `V01-${L}`;
const read = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const [fr, en, vo, groups, anchors] = await Promise.all([
  read('script/v01.json'), read(`script/v01_${lang}.json`), read(`src/data/v01_${lang}.vo.json`),
  read(`src/data/v01_${lang}.groups.json`), read(`src/data/v01_${lang}.anchors.json`),
]);
// Même normalisation que src/cues.ts : latin sans accents, ou écriture arabe sans signes (voyelles brèves, hamza).
const norm = cfg.arabicScript
  ? (s) => s.normalize('NFD').replace(/\p{M}/gu, '').replace(/[^\p{L}\p{N}]/gu, '')
  : (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
const WORD = cfg.arabicScript ? /[\p{L}\p{M}\p{N}]+/gu : /[\p{L}\p{N}_'’-]+/gu;
assert.deepEqual(en.segments.map(({id, pause}) => ({id, pause})), fr.segments.map(({id, pause}) => ({id, pause})));
if (cfg.frozen) {
  // Le texte de la voix est figé : les segments, mis bout à bout, le redonnent mot pour mot (balises comprises).
  const flat = (s) => s.replace(/\s+/g, ' ').trim();
  assert.equal(flat(en.segments.map((s) => s.text).join(' ')), flat(await fs.readFile(cfg.frozen, 'utf8')), 'Texte figé modifié');
} else {
  assert.deepEqual(en.segments.map((s) => s.text.match(/\[[^\]]*\]/g)), fr.segments.map((s) => s.text.match(/\[[^\]]*\]/g)));
}
assert.deepEqual(vo.segments.map((s) => s.id), en.segments.map((s) => s.id));
for (const [i,s] of en.segments.entries()) {
  const expected = s.text.replace(/\[[^\]]*\]/g, '').match(WORD).filter(norm);
  assert.deepEqual(vo.segments[i].words.map((w) => w.w), expected, `Texte complet ${s.id}`);
}
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
const duration = render(COMP, 0).durationInFrames;
const at = (p) => 24 + Math.round(segments[groups[p][0]].start * 30);
const end = (p) => 24 + Math.round(segments[groups[p].at(-1)].end * 30);
const frames = new Set();
for (let f = 0; f < duration; f += 30) frames.add(f);
for (const s of vo.segments) for (const t of [s.start, s.end]) for (const d of [-1, 0, 1, 10]) frames.add(24 + Math.round(t * 30) + d);
const texts = new Set();
const latin = new Set(); // écriture arabe : textes encore en lettres latines (à relire)
for (const f of [...frames].sort((a, b) => a-b)) {
  const {markup} = render(COMP, f);
  for (const [, text] of markup.replace(/<style>[^]*?<\/style>/g, '').matchAll(/>([^<>]+)</g)) {
    if (/\p{L}/u.test(text)) texts.add(text);
    if (cfg.arabicScript && /[a-zà-ÿ]{2,}/i.test(text)) latin.add(text);
  }
  // Ces captures et étiquettes françaises ne doivent pas revenir hors de la version FR.
  assert(!/captures\/(?:mm_3h|mm_mobile|arcep_2025|pascal_chambre|pascal_solitude|pascal_ro139|pascal_ro210)\.png/.test(markup));
  assert(!/PUBMED CENTRAL|WILSON ET AL\.|TRAD\. W\. M\. WATT|PENSEESDEPASCAL/.test(markup));
  if (cfg.arabicScript) assert(markup.includes('dir="rtl"'), `Sens de lecture absent : ${f}`);
}
await fs.writeFile(path.join(outDir, lang === 'en' ? 'rendered-text.txt' : `rendered-text-${lang}.txt`), [...texts].join('\n'));
if (cfg.arabicScript) await fs.writeFile(path.join(outDir, `latin-${lang}.txt`), [...latin].join('\n'));
// Même texte uthmani, police Amiri Quran, et aucun mouvement pendant le plateau du fondu.
const hold = vo.silences?.find((s) => s.kind === 'silent_verse');
const verseStart = hold ? 24 + Math.round(hold.start * 30) : vo.audio ? end('p52') + 1 : at('p52') - 10;
const verseEnd = hold ? Math.min(at('p53') - 6, 24 + Math.round(hold.end * 30)) : at('p53') - 6;
assert(verseEnd - verseStart >= 29, 'Le verset doit laisser au moins un plateau entre les fondus');
const verseA = render(COMP, verseStart + 14).markup;
const verseB = render(COMP, verseEnd - 15).markup;
assert.equal(verseA, verseB, 'Le verset doit être immobile entre ses fondus');
assert(verseA.includes('Amiri Quran'));
assert(verseA.includes('أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ'));
assert(verseA.includes(cfg.verse));
// Sans voix : aucune musique non plus pendant le plateau du verset.
for (let f = verseStart; f < verseEnd; f += 5) assert(render(COMP, f).audio.every((a) => a.volume === 0), `Son sous le verset : ${f}`);
if (vo.audio) {
  assert.equal(vo.audio, `vo/v01_${lang}.wav`);
  for (let f = verseStart; f < verseEnd; f++) {
    assert(render(COMP, f).audio.every((a) => a.volume === 0), `Son sous le verset : ${f}`);
    assert(!words.some((w) => 24 + w.start*30 < f+1 && 24 + w.end*30 > f), `Mot sous le verset : ${f}`);
  }
  for (const w of segments.s63.words) {
    const f = 24 + Math.round((w.start+w.end)*15);
    assert(render(COMP,f).audio.some((a) => a.src.endsWith(vo.audio) && a.volume === 1), `Traduction inaudible : ${w.w}`);
  }
}
const boundaries = [0, at('p7')-8, at('p20')-4, at('p35')-4, at('p54')-6, duration];
const pairs = boundaries.slice(0, -1).flatMap((a, i) => [
  {name: `p${i+1}_debut`, frame: a+30},
  {name: `p${i+1}_milieu`, frame: Math.round((a+boundaries[i+1])/2)},
  {name: `p${i+1}_fin`, frame: boundaries[i+1]-35},
]);
for (const [name, p] of Object.entries({consigne:'p8', ecrans:'p27', pascal:'p29', solitude:'p30', khalwa:'p44', carte:'p46', ghazali:'p47', dhikr:'p51', verset:'p52', fondements:'p53', point:'p58', retour:'p59', revelation:'p65'})) {
  pairs.push({name, frame: name === 'verset' ? Math.round((verseStart+verseEnd)/2) : Math.round((at(p)+end(p))/2)});
}
for (const [name,frame] of Object.entries({verset_fondu_entree:verseStart+7, verset_fondu_sortie:verseEnd-7,
  verset_avant:verseStart-1, verset_apres:verseEnd, traduction_parlee:Math.round((at('p52')+end('p52'))/2),
  pause_question:24+Math.round(segments.s33.end*30)+30, chuchotements:24+Math.round(segments.s69.words.at(-1).start*30),
  fin_voix:24+Math.round(segments.s79.end*30), ecran_final:duration-90})) pairs.push({name,frame});
await htmlStills({outDir:path.join(outDir, lang), pairs, composition:COMP});
const shortDurations = {};
for (const id of ['bouton', 'pascal', 'exercice'].map((s) => `short-${s}-${lang}`)) {
  const n = render(id, 0).durationInFrames; shortDurations[id] = n;
  for (let f = 0; f < n; f += 30) {
    const {markup} = render(id, f);
    if (cfg.arabicScript) assert(markup.includes('dir="rtl"'), `Sens de lecture absent : ${id}:${f}`);
  }
  await htmlStills({outDir:path.join(outDir, id), composition:id, pairs:[{name:'debut', frame:60}, {name:'milieu', frame:Math.round(n/2)}, {name:'fin', frame:n-30}]});
}
let frenchComparison;
const sourceRoot = arg('--baseline');
if (process.argv.includes('--baseline')) {
  assert(sourceRoot, '--baseline attend un répertoire src FR');
  const before = await prepareStills({outDir:path.join(outDir,'compare-before'), sourceRoot});
  frenchComparison = {count:0, different:[]};
  const ids = ['V01', 'short-bouton', 'short-pascal', 'short-exercice'];
  // Une langue de plus ne doit pas déplacer l'anglais non plus.
  if (lang !== 'en') ids.push('V01-EN', 'short-bouton-en', 'short-pascal-en', 'short-exercice-en');
  for (const id of ids) {
    const n = before(id, 0).durationInFrames;
    assert.equal(render(id, 0).durationInFrames, n);
    for (let f=0; f<n; f+=30) {
      if (before(id,f).markup !== render(id,f).markup) frenchComparison.different.push(`${id}:${f}`);
      frenchComparison.count++;
    }
  }
  assert.deepEqual(frenchComparison.different, []);
}
const report = {lang, segments:en.segments.length, anchors:anchorCount, durationInFrames:duration, checkedFrames:frames.size,
  shortDurations, frenchComparison, verseSilence:[verseStart,verseEnd], audioSource:vo.audio, estimated:Boolean(vo.estimated),
  ...(cfg.arabicScript ? {latinTexts:[...latin]} : {}),
  pngInspection:'NOT_PERFORMED: this check renders HTML, not PNG; inspect stills.mjs PNG output separately', stills:pairs};
await fs.writeFile(path.join(outDir,`v01-${lang}-report.json`),JSON.stringify(report,null,2)+'\n');
await fs.writeFile(path.join(outDir,`render-${lang}-stills.txt`), `node tools/stills.mjs out/validation/${lang}-png --composition ${COMP} `+pairs.map(({name,frame})=>`${name}:${frame}`).join(' ')+'\n');
console.log(JSON.stringify({...report,stills:`${pairs.length} vues ${L} + 9 vues Shorts, HTML`},null,2));
