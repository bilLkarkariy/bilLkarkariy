// Secours local quand le bac à sable interdit de lancer Chromium.
// Même React/Remotion et mêmes frames ; Audio est omis et Img devient un <img> statique.
// Cette planche HTML ne remplace pas le contrôle PNG du renderer Remotion.
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {Internals} from 'remotion';
import {build} from 'esbuild';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export async function prepareStills({sourceRoot = 'src', outDir, no3d = true, clean = false}) {
  await fs.mkdir(outDir, {recursive: true});
  const entry = path.resolve(outDir, 'entry.ts');
  const output = path.resolve(outDir, 'render.mjs');
  const remotionPath = pathToFileURL(import.meta.resolve('remotion').replace('file://', '')).pathname;
  await fs.writeFile(entry, `export * from ${JSON.stringify(path.resolve(sourceRoot, 'V01.tsx'))};\nexport * from ${JSON.stringify(path.resolve(sourceRoot, 'Short.tsx'))};`);
  await build({entryPoints: [entry], outfile: output, bundle: true, packages: 'external', platform: 'node', format: 'esm', plugins: [{
    name: 'static-frame', setup(b) {
      b.onResolve({filter: /remotion\/dist\/esm\/index.mjs$/}, (a) => ({path: a.path, external: true}));
      b.onResolve({filter: /^remotion$/}, () => ({path: 'still', namespace: 'still'}));
      b.onLoad({filter: /.*/, namespace: 'still'}, () => ({loader: 'js', resolveDir: process.cwd(), contents: `
        export * from ${JSON.stringify(remotionPath)};
        import React from 'react';
        export const Audio = () => null;
        export const Img = ({pauseWhenBuffering, onError, onLoad, ...p}) => React.createElement('img', p);
        export const staticFile = (s) => ${JSON.stringify(pathToFileURL(path.resolve('public')).href + '/')} + s;
        export const getInputProps = () => (${JSON.stringify({no3d, clean})});
      `}));
    },
  }]});
  const m = await import(pathToFileURL(output).href + '?t=' + Date.now());
  return (id, frame) => {
    const lang = id.endsWith('-en') || id === 'V01_EN' ? 'en' : 'fr';
    const isShort = id.startsWith('short-');
    const short = isShort ? (m.getShorts ? m.getShorts(lang) : m.SHORTS).find((s) => s.id === id) : null;
    if (isShort && !short) throw new Error(`Composition inconnue : ${id}`);
    if (!isShort && !['V01', 'V01_EN'].includes(id)) throw new Error(`Composition inconnue : ${id}`);
    const props = short ? {...short, lang} : {lang};
    const config = {id, fps: 30, width: isShort ? 1080 : 1920, height: isShort ? 1920 : 1080,
      durationInFrames: short ? short.to - short.from + m.SHORT_END : m.durationFor ? m.durationFor(lang) : m.V01_DURATION,
      defaultProps: props, props};
    if (!Number.isInteger(frame) || frame < 0 || frame >= config.durationInFrames) throw new Error(`Frame hors composition : ${id}:${frame}`);
    const providers = [
      [Internals.CompositionManager, {compositions: [config], canvasContent: {type: 'composition', compositionId: id}, currentCompositionMetadata: config}],
      [Internals.TimelineContext, {frame: {[id]: frame}, playing: false, rootId: 'root', imperativePlaying: {current: false}}],
      [Internals.CanUseRemotionHooks, true],
    ];
    let tree = React.createElement(short ? m.Short : m.V01, props);
    for (const [context, value] of providers.reverse()) tree = React.createElement(context.Provider, {value}, tree);
    return {markup: renderToStaticMarkup(tree), ...config};
  };
}

const fontCSS = () => [
  ['Garamond', 'EBGaramond.ttf', 'normal', '400 800'], ['Garamond', 'EBGaramond-Italic.ttf', 'italic', '400 800'],
  ['Plex Mono', 'PlexMono-Light.ttf', 'normal', '300'], ['Plex Mono', 'PlexMono-Regular.ttf', 'normal', '400'],
  ['Plex Mono', 'PlexMono-Medium.ttf', 'normal', '500'], ['Amiri Quran', 'AmiriQuran-Regular.ttf', 'normal', '400'],
  ['Amiri', 'Amiri-Regular.ttf', 'normal', '400'],
].map(([family, file, style, weight]) => `@font-face{font-family:'${family}';src:url('${pathToFileURL(path.resolve('public/fonts', file)).href}');font-style:${style};font-weight:${weight}}`).join('\n');

export async function htmlStills({outDir, pairs, composition, sourceRoot, clean, no3d}) {
  const render = await prepareStills({sourceRoot, outDir, clean, no3d});
  const shots = [];
  for (const {name, frame} of pairs) {
    const shot = render(composition, frame);
    const css = `${fontCSS()} *{box-sizing:border-box} body{margin:0;background:#25221e} .frame{position:relative;width:${shot.width}px;height:${shot.height}px;overflow:hidden;flex:none}`;
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${name} · ${frame}</title><style>${css}</style></head><body><div class="frame">${shot.markup}</div></body></html>`;
    await fs.writeFile(path.join(outDir, `${name}.html`), html);
    shots.push({name, frame, ...shot});
  }
  const scale = 0.3;
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${composition} · contrôle en images fixes</title><style>${fontCSS()}
  *{box-sizing:border-box}body{margin:20px;background:#24211e;color:#eee;font:15px system-ui}.grid{display:flex;flex-wrap:wrap;gap:20px}.cell{flex:none}.frame{position:relative;overflow:hidden}.inner{position:relative;transform-origin:0 0;transform:scale(${scale})}a{color:#eee}</style></head><body>
  <p>${composition} — images fixes HTML, sans audio. Vérification PNG Remotion encore nécessaire.</p><div class="grid">${shots.map((s) => `<div class="cell"><p><a href="${s.name}.html">${s.name} · ${s.frame}</a></p><div class="frame" style="width:${s.width * scale}px;height:${s.height * scale}px"><div class="inner" style="width:${s.width}px;height:${s.height}px">${s.markup}</div></div></div>`).join('')}</div></body></html>`;
  await fs.writeFile(path.join(outDir, 'index.html'), html);
  return shots;
}
