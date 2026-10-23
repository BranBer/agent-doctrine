import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { parseArgs } from 'node:util';

/* Fails on a raw value - an arbitrary Tailwind value or a hex colour - used in
   two component folders, the threshold in react-doctrine 7. Heavy use inside
   one folder is printed as a note, not a failure.

     node repeats.mjs [srcDir] [--skip styles] [--roots components,sections]

   A component and its nested children count as one folder: the first folder
   under any of --roots. The stylesheet folder is where values belong, so it
   is skipped by default. */
const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    skip: { type: 'string', multiple: true, default: ['styles'] },
    roots: { type: 'string', default: 'components,sections,features,pages' },
  },
});
const SRC = positionals[0] ?? 'src';
const ROOTS = values.roots.split(',');
const ARBITRARY = /(?:^|[\s"'`:])((?:min|max)-\[\d+px\]|[a-z-]+-\[\d+(?:px|%)\])/g;
const HEX = /#[0-9a-fA-F]{6}\b/g;

const walk = async (dir) => {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (values.skip.some((s) => path.replaceAll('\\', '/').includes(`/${s}`))) continue;
    if (entry.isDirectory()) out.push(...(await walk(path)));
    else if (/\.(tsx?|jsx?|css)$/.test(entry.name)) out.push(path);
  }
  return out;
};

const folderOf = (file) => {
  const parts = file.replaceAll('\\', '/').split('/');
  const i = parts.findIndex((p) => ROOTS.includes(p));
  return i === -1 ? parts.slice(0, -1).join('/') : parts.slice(0, i + 2).join('/');
};

const seen = new Map();
for (const file of await walk(SRC)) {
  const src = await readFile(file, 'utf8');
  const hits = [...[...src.matchAll(ARBITRARY)].map((m) => m[1]), ...[...src.matchAll(HEX)].map((m) => m[0])];
  for (const hit of hits) {
    const entry = seen.get(hit) ?? { folders: new Set(), uses: 0 };
    entry.folders.add(folderOf(file));
    entry.uses += 1;
    seen.set(hit, entry);
  }
}

const offenders = [...seen]
  .filter(([, h]) => h.folders.size >= 2)
  .sort((a, b) => b[1].folders.size - a[1].folders.size || b[1].uses - a[1].uses);
const dense = [...seen].filter(([, h]) => h.folders.size === 1 && h.uses >= 5);

for (const [hit, h] of offenders) {
  console.log(
    `${hit.padEnd(24)} ${h.folders.size} folder(s), ${h.uses} use(s)  ` +
      [...h.folders].map((f) => f.split('/').slice(-2).join('/')).join(', '),
  );
}
for (const [hit, h] of dense) console.log(`note: ${hit} x${h.uses} in ${[...h.folders][0].split('/').at(-1)}`);
console.log(offenders.length ? `\n${offenders.length} value(s) have earned a name` : 'clean');
process.exit(offenders.length ? 1 : 0);
