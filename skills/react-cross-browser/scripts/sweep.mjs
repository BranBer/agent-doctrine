import { mkdir, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { chromium, webkit } from 'playwright';

/* Every state the project names, at every width it names, in one engine -
   written down so `compare.mjs` can hold one engine to the other.

   The app's own knowledge lives in a driver module the project supplies;
   everything here is the same whatever is being walked. See
   `driver.example.mjs` for the contract.

     node sweep.mjs <driver.mjs> <chromium|webkit> [--widths 375,768,1440]
                                                   [--url http://...]
                                                   [--out qa/sweep]           */

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};
const positional = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
const [driverPath, engineName = 'chromium'] = positional;
if (!driverPath) {
  console.error('usage: node sweep.mjs <driver.mjs> <chromium|webkit> [--widths a,b] [--url u] [--out dir]');
  process.exit(2);
}

const driver = await import(pathToFileURL(resolve(driverPath)).href);
const URL_ = flag('url', driver.url ?? 'http://localhost:4173/');
const WIDTHS = (flag('widths') ?? (driver.widths ?? [375, 768, 1440]).join(',')).split(',').map(Number);
const OUT = flag('out', 'qa/sweep');
const HEIGHT = driver.height ?? 900;
const BOXES = driver.boxes ?? { h1: 'h1' };
const SETTLE = driver.settle ?? 600;
const engine = { chromium, webkit }[engineName];
if (!engine) {
  console.error(`unknown engine "${engineName}"`);
  process.exit(2);
}

/* Runs in the page. Records what a layout is built from rather than how it
   looks, so a difference points at a cause. */
const record = (boxes) => {
  const round = (v) => Math.round(v * 10) / 10;
  const box = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const b = el.getBoundingClientRect();
    return [round(b.left), round(b.top + scrollY), round(b.width), round(b.height)];
  };
  const imgs = [...document.images];
  /* The words showing, taken from the DOM rather than `innerText`: engines
     disagree on whether a zero-height `inert` subtree has words in it, and
     that difference is the instrument's, not the page's.

     A live region goes with them. What it holds is whatever was last
     announced, cleared on a timer the two engines do not share, so comparing
     it compares a race rather than the state. */
  const copy = document.body.cloneNode(true);
  copy.querySelectorAll('[inert],[aria-hidden="true"],[aria-live],script,style').forEach((el) => el.remove());
  return {
    text: copy.textContent.replace(/\s+/g, ' ').trim(),
    images: imgs.length,
    broken: imgs
      .filter((i) => !i.complete || i.naturalWidth === 0)
      .map((i) => (i.currentSrc || i.src).split('/').pop().slice(0, 60)),
    fonts: [
      ...new Set(
        [...document.fonts]
          .filter((f) => f.status === 'loaded')
          .map((f) => `${f.family.replace(/"/g, '')} ${f.weight}`),
      ),
    ].sort(),
    overflow: document.documentElement.scrollWidth - innerWidth,
    /* Anything whose right edge is past the window, whether or not the
       document grew: a clipping ancestor hides the overflow from
       `scrollWidth` while the element is still off the side of the screen.
       Only the innermost offender is reported, and decoration is allowed to
       bleed off its own panel. */
    past: [...document.querySelectorAll('body *')]
      .filter((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.right <= innerWidth + 1) return false;
        if (el.closest('[aria-hidden="true"]')) return false;
        return ![...el.children].some((c) => c.getBoundingClientRect().right > innerWidth + 1);
      })
      .slice(0, 4)
      .map((el) => `${el.tagName.toLowerCase()}.${String(el.className).slice(0, 40)} right=${Math.round(el.getBoundingClientRect().right)}`),
    hrefless: [...document.querySelectorAll('a')].filter((a) => !a.getAttribute('href')).length,
    boxes: Object.fromEntries(Object.entries(boxes).map(([name, sel]) => [name, box(sel)])),
  };
};

const browser = await engine.launch();
const out = {};
const dir = `${OUT}/${engineName}`;
await mkdir(dir, { recursive: true });

for (const width of WIDTHS) {
  const page = await browser.newPage({ viewport: { width, height: HEIGHT } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text().slice(0, 120)));

  for (const state of driver.states) {
    if (state.reload !== false) {
      await page.goto(URL_, { waitUntil: 'networkidle' });
      await page.waitForTimeout(400);
    }
    await state.go?.(page, { width, url: URL_ });
    // Park the pointer: a hover state left under it is not the state's.
    await page.mouse.move(4, 4);
    await page.waitForTimeout(SETTLE);

    // Walk the page so anything lazy mounts, then wait for the images to decode.
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight) {
        scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 60));
      }
      scrollTo(0, 0);
      await Promise.race([
        Promise.all([...document.images].map((i) => i.decode().catch(() => {}))),
        new Promise((r) => setTimeout(r, 4000)),
      ]);
    });
    await page.waitForTimeout(300);

    const data = await page.evaluate(record, BOXES);
    data.errors = errors.splice(0);
    out[`${width} ${state.name}`] = data;

    await page.screenshot({ path: `${dir}/${width}-${state.name}-top.png` });
    await page.evaluate(() => scrollTo(0, Math.round(innerHeight * 0.8)));
    await page.waitForTimeout(400);
    await page.screenshot({ path: `${dir}/${width}-${state.name}-down.png` });
    await page.evaluate(() => scrollTo(0, 0));
    await page.waitForTimeout(200);

    const flags = [
      data.broken.length && `${data.broken.length} broken images`,
      (data.overflow > 0 || data.past.length) && 'overflow',
      data.errors.length && `${data.errors.length} errors`,
    ].filter(Boolean);
    console.log(`  ${engineName} ${width} ${state.name.padEnd(18)} ${data.images} images  ${flags.join(', ') || 'ok'}`);
  }
  await page.close();
}

await browser.close();
await writeFile(`${OUT}/${engineName}.json`, JSON.stringify(out, null, 1));
console.log(`\nwrote ${OUT}/${engineName}.json - ${Object.keys(out).length} states`);
