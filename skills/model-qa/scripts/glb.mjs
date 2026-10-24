import { mkdirSync, realpathSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

/* Exports a code-built three.js model to GLB, so views.mjs can render it.

     node glb.mjs <model-module> <out.glb> [--export name] [--args '{"json":1}']

   The module's export (default unless --export) is a function returning an
   Object3D, or a promise of one; --args is passed to it as one parsed value.
   GLTFExporter is taken from the three that the module itself resolves, so the
   exporter and the model never come from two different copies of three.      */

// GLTFExporter's binary path reads blobs with FileReader, which Node lacks.
globalThis.FileReader ??= class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then((result) => { this.result = result; this.onloadend?.(); });
  }
};

export async function toGLB(object, from) {
  const exporterPath = createRequire(from).resolve('three/examples/jsm/exporters/GLTFExporter.js');
  const { GLTFExporter } = await import(pathToFileURL(exporterPath).href);
  const buffer = await new GLTFExporter().parseAsync(object, { binary: true });
  return Buffer.from(buffer);
}

// Compare real paths: ~/.claude/skills reaches these scripts through a link, and argv[1] keeps
// the link's path while import.meta.url resolves it.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  const args = process.argv.slice(2);
  const flag = (name) => (args.includes(`--${name}`) ? args[args.indexOf(`--${name}`) + 1] : undefined);
  const [modulePath, out] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
  if (!modulePath || !out) {
    console.error('usage: node glb.mjs <model-module> <out.glb> [--export name] [--args json]');
    process.exit(2);
  }
  const file = resolve(modulePath);
  const build = (await import(pathToFileURL(file).href))[flag('export') ?? 'default'];
  if (typeof build !== 'function') {
    console.error(`${modulePath} has no function export "${flag('export') ?? 'default'}"`);
    process.exit(2);
  }
  const object = await build(flag('args') === undefined ? undefined : JSON.parse(flag('args')));
  mkdirSync(dirname(resolve(out)), { recursive: true });
  writeFileSync(out, await toGLB(object, file));
  console.log(`wrote ${out}`);
}
