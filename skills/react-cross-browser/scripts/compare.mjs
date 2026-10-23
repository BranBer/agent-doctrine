import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

/* Holds one engine to the other across everything `sweep.mjs` recorded, one
   state at a time, and reports content faults in either engine as well - a
   broken image is a failure whichever engine it is broken in.

   Per state: the same words, the same images all decoded, the same font faces
   loaded, nothing past the window, no link without a destination, no errors,
   the same boxes to within a tolerance, and no *clustered* pixel difference
   in either screenshot.

   **The raw pixel difference is not the signal.** The two engines rasterise
   glyphs differently, so every letter edge differs - reliably 1-3% of a page
   that is completely correct. What matters is whether the difference
   clusters: eroding the diff with a 9x9 window clears text (body strokes are
   about 2px) while anything wider survives - a mask that never painted, a
   gradient that banded, a block that moved. Read the map before believing a
   number.

     node compare.mjs [--dir qa/sweep] [--base chromium] [--other webkit]
                      [--tolerance 1.5] [--cluster 0.05] [--fonts proxima]   */

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};
const DIR = flag('dir', 'qa/sweep');
const BASE = flag('base', 'chromium');
const OTHER = flag('other', 'webkit');
const TOLERANCE = Number(flag('tolerance', 1.5));
const CLUSTER_FAIL = Number(flag('cluster', 0.05));
const NEEDED_FONTS = (flag('fonts') ?? '').split(',').filter(Boolean);

const DIFF_CHANNEL = 24;
/* The erosion window. 9x9 clears body text and a headline up to about 40px;
   a phone screen carrying 48px display type needs a wider one, because a
   7px stroke survives 9x9 and the map then traces letters at a percentage
   that looks like a defect. Raise it rather than raising `--cluster`. */
const CLUSTER_WINDOW = Number(flag('erode', 4));
const CLUSTER_MIN = Math.round((2 * CLUSTER_WINDOW + 1) ** 2 * 0.74);

const [A, B] = await Promise.all(
  [BASE, OTHER].map((n) => readFile(`${DIR}/${n}.json`, 'utf8').then(JSON.parse)),
);

const firstDiff = (a, b) => {
  let i = 0;
  while (i < a.length && a[i] === b[i]) i++;
  return `"...${a.slice(Math.max(0, i - 30), i + 40)}..." vs "...${b.slice(Math.max(0, i - 30), i + 40)}..."`;
};

const browser = await chromium.launch();
const page = await browser.newPage();
await mkdir(`${DIR}/diff`, { recursive: true });

const clustered = async (file) => {
  const [a, b] = await Promise.all(
    [BASE, OTHER].map((e) => readFile(`${DIR}/${e}/${file}`).then((f) => f.toString('base64'))),
  );
  const out = await page.evaluate(
    async ([x, y, channel, radius, minNeighbours]) => {
      const load = (b64) =>
        new Promise((res) => {
          const img = new Image();
          img.onload = () => res(img);
          img.src = 'data:image/png;base64,' + b64;
        });
      const [ia, ib] = await Promise.all([load(x), load(y)]);
      if (ia.width !== ib.width || ia.height !== ib.height) {
        return { size: [ia.width, ia.height, ib.width, ib.height] };
      }
      const pixels = (img) => {
        const c = new OffscreenCanvas(img.width, img.height);
        const ctx = c.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return ctx.getImageData(0, 0, img.width, img.height).data;
      };
      const [da, db] = [pixels(ia), pixels(ib)];
      const { width: w, height: h } = ia;
      const mask = new Uint8Array(w * h);
      let raw = 0;
      for (let p = 0; p < mask.length; p++) {
        const i = p * 4;
        const d = Math.max(
          Math.abs(da[i] - db[i]),
          Math.abs(da[i + 1] - db[i + 1]),
          Math.abs(da[i + 2] - db[i + 2]),
        );
        if (d > channel) {
          mask[p] = 1;
          raw++;
        }
      }
      let hits = 0;
      let box = [Infinity, Infinity, -1, -1];
      for (let py = radius; py < h - radius; py++) {
        for (let px = radius; px < w - radius; px++) {
          if (!mask[py * w + px]) continue;
          let n = 0;
          for (let dy = -radius; dy <= radius; dy++) {
            for (let dx = -radius; dx <= radius; dx++) n += mask[(py + dy) * w + px + dx];
          }
          if (n >= minNeighbours) {
            hits++;
            box = [Math.min(box[0], px), Math.min(box[1], py), Math.max(box[2], px), Math.max(box[3], py)];
          }
        }
      }
      const total = w * h;
      const result = {
        raw: Math.round((raw / total) * 10000) / 100,
        clustered: Math.round((hits / total) * 10000) / 100,
        box: box[2] < 0 ? null : box,
      };
      if (hits / total > 0.0005) {
        const canvas = new OffscreenCanvas(w, h);
        const ctx = canvas.getContext('2d');
        const img = ctx.createImageData(w, h);
        for (let p = 0; p < mask.length; p++) {
          const i = p * 4;
          const g = 235 + Math.round(da[i] * 0.08);
          img.data.set(mask[p] ? [255, 0, 255, 255] : [g, g, g, 255], i);
        }
        ctx.putImageData(img, 0, 0);
        const blob = await canvas.convertToBlob({ type: 'image/png' });
        result.png = Array.from(new Uint8Array(await blob.arrayBuffer()));
      }
      return result;
    },
    [a, b, DIFF_CHANNEL, CLUSTER_WINDOW, CLUSTER_MIN],
  );
  if (out.png) {
    await writeFile(`${DIR}/diff/${file}`, Buffer.from(out.png));
    delete out.png;
  }
  return out;
};

const report = {};
const notes = [];
let failures = 0;
let worstPixels = { v: 0 };

for (const key of Object.keys(A)) {
  const a = A[key];
  const b = B[key];
  const [width, state] = key.split(' ');
  const problems = [];
  if (!b) {
    problems.push(`not reached in ${OTHER}`);
  } else {
    if (a.text !== b.text) problems.push(`words differ: ${firstDiff(a.text, b.text)}`);
    if (a.images !== b.images) problems.push(`${a.images} images in ${BASE}, ${b.images} in ${OTHER}`);
    for (const [name, d] of [[BASE, a], [OTHER, b]]) {
      if (d.broken.length) problems.push(`${name}: images not decoded - ${d.broken.join(', ')}`);
      if (d.overflow > 0 || d.past.length) problems.push(`${name}: past the window - ${d.overflow}px ${d.past.join('; ')}`);
      if (d.hrefless) problems.push(`${name}: ${d.hrefless} links without an href`);
      if (d.errors.length) problems.push(`${name}: ${d.errors.join(' | ')}`);
      for (const want of NEEDED_FONTS) {
        if (!d.fonts.some((f) => f.toLowerCase().startsWith(want.toLowerCase()))) {
          problems.push(`${name}: loaded no ${want}`);
        }
      }
    }
    /* Which *weights* have loaded is each engine's business - it follows
       what has been rendered and how eagerly the engine fetches faces - so
       only a whole family present in one and absent in the other is a fault.
       A missing weight is worth seeing, and printed, but does not fail. */
    const families = (d) => [...new Set(d.fonts.map((f) => f.replace(/ \d+$/, '')))].sort();
    const [fa, fb] = [families(a), families(b)];
    if (fa.join() !== fb.join()) problems.push(`font families: ${BASE} [${fa}] ${OTHER} [${fb}]`);
    else if (a.fonts.join() !== b.fonts.join()) {
      notes.push(`${key}  weights loaded differ (not a fault): ${BASE} [${a.fonts}] ${OTHER} [${b.fonts}]`);
    }
    for (const [name, boxA] of Object.entries(a.boxes)) {
      const boxB = b.boxes[name];
      if (!boxA !== !boxB) problems.push(`${name}: ${boxA ? 'missing' : 'extra'} in ${OTHER}`);
      else if (boxA) {
        const d = Math.max(...boxA.map((v, i) => Math.abs(v - boxB[i])));
        if (d > TOLERANCE) problems.push(`${name} box off by ${d.toFixed(1)}px: [${boxA}] vs [${boxB}]`);
      }
    }
    for (const shot of ['top', 'down']) {
      const px = await clustered(`${width}-${state}-${shot}.png`);
      if (px.size) problems.push(`${shot} shot sizes differ ${px.size}`);
      else {
        if (px.clustered > worstPixels.v) worstPixels = { v: px.clustered, at: `${key} ${shot}` };
        if (px.clustered > CLUSTER_FAIL) problems.push(`${shot} shot: ${px.clustered}% clustered, box ${px.box}`);
      }
    }
  }
  report[key] = problems;
  if (problems.length) failures += 1;
}

await browser.close();
await writeFile(`${DIR}/report.json`, JSON.stringify(report, null, 1));

for (const width of [...new Set(Object.keys(report).map((k) => k.split(' ')[0]))]) {
  const keys = Object.keys(report).filter((k) => k.startsWith(`${width} `));
  const bad = keys.filter((k) => report[k].length);
  console.log(`${String(width).padStart(5)}  ${keys.length - bad.length}/${keys.length} states agree`);
  for (const k of bad) for (const p of report[k]) console.log(`         ${k.split(' ')[1].padEnd(18)} ${p}`);
}
console.log(`\nworst clustered difference ${worstPixels.v}% (${worstPixels.at ?? '-'})`);
console.log(failures ? `${failures} states FAILED` : 'all states agree');
process.exit(failures ? 1 : 0);
