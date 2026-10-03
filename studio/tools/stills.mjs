// Images fixes du montage, un seul navigateur pour toutes : node tools/stills.mjs out/stills nom:image nom:image …
// (les plans 3D sont remplacés par leur carton : --props no3d)
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';

const [outDir, ...pairs] = process.argv.slice(2);
const serveUrl = path.resolve(process.env.BUNDLE ?? 'out/bundle');
const inputProps = {no3d: !process.env.WITH3D};
const browser = await openBrowser('chrome', {browserExecutable: process.env.CHROME ?? null});
const composition = await selectComposition({serveUrl, id: 'V01', inputProps, puppeteerInstance: browser});
for (const p of pairs) {
  const [name, f] = p.split(':');
  await renderStill({composition, serveUrl, frame: Number(f), output: path.join(outDir, `${name}.png`), inputProps, puppeteerInstance: browser, scale: Number(process.env.SCALE ?? 0.5)});
  console.log(name, f);
}
await browser.close({silent: true});
