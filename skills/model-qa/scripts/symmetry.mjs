import { spawnSync } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderViews } from './views.mjs';

/* Checks a bilaterally symmetric model against its own mirror image about X = 0.

     node symmetry.mjs <model.glb> <out-dir> [--size 1024] [--min-iou 0.995] [--tol 0.005]

   The silhouette scores against a concept compare whole views, so a small part off the centre line
   passes them: a roof rack 56 mm to one side did, because the sheet it was measured from was drawn
   off-centre in one view. This renders the front and top views without the parts the model declares
   one-sided (userData.oneSided on the part, which glTF carries as the node's extras), then
   compare.py symmetry mirrors both renders, scores the mirrored silhouette's IoU and checks every
   named part's box: twins (*-left / *-right, *_L / *_R) must mirror each other, and every other
   part must be centred on X = 0. Prints a table and exits 1 when the model is not symmetric.

   Its renders are made for this check alone (aliased, one-sided parts left out), so they and
   symmetry.json and symmetry.png go in a symmetry/ folder of out-dir, never over the scoring
   renders that may share it.                                                                     */

const HERE = dirname(fileURLToPath(import.meta.url));

// Real paths: ~/.claude/skills reaches this script through a link that argv[1] keeps.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  const args = process.argv.slice(2);
  const flag = (name) => (args.includes(`--${name}`) ? args[args.indexOf(`--${name}`) + 1] : undefined);
  const [model, out] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
  if (!model || !out) {
    console.error('usage: node symmetry.mjs <model.glb> <out-dir> [--size 1024] [--min-iou 0.995] [--tol 0.005]');
    process.exit(2);
  }
  // Hard edges, so a symmetric model rasterises symmetrically (see renderViews)
  const dir = join(out, 'symmetry');
  await renderViews(model, dir, { size: Number(flag('size') ?? 1024), views: ['front', 'top'], dropOneSided: true, antialias: false });
  const limits = ['min-iou', 'tol'].flatMap((name) => (flag(name) === undefined ? [] : [`--${name}`, flag(name)]));
  const run = spawnSync('python', ['-I', join(HERE, 'compare.py'), 'symmetry', dir, ...limits], { stdio: 'inherit' });
  process.exit(run.status ?? 1);
}
