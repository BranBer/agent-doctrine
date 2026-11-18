/* Contact sheet of an animated GLB: one row per clip, four frames across it, to look for collapsed
   limbs, a scaled head or torn cloth after a retarget.

     node clips.mjs <animated.glb> <out.png> [--front x|z] [--cols 4] [--clip name]

   --cols sets the frames per row; --clip shows one clip only, to find a moment inside a long one.
   Prints each clip's name, length and track count. --front says which axis the model faces (Tripo: x).
   Uses model-qa's three and Playwright, in Playwright's own headless Chromium.                        */
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const QA = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'model-qa', 'scripts');
const { chromium } = createRequire(join(QA, 'x.js'))('playwright');
const ORIGIN = 'http://model-gen.local';
const CELL = 320;

const PAGE = `<!doctype html>
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
window.sheet = async (cell, front, cols, only) => {
  const gltf = await new GLTFLoader().loadAsync('/model.glb');
  const scene = new THREE.Scene();
  scene.add(gltf.scene, new THREE.HemisphereLight(0xffffff, 0x554444, 2.2));
  const box = new THREE.Box3().setFromObject(gltf.scene);
  const c = box.getCenter(new THREE.Vector3()), r = box.getSize(new THREE.Vector3()).length() * 0.5;
  const cam = new THREE.OrthographicCamera(-r, r, r, -r, 0.01, 100);
  const dir = front === 'x' ? new THREE.Vector3(1, 0.35, 0.8) : new THREE.Vector3(0.8, 0.35, 1);
  cam.position.copy(c).addScaledVector(dir.normalize(), 10); cam.lookAt(c);
  const clips = gltf.animations.filter((k) => !only || k.name === only);
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(cell * cols, cell * clips.length); renderer.setClearColor(0xdddddd); renderer.setScissorTest(true);
  const mixer = new THREE.AnimationMixer(gltf.scene);
  clips.forEach((clip, row) => {
    mixer.stopAllAction(); const action = mixer.clipAction(clip); action.play();
    for (let i = 0; i < cols; i++) {
      mixer.setTime(clip.duration * i / cols);
      const y = cell * (clips.length - 1 - row);
      renderer.setViewport(i * cell, y, cell, cell); renderer.setScissor(i * cell, y, cell, cell);
      renderer.render(scene, cam);
    }
  });
  document.body.append(renderer.domElement);
  return clips.map((k) => ({ name: k.name, seconds: +k.duration.toFixed(2), tracks: k.tracks.length }));
};
</script>`;

const args = process.argv.slice(2);
const [model, out] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!model || !out) { console.error('usage: node clips.mjs <animated.glb> <out.png> [--front x|z]'); process.exit(1); }
const flag = (name, fallback) => (args.includes(name) ? args[args.indexOf(name) + 1] : fallback);
const front = flag('--front', 'x');

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--mute-audio'] });
const page = await browser.newPage();
await page.route(`${ORIGIN}/**`, (route) => {
  const path = new URL(route.request().url()).pathname;
  if (path === '/') return route.fulfill({ contentType: 'text/html', body: PAGE });
  if (path === '/model.glb') return route.fulfill({ contentType: 'model/gltf-binary', body: readFileSync(model) });
  return route.fulfill({ contentType: 'text/javascript', body: readFileSync(join(QA, 'node_modules', path)) });
});
await page.goto(ORIGIN + '/');
await page.waitForFunction(() => window.sheet);
const clips = await page.evaluate(([cell, f, cols, only]) => window.sheet(cell, f, cols, only), [CELL, front, Number(flag('--cols', 4)), flag('--clip', null)]);
if (!clips.length) { console.error('no animation clips in', model); await browser.close(); process.exit(1); }
writeFileSync(out, await page.locator('canvas').screenshot());
await browser.close();
for (const k of clips) console.log(`${k.name}  ${k.seconds}s  ${k.tracks} tracks`);
console.log('wrote', out);
