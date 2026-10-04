// Bundle sans cache dans node_modules (lien partagé en lecture seule).
// node tools/bundle_local.mjs [out/bundle]
import {bundle} from '@remotion/bundler';
import path from 'node:path';
const outDir = path.resolve(process.argv[2] ?? 'out/bundle');
console.log(await bundle({entryPoint: path.resolve('src/index.ts'), outDir, enableCaching: false}));
