// Version arabe : vérifications hors ligne + liste d'images à rendre ; aucun audio, aucun appel réseau.
// node tools/check_v01_ar.mjs [--baseline <répertoire src avant la version arabe>]
// Repris de tools/check_v01_en.mjs. Ce que l'on vérifie :
//  - le texte de la voix est exactement script/v01_texte_playground_balises_ar.txt (figé), mêmes IDs et pauses ;
//  - l'alignement contient tous les mots, dans l'ordre ; tous les repères arabes se trouvent ;
//  - V01-AR (avec et sans visage) et les trois Shorts arabes se rendent (HTML) sans texte français ni anglais oublié ;
//  - écriture de droite à gauche : tout texte arabe est dans un bloc `direction: rtl` (SVG exceptés) ;
//  - le verset : texte uthmani exact, Amiri Quran, immobile entre ses fondus, rien dessous, musique et bruitages muets ;
//  - avec --baseline : le français et l'anglais (V01, V01-EN, leurs Shorts) gardent exactement le même HTML.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {prepareStills, htmlStills} from './stills_html.mjs';

const read = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const [fr, ar, vo, groups, anchors, frozen] = await Promise.all([
  read('script/v01.json'), read('script/v01_ar.json'), read('src/data/v01_ar.vo.json'),
  read('src/data/v01_ar.groups.json'), read('src/data/v01_ar.anchors.json'),
  fs.readFile('script/v01_texte_playground_balises_ar.txt', 'utf8'),
]);
// même normalisation que src/cues.ts
const norm = (s) => s.normalize('NFD').replace(/[̀-ًͯ-ٰٟـ]/g, '').toLowerCase()
  .replace(/ٱ/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[^a-z0-9ء-غف-ي]/g, '');
const ARABIC = /[؀-ۿ]/;

// 1. le texte figé, découpé sans perte
assert.deepEqual(ar.segments.map(({id, pause}) => ({id, pause})), fr.segments.map(({id, pause}) => ({id, pause})));
assert.equal(ar.lead, fr.lead); assert.equal(ar.tail, fr.tail); assert.equal(ar.language, 'ar');
const paragraphs = frozen.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
assert.equal(paragraphs.length, Object.keys(groups).length);
const byId = Object.fromEntries(ar.segments.map((s) => [s.id, s]));
Object.values(groups).forEach((ids, i) => assert.equal(ids.map((id) => byId[id].text).join(' '), paragraphs[i], `Texte figé, paragraphe p${i + 1}`));
assert.deepEqual(Object.values(groups).flat(), ar.segments.map((s) => s.id));

// 2. l'alignement : tous les mots, dans l'ordre
assert.equal(vo.audio, 'vo/v01_ar.wav', 'La vraie voix arabe doit être branchée');
assert(!vo.estimated, 'Alignement estimé interdit pour la livraison');
assert.deepEqual(vo.silences, [], 'Aucun plateau silencieux ajouté au WAV arabe');
assert.deepEqual(vo.segments.map((s) => s.id), ar.segments.map((s) => s.id));
for (const [i, s] of ar.segments.entries()) {
  const expected = s.text.replace(/\[[^\]]*\]/g, '').match(/[\p{L}\p{M}\p{N}_'’-]+/gu).filter(norm);
  assert.deepEqual(vo.segments[i].words.map((w) => w.w), expected, `Texte complet ${s.id}`);
}
const segments = Object.fromEntries(vo.segments.map((s) => [s.id, s]));
const words = vo.segments.flatMap((s) => s.words);
for (let i = 0; i < words.length; i++) {
  assert(words[i].start < words[i].end, `Durée du mot ${i}`);
  if (i) assert(words[i - 1].end <= words[i].start, `Ordre des mots ${i}`);
}

// 3. les repères arabes (clé = le mot français du montage)
const en = await read('src/data/v01_en.anchors.json');
for (const [id, keys] of Object.entries(en)) for (const key of Object.keys(keys)) assert(anchors[id]?.[key], `Repère manquant ${id}:${key}`);
let anchorCount = 0;
for (const [id, targets] of Object.entries(anchors)) {
  const ws = groups[id].flatMap((s) => segments[s].words).map((w) => norm(w.w));
  for (const [key, target] of Object.entries(targets)) {
    const phrase = (typeof target === 'string' ? target : target.phrase).split(' ').map(norm);
    const nth = typeof target === 'string' ? 0 : target.nth;
    const hits = ws.map((_, i) => i).filter((i) => phrase.every((w, j) => w === ws[i + j]));
    assert(hits.length > nth, `Repère introuvable ${id}:${key}`); anchorCount++;
  }
}

// 4. rendu HTML de V01-AR
const outDir = 'out/validation-ar';
const render = await prepareStills({outDir: path.join(outDir, 'check')});
const duration = render('V01-AR', 0).durationInFrames;
const at = (p) => 24 + Math.round(segments[groups[p][0]].start * 30);
const end = (p) => 24 + Math.round(segments[groups[p].at(-1)].end * 30);
const frames = new Set();
for (let f = 0; f < duration; f += 30) frames.add(f);
for (const s of vo.segments) for (const t of [s.start, s.end]) for (const d of [-1, 0, 1, 10]) frames.add(Math.min(duration - 1, 24 + Math.round(t * 30) + d));

// Latin autorisé à l'écran en arabe : noms propres et mots des documents, chiffres, signes
const LATIN_OK = new Set(['Science', '«OTHER TECHNIQUES»', 'BILLKARKARIY', 'bilLkarkariy']);
const texts = new Set();
const latin = new Set();
const ltrArabic = new Set();
const textNodes = (markup) => {
  // pile des balises ouvertes : un texte arabe doit avoir un ancêtre « direction:rtl » (hors SVG)
  const out = [];
  const stack = [];
  for (const m of markup.matchAll(/<(\/?)([a-zA-Z][\w:-]*)((?:[^>"']|"[^"]*"|'[^']*')*?)(\/?)>|([^<]+)/g)) {
    if (m[5] !== undefined) {
      const text = m[5].replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
      if (text.trim()) out.push({text, rtl: stack.some((t) => /direction:\s*rtl/.test(t.attrs)), svg: stack.some((t) => t.tag === 'svg' || t.tag === 'text'), style: stack.some((t) => t.tag === 'style'), parent: stack.at(-1)});
      continue;
    }
    const [, close, tag, attrs, self] = m;
    if (close) { while (stack.length && stack.pop().tag !== tag); }
    else if (!self) stack.push({tag, attrs});
  }
  return out;
};
let rtlChecked = 0;
for (const f of [...frames].sort((a, b) => a - b)) {
  const {markup} = render('V01-AR', f);
  for (const t of textNodes(markup)) {
    if (t.style) continue;
    texts.add(t.text);
    if (/[A-Za-zÀ-ÿ]/.test(t.text) && !LATIN_OK.has(t.text.trim())) latin.add(t.text.trim());
    if (ARABIC.test(t.text) && !t.svg) { rtlChecked++; if (!t.rtl) ltrArabic.add(`${f}: ${t.text.trim()} < ${t.parent?.tag} ${t.parent?.attrs.slice(0, 200)}`); }
  }
  // pas d'étiquette d'archive (les sources restent dans la description)
  assert(!/PUBMED CENTRAL|WILSON ET AL\.|TRAD\. W\. M\. WATT|PENSEESDEPASCAL|MÉDIAMÉTRIE ·|ARCEP ·/.test(markup), `Source à l'écran : ${f}`);
}
// la version livrée est sans visage et sans cartons de travail (comme l'anglais) : mêmes contrôles sur ses pages
const delivered = await prepareStills({outDir: path.join(outDir, 'check-faceless'), faceless: true, clean: true});
assert.equal(delivered('V01-AR', 0).durationInFrames, duration);
let facelessFrames = 0;
for (let f = 0; f < duration; f += 15) {
  for (const t of textNodes(delivered('V01-AR', f).markup)) {
    if (t.style) continue;
    texts.add(t.text);
    if (/[A-Za-zÀ-ÿ]/.test(t.text) && !LATIN_OK.has(t.text.trim())) latin.add(`sans visage ${f}: ${t.text.trim()}`);
    if (ARABIC.test(t.text) && !t.svg) { rtlChecked++; if (!t.rtl) ltrArabic.add(`sans visage ${f}: ${t.text.trim()}`); }
  }
  facelessFrames++;
}
await fs.writeFile(path.join(outDir, 'rendered-text.txt'), [...texts].join('\n'));
assert.deepEqual([...latin], [], `Texte non traduit à l'écran : ${[...latin].join(' | ')}`);
assert.deepEqual([...ltrArabic], [], `Texte arabe sans direction rtl : ${[...ltrArabic].join(' | ')}`);

// 5. le verset : la voix arabe le dit, l'écran ne montre que le texte uthmani
const verseStart = at('p52') - 10;
const verseEnd = Math.min(at('p53') - 6, end('p52') + 30);
assert(verseEnd - verseStart >= 29, 'Le verset doit laisser au moins un plateau entre les fondus');
// (une séquence vide, sans rien à l'écran, peut s'ouvrir pendant le plateau : on l'ignore)
const visible = (markup) => markup.replace(/<div style="[^"]*"><\/div>/g, '');
const verseA = visible(render('V01-AR', verseStart + 14).markup);
const verseB = visible(render('V01-AR', verseEnd - 15).markup);
assert.equal(verseA, verseB, 'Le verset doit être immobile entre ses fondus');
assert(verseA.includes('Amiri Quran'));
assert(verseA.includes('ٱلَّذِينَ ءَامَنُوا۟ وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ ٱللَّهِ ۗ'));
assert(verseA.includes('أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ'));
assert(!/rappel de Dieu|remembrance of Allah|CORAN|QURAN|سورة/.test(verseA), 'Rien sous le verset en arabe');
for (let f = verseStart; f < verseEnd; f++) {
  const shot = render('V01-AR', f);
  assert(!/3d\//.test(shot.markup), `Plan 3D sous le verset : ${f}`);
  assert.deepEqual(textNodes(shot.markup).filter((t) => !t.style).map((t) => t.text.trim()).filter(Boolean), [
    'ٱلَّذِينَ ءَامَنُوا۟ وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ ٱللَّهِ ۗ',
    'أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ',
  ], `Texte autre que le verset : ${f}`);
  if (f >= verseStart + 14 && f <= verseEnd - 15) {
    assert.equal(visible(shot.markup), verseA, `Mouvement pendant le verset : ${f}`);
  }
  assert(shot.audio.some((a) => a.src.endsWith(vo.audio) && a.volume === 1), `Voix coupée sous le verset : ${f}`);
  for (const a of shot.audio) {
    if (a.src.endsWith(vo.audio)) continue; // la voix dit le verset
    assert.equal(a.volume, 0, `Son sous le verset : ${f} ${a.src}`);
  }
}

// 6. images à regarder (rendu PNG sur le Mac : voir docs/v01-ar-images-fixes.md)
const boundaries = [0, at('p7') - 8, at('p20') - 4, at('p35') - 4, at('p54') - 6, duration];
const pairs = boundaries.slice(0, -1).flatMap((a, i) => [
  {name: `p${i + 1}_debut`, frame: a + 30},
  {name: `p${i + 1}_milieu`, frame: Math.round((a + boundaries[i + 1]) / 2)},
  {name: `p${i + 1}_fin`, frame: boundaries[i + 1] - 35},
]);
const mid = (p) => Math.round((at(p) + end(p)) / 2);
const named = {
  plan: at('p2') + 20, points: end('p3') + 6, revue: at('p6') + 30, derniere_phrase: mid('p6'), consigne: end('p8') - 20,
  decharge: mid('p9'), groupes: mid('p11'), resultats: mid('p13'), page_labo: mid('p14'), vagabondage: mid('p15'),
  domicile: end('p16') - 10, etude9: mid('p17'), preparation: mid('p19'), scenariste: at('p20') + 40, pellicule: end('p20'),
  boulangerie: end('p21') - 10, page_question: end('p22') + 20, harvard: mid('p23'), resultats_kg: mid('p24'), titre_kg: end('p25') - 10,
  ascenseur: mid('p26'), mediametrie: mid('p27'), annees: at('p29') + 6, pascal: mid('p29'), solitude: mid('p30'), poche: mid('p31'),
  nuit: mid('p32'), page_cause: mid('p34'), vide: mid('p35'), muscle: mid('p37'), techniques: mid('p39'), siecles: mid('p40'),
  mot_solitude: end('p41'), khalwa_mot: mid('p43'), khalwa_3d: mid('p44'), carte_bagdad: mid('p46'), langue: mid('p47'),
  carte_damas: at('p48') + 60, minaret: end('p48') - 10, ihya: mid('p49'), dhikr_mot: at('p51') + 10, chapelet: at('p51') + 70, dhikr_3d: end('p51'),
  verset: Math.round((verseStart + verseEnd) / 2), verset_fondu_entree: verseStart + 7, verset_fondu_sortie: verseEnd - 7,
  fondements: end('p53') - 20, exercice_1: mid('p55'), exercice_2: mid('p56'), exercice_3: mid('p57'), exercice_4: end('p58') - 30,
  exercice_5: mid('p59'), envie: end('p60') - 10, retours: end('p61') - 10, bouton_poche: end('p63') - 10, revelation: mid('p65'),
  page_entraine: mid('p66'), meublee: mid('p67'), page_suite: end('p68') - 10, ecran_final: duration - 90,
};
for (const [name, frame] of Object.entries(named)) pairs.push({name, frame: Math.min(duration - 1, frame)});
await htmlStills({outDir: path.join(outDir, 'ar'), pairs, composition: 'V01-AR'});
const facelessPairs = pairs.filter(({name}) => /^page_|^p1_debut$|^revelation$|^meublee$|^retours$|^consigne$|^ecran_final$/.test(name));
await htmlStills({outDir: path.join(outDir, 'ar-sans-visage'), pairs: facelessPairs, composition: 'V01-AR', faceless: true, clean: true});

// 7. les Shorts arabes
const shortDurations = {};
const shortPairs = {};
for (const id of ['short-bouton-ar', 'short-pascal-ar', 'short-exercice-ar']) {
  const n = render(id, 0).durationInFrames; shortDurations[id] = n;
  for (let f = 0; f < n; f += 30) {
    for (const t of textNodes(render(id, f).markup)) {
      if (t.style) continue;
      if (/[A-Za-zÀ-ÿ]/.test(t.text) && !LATIN_OK.has(t.text.trim())) latin.add(`${id}:${t.text.trim()}`);
      if (ARABIC.test(t.text) && !t.svg && !t.rtl) ltrArabic.add(`${id}:${t.text.trim()}`);
    }
  }
  shortPairs[id] = [{name: 'debut', frame: 60}, {name: 'milieu', frame: Math.round(n / 2)}, {name: 'fin', frame: n - 30}];
  await htmlStills({outDir: path.join(outDir, id), composition: id, pairs: shortPairs[id]});
}
assert.deepEqual([...latin], [], `Texte non traduit dans les Shorts : ${[...latin].join(' | ')}`);
assert.deepEqual([...ltrArabic], [], `Texte arabe sans direction rtl dans les Shorts : ${[...ltrArabic].join(' | ')}`);

// 8. le français et l'anglais n'ont pas bougé
let comparison;
const baselineIndex = process.argv.indexOf('--baseline');
if (baselineIndex !== -1) {
  const sourceRoot = process.argv[baselineIndex + 1];
  assert(sourceRoot, '--baseline attend un répertoire src');
  const before = await prepareStills({outDir: path.join(outDir, 'compare-before'), sourceRoot});
  comparison = {count: 0, different: []};
  for (const id of ['V01', 'V01-EN', 'short-bouton', 'short-pascal', 'short-exercice', 'short-bouton-en', 'short-pascal-en', 'short-exercice-en']) {
    const n = before(id, 0).durationInFrames;
    assert.equal(render(id, 0).durationInFrames, n, `Durée de ${id}`);
    for (let f = 0; f < n; f += 30) {
      const a = before(id, f); const b = render(id, f);
      if (a.markup !== b.markup || JSON.stringify(a.audio) !== JSON.stringify(b.audio)) comparison.different.push(`${id}:${f}`);
      comparison.count++;
    }
  }
  assert.deepEqual(comparison.different, []);
}

const report = {segments: ar.segments.length, words: words.length, anchors: anchorCount, durationInFrames: duration,
  duration: `${Math.floor(duration / 1800)}:${String(Math.round(duration / 30) % 60).padStart(2, '0')}`, estimated: Boolean(vo.estimated),
  checkedArabicFrames: frames.size, checkedFacelessFrames: facelessFrames, arabicTextNodesCheckedRtl: rtlChecked, shortDurations, frenchEnglishComparison: comparison,
  verse: [verseStart, verseEnd], audioSource: vo.audio,
  pngInspection: 'NOT_PERFORMED: HTML only; PNG stills to render on the Mac (docs/v01-ar-images-fixes.md)', stills: pairs, shortStills: shortPairs};
await fs.writeFile(path.join(outDir, 'v01-ar-report.json'), JSON.stringify(report, null, 2) + '\n');
await fs.writeFile(path.join(outDir, 'render-ar-stills.txt'), 'node tools/stills.mjs out/stills-ar --composition V01-AR ' + pairs.map(({name, frame}) => `${name}:${frame}`).join(' ') + '\n');
console.log(JSON.stringify({...report, stills: `${pairs.length} vues V01-AR + ${facelessPairs.length} sans visage + 9 vues Shorts, HTML`, shortStills: undefined}, null, 2));
