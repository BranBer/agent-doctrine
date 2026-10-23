import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { chromium } from 'playwright';

/* Pixel snapping, which headless browsers hide.

   A background box is rasterised as `round(top + height) - round(top)`, so its
   painted height depends on the *top's* fraction. Where the device pixel ratio
   makes an element's offset land on a half device pixel, that element is
   snapped a pixel thinner and noticeably lighter than its siblings - a hairline
   rule, one line of a three-line glyph, one divider in a row of them.

   Headless Playwright coverage-antialiases where a real browser snaps, so both
   engines report the fault as clean at every ratio. Reproducing it needs a
   headed browser at a ratio whose fraction is .25 or .75.

   This measures the ink per device row inside an element's box, groups the
   inked rows into bands, and fails when bands that should match do not.

     node snap.mjs <url> <selector> [--dprs 1,1.25,1.5,1.75,2,2.25,3]
                                    [--driver d.mjs --state name]
                                    [--width 375] [--tolerance 0.1]
                                    [--css "sel{…}"]

   `--css` injects a rule before the page runs, which is how a candidate fix
   is tried - or an existing one switched off to confirm the check still
   fails without it. Never accept a fix whose negative control passes.       */

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};
const positional = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
const [URL_, SELECTOR] = positional;
if (!URL_ || !SELECTOR) {
  console.error('usage: node snap.mjs <url> <selector> [--dprs …] [--driver d.mjs --state name] [--width 375]');
  process.exit(2);
}
const DPRS = (flag('dprs', '1,1.25,1.5,1.75,2,2.25,3')).split(',').map(Number);
const WIDTH = Number(flag('width', 375));
const TOLERANCE = Number(flag('tolerance', 0.1));
const EXTRA_CSS = flag('css');
const driverPath = flag('driver');
const stateName = flag('state');

const driver = driverPath ? await import(pathToFileURL(resolve(driverPath)).href) : null;
const state = driver?.states.find((s) => s.name === stateName);
if (driverPath && !state) {
  console.error(`driver has no state "${stateName}"`);
  process.exit(2);
}

let failed = 0;
for (const dpr of DPRS) {
  // Headed, and the ratio forced on the browser rather than the context: a
  // context's deviceScaleFactor changes the capture, not the rasterisation.
  const browser = await chromium.launch({
    headless: false,
    args: [`--force-device-scale-factor=${dpr}`],
  });
  const page = await browser.newPage({ viewport: { width: WIDTH, height: 900 } });
  if (EXTRA_CSS) {
    await page.addInitScript((css) => {
      addEventListener('DOMContentLoaded', () => {
        const el = document.createElement('style');
        el.textContent = css;
        document.head.append(el);
      });
    }, EXTRA_CSS);
  }
  await page.goto(URL_, { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  await state?.go?.(page, { width: WIDTH, url: URL_ });
  await page.mouse.move(4, 4);
  await page.waitForTimeout(600);

  const target = page.locator(SELECTOR).first();
  if (!(await target.count())) {
    console.log(`dpr ${dpr}: "${SELECTOR}" not on the page`);
    await browser.close();
    continue;
  }
  const clip = await target.evaluate((el) => {
    const r = el.getBoundingClientRect();
    return { x: Math.floor(r.x) - 2, y: Math.floor(r.y) - 2, width: Math.ceil(r.width) + 4, height: Math.ceil(r.height) + 4 };
  });
  const shot = await page.screenshot({ clip });
  const bands = await page.evaluate(async (b64) => {
    const bmp = await createImageBitmap(await (await fetch(`data:image/png;base64,${b64}`)).blob());
    const canvas = document.createElement('canvas');
    canvas.width = bmp.width;
    canvas.height = bmp.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(bmp, 0, 0);
    const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const rows = [];
    for (let y = 0; y < canvas.height; y++) {
      let ink = 0;
      for (let x = 0; x < canvas.width; x++) {
        const i = (y * canvas.width + x) * 4;
        ink += 255 - Math.min(data[i], data[i + 1], data[i + 2]);
      }
      rows.push(ink / 255);
    }
    // The quietest row is the ground; anything meaningfully above it is ink.
    const floor = Math.min(...rows);
    const over = rows.map((v) => v - floor);
    const peak = Math.max(...over);
    const out = [];
    over.forEach((v, y) => {
      if (v < peak * 0.15) return;
      const last = out.at(-1);
      if (last && last.to === y - 1) {
        last.to = y;
        last.ink += v;
      } else out.push({ from: y, to: y, ink: v });
    });
    return out.map((band) => ({ rows: band.to - band.from + 1, ink: Math.round(band.ink) }));
  }, shot.toString('base64'));
  await browser.close();

  if (bands.length < 2) {
    console.log(`dpr ${dpr}: ${bands.length} band(s) - nothing to compare`);
    continue;
  }
  const inks = bands.map((b) => b.ink).sort((x, y) => x - y);
  const median = inks[Math.floor(inks.length / 2)];
  const worst = Math.max(...bands.map((b) => Math.abs(b.ink - median) / median));
  const ok = worst <= TOLERANCE;
  if (!ok) failed++;
  console.log(
    `dpr ${String(dpr).padEnd(5)} ${ok ? 'PASS' : 'FAIL'}  ` +
      bands.map((b) => `${b.rows}r/${b.ink}`).join('  ') +
      `   worst ${(worst * 100).toFixed(0)}% off the median`,
  );
}

console.log(failed ? `\n${failed} ratio(s) snap unevenly` : '\nevery ratio paints its bands alike');
process.exit(failed ? 1 : 0);
