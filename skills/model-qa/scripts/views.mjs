import { mkdirSync, realpathSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

/* Orthographic renders of a GLB from the views a concept sheet shows.

     node views.mjs <model.glb> <out-dir> [--size 1024] [--views side,front,back,top,hero] [--hero 1,0.6,1.1]

   The model is read in the glTF frame: +Y up, nose toward +Z. Every view uses
   one shared scale (pxPerUnit in views.json), so proportions between views are
   real, the way a blueprint's are:

     side   from the model's left (+X): nose points left, length across, height up
     front  from +Z: width across, height up
     back   from -Z: width across, height up
     top    from +Y: nose points left, length across, width up
     hero   a perspective three-quarter view from the front left, above; for
            people to judge, never scored (perspective has no shared scale).
            --hero x,y,z sets its direction, to match a hero concept's angle

   Each view writes <view>.png (lit by a fixed top-left key light, for looking
   at) and <view>.flat.png (unlit base colours, for colour checks), both on a
   transparent background, plus views.json. views.json also holds the model's
   box and every named part's box (the named children of the model's root),
   with the parts the model declares one-sided (userData.oneSided, carried in
   glTF as a node's extras). It runs in Playwright's own headless Chromium,
   never the user's browser.                                                 */

const HERE = dirname(fileURLToPath(import.meta.url));
const THREE_DIR = join(HERE, 'node_modules', 'three');
const ORIGIN = 'http://model-qa.local';

export const VIEWS = {
  side: { dir: [1, 0, 0], up: [0, 1, 0] },
  front: { dir: [0, 0, 1], up: [0, 1, 0] },
  back: { dir: [0, 0, -1], up: [0, 1, 0] },
  top: { dir: [0, 1, 0], up: [-1, 0, 0] },
  hero: { dir: [1, 0.6, 1.1], up: [0, 1, 0], perspective: true },
};

const PAGE = `<!doctype html>
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// The share of the frame the model's longest side fills.
const FILL = 0.8;

const boxOf = (object) => {
  const b = new THREE.Box3().setFromObject(object);
  return { min: b.min.toArray(), max: b.max.toArray(), centre: b.getCenter(new THREE.Vector3()).toArray() };
};

window.renderViews = async (size, views, { dropOneSided = false, antialias = true } = {}) => {
  const root = (await new GLTFLoader().loadAsync('/model.glb')).scene;
  // The model's own root: the scene wraps it, and an exported group wraps its parts.
  let top = root;
  while (top.children.length === 1 && !top.children[0].isMesh) top = top.children[0];
  // A part is a child named in the file: the loader keeps that name in userData.name, and names the rest itself (mesh_0).
  const named = top.children.filter((c) => c.userData.name !== undefined);
  const parts = Object.fromEntries(named.map((c) => [c.name, { ...boxOf(c), oneSided: !!c.userData.oneSided }]));
  if (dropOneSided) top.children.filter((c) => c.userData.oneSided).forEach((c) => c.removeFromParent());
  const box = new THREE.Box3().setFromObject(root);
  const centre = box.getCenter(new THREE.Vector3());
  const dims = box.getSize(new THREE.Vector3());
  const longest = Math.max(dims.x, dims.y, dims.z);
  const pxPerUnit = (size * FILL) / longest;
  const half = size / 2 / pxPerUnit;

  const renderer = new THREE.WebGLRenderer({ antialias, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(size, size);
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  scene.add(root, new THREE.HemisphereLight(0xffffff, 0x9aa3b5, 1.4));
  const ortho = new THREE.OrthographicCamera(-half, half, half, -half, 0.01, longest * 10);
  const FOV = 30;
  const perspective = new THREE.PerspectiveCamera(FOV, 1, 0.01, longest * 20);
  for (const camera of [ortho, perspective]) {
    const key = new THREE.DirectionalLight(0xffffff, 2.0);
    key.position.set(-1, 1.2, 1);
    camera.add(key, key.target);
    key.target.position.set(0, 0, -1);
    scene.add(camera);
  }

  const meshes = [];
  root.traverse((o) => o.isMesh && meshes.push(o));
  const triangles = meshes.reduce((n, m) => n + (m.geometry.index ?? m.geometry.attributes.position).count / 3, 0);
  const flat = new Map(meshes.map((m) => [m, [m.material].flat().map((mat) => new THREE.MeshBasicMaterial({
    color: mat.color, vertexColors: mat.vertexColors, map: mat.map ?? null, side: mat.side,
    transparent: mat.transparent, opacity: mat.opacity,
  }))]));

  const images = {};
  for (const [name, v] of Object.entries(views)) {
    const camera = v.perspective ? perspective : ortho;
    // Orthographic: well clear of the model. Perspective: the bounding sphere fits the frame from any
    // direction, which framing on the longest side does not (a cube's diagonal is 1.73 times its side).
    const radius = dims.length() / 2;
    const distance = v.perspective ? radius / Math.sin(THREE.MathUtils.degToRad(FOV / 2)) / FILL : longest * 3;
    camera.position.copy(centre).addScaledVector(new THREE.Vector3(...v.dir).normalize(), distance);
    camera.up.set(...v.up);
    camera.lookAt(centre);
    renderer.render(scene, camera);
    const lit = renderer.domElement.toDataURL('image/png');
    const own = meshes.map((m) => m.material);
    meshes.forEach((m) => { const f = flat.get(m); m.material = Array.isArray(m.material) ? f : f[0]; });
    renderer.render(scene, camera);
    const unlit = renderer.domElement.toDataURL('image/png');
    meshes.forEach((m, i) => { m.material = own[i]; });
    images[name] = { lit, unlit };
  }
  return {
    pxPerUnit, dims: { x: dims.x, y: dims.y, z: dims.z }, box: { min: box.min.toArray(), max: box.max.toArray() },
    parts, dropped: dropOneSided ? Object.keys(parts).filter((n) => parts[n].oneSided) : [],
    triangles, meshes: meshes.length, images,
  };
};
window.ready = true;
</script>`;

/**
 * dropOneSided renders the model without the parts it declares one-sided, and antialias false renders hard edges, for
 * the symmetry check: multisampling's sample pattern is not mirror-symmetric, so it puts a symmetric model's two edges
 * a pixel apart, where without it a pixel is in exactly when its centre is.
 */
export async function renderViews(modelPath, outDir, { size = 1024, views = Object.keys(VIEWS), hero, dropOneSided = false, antialias = true } = {}) {
  const unknown = views.filter((v) => !VIEWS[v]);
  if (unknown.length) throw new Error(`unknown view ${unknown.join(', ')}; known: ${Object.keys(VIEWS).join(', ')}`);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.route(`${ORIGIN}/**`, (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path === '/') return route.fulfill({ contentType: 'text/html', body: PAGE });
      if (path === '/model.glb') return route.fulfill({ path: resolve(modelPath), contentType: 'model/gltf-binary' });
      if (path.startsWith('/three/')) {
        return route.fulfill({ path: join(THREE_DIR, path.slice('/three/'.length)), contentType: 'text/javascript' });
      }
      return route.fulfill({ status: 404, body: 'not found' });
    });
    await page.goto(`${ORIGIN}/`);
    await page.waitForFunction(() => window.ready || false, null, { timeout: 30_000 }).catch(() => {
      throw new Error(`render page did not start: ${errors.join('; ') || 'no error reported'}`);
    });
    const picked = Object.fromEntries(views.map((v) => [v, v === 'hero' && hero ? { ...VIEWS.hero, dir: hero } : VIEWS[v]]));
    const result = await page.evaluate(([s, v, o]) => window.renderViews(s, v, o), [size, picked, { dropOneSided, antialias }]);
    mkdirSync(outDir, { recursive: true });
    const png = (dataUrl) => Buffer.from(dataUrl.split(',', 2)[1], 'base64');
    for (const [name, { lit, unlit }] of Object.entries(result.images)) {
      writeFileSync(join(outDir, `${name}.png`), png(lit));
      writeFileSync(join(outDir, `${name}.flat.png`), png(unlit));
    }
    const meta = {
      model: modelPath, size, pxPerUnit: result.pxPerUnit, dims: result.dims, box: result.box,
      triangles: result.triangles, meshes: result.meshes, views: picked, parts: result.parts, dropped: result.dropped,
    };
    writeFileSync(join(outDir, 'views.json'), JSON.stringify(meta, null, 2) + '\n');
    return meta;
  } finally {
    await browser.close();
  }
}

// Compare real paths: ~/.claude/skills reaches these scripts through a link, and argv[1] keeps
// the link's path while import.meta.url resolves it.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  const args = process.argv.slice(2);
  const flag = (name, fallback) => (args.includes(`--${name}`) ? args[args.indexOf(`--${name}`) + 1] : fallback);
  const [model, out] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
  if (!model || !out) {
    console.error('usage: node views.mjs <model.glb> <out-dir> [--size 1024] [--views side,front,back,top,hero] [--hero x,y,z]');
    process.exit(2);
  }
  const meta = await renderViews(model, out, {
    size: Number(flag('size', 1024)),
    views: flag('views', Object.keys(VIEWS).join(',')).split(','),
    hero: flag('hero', undefined)?.split(',').map(Number),
  });
  const { x, y, z } = meta.dims;
  console.log(`wrote ${Object.keys(meta.views).join(', ')} to ${out} (model ${x.toFixed(3)} wide x ${y.toFixed(3)} tall x ${z.toFixed(3)} long, ${meta.triangles} triangles in ${meta.meshes} meshes, ${meta.pxPerUnit.toFixed(2)} px/unit)`);
}
