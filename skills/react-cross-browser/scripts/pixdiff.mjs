import { readFile, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

/* Two PNGs, compared the only way a cross-engine screenshot can honestly be
   compared: raw difference, then the difference eroded with a 9x9 window so
   that antialiased glyph edges drop out and only a block wider than a stroke
   survives. Optionally writes a magenta map of what survived.

     node pixdiff.mjs <a.png> <b.png> [--map diff.png] [--channel 24]
                                      [--fail 0.05]                          */

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};
const [A, B] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!A || !B) {
  console.error('usage: node pixdiff.mjs <a.png> <b.png> [--map diff.png] [--channel 24] [--fail 0.05]');
  process.exit(2);
}
const MAP = flag('map');
const CHANNEL = Number(flag('channel', 24));
const FAIL = Number(flag('fail', 0.05));

const [a, b] = await Promise.all([A, B].map((f) => readFile(f).then((x) => x.toString('base64'))));
const browser = await chromium.launch();
const page = await browser.newPage();

const out = await page.evaluate(
  async ([x, y, channel, wantMap]) => {
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
    const w = ia.width;
    const h = ia.height;
    const pixels = (img) => {
      const c = new OffscreenCanvas(w, h);
      const ctx = c.getContext('2d');
      ctx.drawImage(img, 0, 0);
      return ctx.getImageData(0, 0, w, h).data;
    };
    const [da, db] = [pixels(ia), pixels(ib)];
    const mask = new Uint8Array(w * h);
    let raw = 0;
    let maxDelta = 0;
    for (let p = 0; p < mask.length; p++) {
      const i = p * 4;
      const d = Math.max(
        Math.abs(da[i] - db[i]),
        Math.abs(da[i + 1] - db[i + 1]),
        Math.abs(da[i + 2] - db[i + 2]),
      );
      if (d > maxDelta) maxDelta = d;
      if (d > channel) {
        mask[p] = 1;
        raw++;
      }
    }
    const survivor = new Uint8Array(w * h);
    let hits = 0;
    let box = [Infinity, Infinity, -1, -1];
    const rows = [];
    for (let py = 4; py < h - 4; py++) {
      let n = 0;
      for (let px = 4; px < w - 4; px++) {
        if (!mask[py * w + px]) continue;
        let k = 0;
        for (let dy = -4; dy <= 4; dy++) {
          for (let dx = -4; dx <= 4; dx++) k += mask[(py + dy) * w + px + dx];
        }
        if (k >= 60) {
          survivor[py * w + px] = 1;
          hits++;
          n++;
          box = [Math.min(box[0], px), Math.min(box[1], py), Math.max(box[2], px), Math.max(box[3], py)];
        }
      }
      if (n) rows.push([py, n]);
    }
    const total = w * h;
    const result = {
      size: null,
      width: w,
      height: h,
      maxDelta,
      raw: Math.round((raw / total) * 10000) / 100,
      clustered: Math.round((hits / total) * 100000) / 1000,
      box: box[2] < 0 ? null : box,
      bands: [],
    };
    for (const [py, n] of rows) {
      const last = result.bands.at(-1);
      if (last && py === last.to + 1) {
        last.to = py;
        last.widest = Math.max(last.widest, n);
      } else result.bands.push({ from: py, to: py, widest: n });
    }
    result.bands = result.bands.filter((band) => band.to - band.from > 2);
    if (wantMap) {
      const canvas = new OffscreenCanvas(w, h);
      const ctx = canvas.getContext('2d');
      const img = ctx.createImageData(w, h);
      for (let p = 0; p < mask.length; p++) {
        const i = p * 4;
        // the page in pale grey, what differs in magenta, what survived erosion solid
        const g = 235 + Math.round(da[i] * 0.08);
        if (survivor[p]) img.data.set([255, 0, 255, 255], i);
        else if (mask[p]) img.data.set([255, 170, 255, 255], i);
        else img.data.set([g, g, g, 255], i);
      }
      ctx.putImageData(img, 0, 0);
      const blob = await canvas.convertToBlob({ type: 'image/png' });
      result.png = Array.from(new Uint8Array(await blob.arrayBuffer()));
    }
    return result;
  },
  [a, b, CHANNEL, Boolean(MAP)],
);

await browser.close();

if (out.size) {
  console.log(`sizes differ: ${out.size[0]}x${out.size[1]} vs ${out.size[2]}x${out.size[3]}`);
  process.exit(1);
}
if (out.png) {
  await writeFile(MAP, Buffer.from(out.png));
  delete out.png;
}
console.log(`${out.width}x${out.height}  max channel delta ${out.maxDelta}`);
console.log(`raw ${out.raw}%   clustered ${out.clustered}%   -> ${out.clustered > FAIL ? 'FAIL' : 'PASS'}`);
if (out.box) console.log(`clustered box  left ${out.box[0]} top ${out.box[1]} right ${out.box[2]} bottom ${out.box[3]}`);
for (const band of out.bands) console.log(`  band y ${band.from}-${band.to}  widest row ${band.widest}px`);
if (MAP) console.log(`map -> ${MAP}`);
process.exit(out.clustered > FAIL ? 1 : 0);
