// node tools/stills.mjs out/stills --composition V01-EN debut:300 milieu:9000
// --html : planche locale de secours, sans lancer Chromium ; pas un export PNG.
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs/promises';
import path from 'node:path';

const args = process.argv.slice(2);
const outDir = args.shift();
let compositionId = process.env.COMPOSITION ?? 'V01';
let html = false;
const pairs = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--composition') { compositionId = args[++i]; continue; }
  if (args[i] === '--html') { html = true; continue; }
  const match = /^([a-zA-Z0-9_-]+):(\d+)$/.exec(args[i]);
  if (!match) throw new Error(`Image invalide : ${args[i]} (nom:frame attendu)`);
  pairs.push({name: match[1], frame: Number(match[2])});
}
if (!outDir || !pairs.length) throw new Error('Usage : node tools/stills.mjs out/stills [--composition V01-EN] [--html] nom:frame …');
await fs.mkdir(outDir, {recursive: true});
const inputProps = {no3d: !process.env.WITH3D, clean: Boolean(process.env.CLEAN)};
if (html) {
  const {htmlStills} = await import('./stills_html.mjs');
  await htmlStills({outDir, pairs, composition: compositionId, sourceRoot: process.env.SOURCE_ROOT, ...inputProps});
  console.log(path.join(outDir, 'index.html'));
} else {
  const serveUrl = path.resolve(process.env.BUNDLE ?? 'out/bundle');
  const browser = await openBrowser('chrome', {browserExecutable: process.env.CHROME ?? null});
  try {
    const composition = await selectComposition({serveUrl, id: compositionId, inputProps, puppeteerInstance: browser});
    for (const {name, frame} of pairs) {
      await renderStill({composition, serveUrl, frame, output: path.join(outDir, `${name}.png`), inputProps, puppeteerInstance: browser, scale: Number(process.env.SCALE ?? 0.5)});
      console.log(name, frame);
    }
  } finally {
    await browser.close({silent: true});
  }
}
