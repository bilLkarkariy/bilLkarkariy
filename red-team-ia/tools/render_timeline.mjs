// Rend la timeline (page HTML au format Artifact, sans squelette) en PDF A4 d'une page.
//   node red-team-ia/tools/render_timeline.mjs [--png apercu.png]
// Nécessite Playwright (Node) et un accès à fonts.googleapis.com pour les polices.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = join(root, '02-timeline-black-october.html');
const out = join(root, '02-timeline-black-october.pdf');
const pngArg = process.argv.indexOf('--png');

// Même squelette que celui ajouté à la publication de l'Artifact.
const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>${readFileSync(src, 'utf8')}</body></html>`;

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fonts.some(f => f.includes('Archivo')) || !fonts.some(f => f.includes('IBM Plex'))) {
    throw new Error(`Polices non chargées (${[...new Set(fonts)].join(', ') || 'aucune'}) : vérifier l'accès à Google Fonts.`);
  }
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  if (pngArg > -1) {
    await page.setViewportSize({ width: 794, height: 1123 });
    await page.screenshot({ path: process.argv[pngArg + 1], fullPage: true });
  }
  console.log(`PDF écrit : ${out}`);
} finally {
  await browser.close();
}
