import { readFile } from 'node:fs/promises';
import { chromium } from 'playwright';
// Is a shipped asset the raw photo with a left fade already burned in?
// Both are stretched to one box, so only the shape of the column ratio matters:
// a smooth ramp from ~0.2 to 1.0 is the mask; flat ~1.0 is a clean photo.
const [raw, asset] = await Promise.all(process.argv.slice(2, 4).map(f => readFile(f).then(x => x.toString('base64'))));
const b = await chromium.launch(); const p = await b.newPage();
const out = await p.evaluate(async ([raw, asset]) => {
  const load = (s, t) => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = `data:image/${t};base64,` + s; });
  const [ri, ai] = await Promise.all([load(raw, 'png'), load(asset, 'jpeg')]);
  const W = 400, H = 300;
  const px = img => { const c = new OffscreenCanvas(W, H); c.getContext('2d').drawImage(img, 0, 0, W, H); return c.getContext('2d').getImageData(0, 0, W, H).data; };
  const [rd, ad] = [px(ri), px(ai)];
  const lum = (d, i) => 0.2126*d[i] + 0.7152*d[i+1] + 0.0722*d[i+2];
  const band = (d, x0, x1, y0, y1) => { let s = 0, n = 0; for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { s += lum(d, (y*W+x)*4); n++; } return s / n; };
  const cols = []; for (let c = 0; c < 10; c++) { const x0 = Math.floor(c*W/10), x1 = Math.floor((c+1)*W/10); cols.push(band(ad, x0, x1, 0, Math.floor(H*0.4)) / band(rd, x0, x1, 0, Math.floor(H*0.4))); }
  const rows = []; for (let r = 0; r < 6; r++) { const y0 = Math.floor(r*H/6), y1 = Math.floor((r+1)*H/6); rows.push(band(ad, 0, W, y0, y1) / band(rd, 0, W, y0, y1)); }
  return { cols, rows };
}, [raw, asset]);
await b.close();
console.log('asset/raw by column (left->right): ' + out.cols.map(v => v.toFixed(2)).join(' '));
console.log('asset/raw by row    (top->bottom): ' + out.rows.map(v => v.toFixed(2)).join(' '));
