import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { toGLB } from './glb.mjs';
import { renderViews } from './views.mjs';

/* Breaks a code-built model in known ways and scores every break against its concept sheet, so the
   pass bar is set from evidence for this asset rather than assumed.

     node calibrate.mjs <model-module> <concept.json> <out-dir> [--parts a,b] [--shrink 0.85]
                        [--outline 0] [--gate side,front] [--size 1024]

   Faults: every named child of the model's root shrunk about its own centre (<name>-small) and
   removed (<name>-gone), and the whole model 10% long, narrow and low. A fault is caught when any
   gated view fails the bar. Prints a table, writes <out-dir>/calibration.json, and writes the
   tightest per-view bar that still passes the good model to <out-dir>/bar.json, with how many
   faults it catches. Gate later rounds with compare.py --bar <out-dir>/bar.json.            */

const HERE = dirname(fileURLToPath(import.meta.url));
const BAR = { min_iou: 0.94, max_size: 0.03, max_p95: 0.03, max_colour: 1 };

const passes = (m, bar) =>
  m.iou >= bar.min_iou && Math.max(Math.abs(m.w_err), Math.abs(m.h_err)) <= bar.max_size && m.edge_p95 <= bar.max_p95 &&
  m.colour_miss <= bar.max_colour;

function faults(build, args, parts, shrink) {
  const list = [{ fault: 'good', make: (o) => o }];
  for (const name of parts) {
    list.push({ fault: `${name}-small`, make: (o, THREE) => {
      const part = o.getObjectByName(name);
      const centre = new THREE.Box3().setFromObject(part).getCenter(new THREE.Vector3());
      const local = part.parent.worldToLocal(centre.clone());
      part.position.sub(local).multiplyScalar(shrink).add(local);
      part.scale.multiplyScalar(shrink);
      return o;
    } });
    list.push({ fault: `${name}-gone`, make: (o) => { o.getObjectByName(name).removeFromParent(); return o; } });
  }
  for (const [fault, axis, k] of [['long', 'z', 1.1], ['narrow', 'x', 0.9], ['low', 'y', 0.9]]) {
    list.push({ fault, make: (o) => { o.scale[axis] *= k; return o; } });
  }
  return list.map((f) => ({ ...f, build: async (THREE) => f.make(await build(args), THREE) }));
}

function score(concept, renders, outline) {
  const run = spawnSync('python', ['-I', join(HERE, 'compare.py'), concept, renders, join(renders, 'out'), '--outline', String(outline)],
    { encoding: 'utf8' });
  if (run.status === null || /Traceback|SystemExit|can't read/.test(run.stderr)) throw new Error(run.stderr || run.stdout);
  return JSON.parse(readFileSync(join(renders, 'out', 'report.json'), 'utf8')).views;
}

export async function calibrate(modulePath, concept, outDir, { parts, shrink = 0.85, outline = 0, gate, size = 1024 } = {}) {
  const file = resolve(modulePath);
  const build = (await import(pathToFileURL(file).href)).default;
  const { createRequire } = await import('node:module');
  // The ESM build beside the CJS one that require-resolution finds: the copy the model itself imports.
  const THREE = await import(pathToFileURL(join(dirname(createRequire(file).resolve('three')), 'three.module.js')).href);
  const root = await build();
  const names = root.children.map((c) => c.name).filter(Boolean);
  const twice = [...new Set(names.filter((n, i) => names.indexOf(n) !== i))];
  // A fault can only break a part it can find by name, and a repeated name finds the first one only.
  if (twice.length) console.warn(`parts sharing a name, so only the first of each is tested: ${twice.join(', ')}`);
  const named = parts ?? [...new Set(names)];
  const views = Object.keys(JSON.parse(readFileSync(concept, 'utf8')).views);
  const gated = gate ?? views;
  const results = [];
  for (const f of faults(build, undefined, named, shrink)) {
    const dir = join(outDir, f.fault);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, 'model.glb'), await toGLB(await f.build(THREE), file));
    await renderViews(join(dir, 'model.glb'), dir, { size, views });
    const scored = score(concept, dir, outline);
    const worst = {
      iou: Math.min(...gated.map((v) => scored[v].iou)),
      size: Math.max(...gated.map((v) => Math.max(Math.abs(scored[v].w_err), Math.abs(scored[v].h_err)))),
      p95: Math.max(...gated.map((v) => scored[v].edge_p95)),
      colour: Math.max(...gated.map((v) => scored[v].colour_miss)),
    };
    results.push({ fault: f.fault, views: scored, worst });
  }
  const [good, ...broken] = results;
  const caughtBy = (barFor) => (r) => gated.some((v) => !passes(r.views[v], barFor(v)));
  // Per view, just inside the good model's own numbers: as tight as a bar can be while the good model
  // passes. Per view because the views' baselines differ (colour miss runs higher where the concept
  // shows more shading or interior detail). From here on it catches any regression of that size.
  const floor3 = (x) => Math.floor(x * 1000) / 1000;
  const ceil3 = (x) => Math.ceil(x * 1000) / 1000;
  const suggested = Object.fromEntries(gated.map((v) => {
    const g = good.views[v];
    return [v, {
      min_iou: floor3(g.iou - 0.005), max_size: ceil3(Math.max(Math.abs(g.w_err), Math.abs(g.h_err)) + 0.005),
      max_p95: ceil3(g.edge_p95 + 0.002), max_colour: ceil3(g.colour_miss + 0.02),
    }];
  }));
  const report = {
    gate: gated, default: BAR, suggested,
    good: { ...good, pass: !caughtBy(() => BAR)(good) },
    faults: broken.map((r) => ({ ...r, caught: caughtBy(() => BAR)(r), caughtBySuggested: caughtBy((v) => suggested[v])(r) })),
  };
  writeFileSync(join(outDir, 'calibration.json'), JSON.stringify(report, null, 2) + '\n');
  writeFileSync(join(outDir, 'bar.json'), JSON.stringify(suggested, null, 2) + '\n');
  return report;
}

// Real paths: ~/.claude/skills reaches this script through a link that argv[1] keeps.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  const args = process.argv.slice(2);
  const flag = (name) => (args.includes(`--${name}`) ? args[args.indexOf(`--${name}`) + 1] : undefined);
  const [modulePath, concept, out] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
  if (!modulePath || !concept || !out) {
    console.error('usage: node calibrate.mjs <model-module> <concept.json> <out-dir> [--parts a,b] [--shrink 0.85] [--outline 0] [--gate side,front] [--size 1024]');
    process.exit(2);
  }
  const r = await calibrate(modulePath, concept, out, {
    parts: flag('parts')?.split(','), shrink: Number(flag('shrink') ?? 0.85), outline: Number(flag('outline') ?? 0),
    gate: flag('gate')?.split(','), size: Number(flag('size') ?? 1024),
  });
  const row = (name, w, mark) => console.log(`${name.padEnd(28)} IoU ${w.iou.toFixed(3)}  size ${(100 * w.size).toFixed(1).padStart(5)}%  p95 ${(100 * w.p95).toFixed(1).padStart(4)}%  colour ${(100 * w.colour).toFixed(1).padStart(4)}%  ${mark}`);
  console.log(`worst gated view (${r.gate.join(', ')}) per fault; "caught" means a gated view fails the bar`);
  row('good', r.good.worst, r.good.pass ? 'passes the default bar' : 'FAILS the default bar');
  for (const f of r.faults) row(f.fault, f.worst, `${f.caught ? 'caught' : 'MISSED'} by default, ${f.caughtBySuggested ? 'caught' : 'MISSED'} by suggested`);
  const n = (k) => r.faults.filter((f) => f[k]).length;
  console.log(`\ndefault bar (--min-iou ${r.default.min_iou} --max-size ${r.default.max_size} --max-p95 ${r.default.max_p95}) catches ${n('caught')} of ${r.faults.length}`);
  console.log(`suggested per-view bar catches ${n('caughtBySuggested')} of ${r.faults.length}:`);
  for (const [v, b] of Object.entries(r.suggested)) {
    console.log(`  ${v.padEnd(6)} IoU >= ${b.min_iou}, size <= ${b.max_size}, p95 <= ${b.max_p95}, colour miss <= ${b.max_colour}`);
  }
  const missed = r.faults.filter((f) => !f.caughtBySuggested).map((f) => f.fault);
  if (missed.length) console.log(`no view sees: ${missed.join(', ')} (check these by eye, or build mirrored parts from one function)`);
  console.log(`wrote ${join(out, 'calibration.json')} and ${join(out, 'bar.json')}; gate with compare.py ... --bar ${join(out, 'bar.json')}`);
}
