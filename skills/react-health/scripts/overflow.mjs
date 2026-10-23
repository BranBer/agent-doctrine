import { parseArgs } from 'node:util';
import { chromium, webkit } from 'playwright';

/* Fails if a page is ever wider than the window, or if any element's right
   edge is past it - a clipped ancestor hides the second from scrollWidth
   (react-doctrine 10). Decoration under aria-hidden may bleed.

     node overflow.mjs <url...> [--widths 320,375,768,1024,1440] [--engine both]  */
const { values, positionals: urls } = parseArgs({
  allowPositionals: true,
  options: {
    widths: { type: 'string', default: '320,375,430,595,768,1024,1200,1440' },
    engine: { type: 'string', default: 'both' },
  },
});
if (!urls.length) throw new Error('usage: node overflow.mjs <url...>');
const engines = values.engine === 'both' ? [chromium, webkit] : [values.engine === 'webkit' ? webkit : chromium];

let failed = 0;
for (const engine of engines) {
  const browser = await engine.launch();
  for (const url of urls) {
    for (const width of values.widths.split(',').map(Number)) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.goto(url, { waitUntil: 'networkidle' });
      const { scroll, offenders } = await page.evaluate(() => ({
        scroll: document.documentElement.scrollWidth,
        offenders: [...document.querySelectorAll('body *')]
          .filter((el) => !el.closest('[aria-hidden="true"]') && el.getBoundingClientRect().right > innerWidth + 1)
          .slice(0, 5)
          .map((el) => `${el.tagName.toLowerCase()}.${String(el.className.baseVal ?? el.className).slice(0, 50)}`),
      }));
      const ok = scroll <= width && offenders.length === 0;
      if (!ok) failed += 1;
      console.log(`${ok ? 'PASS' : 'FAIL'} ${engine.name()} ${width} ${url} -> scrollWidth ${scroll}`);
      for (const o of ok ? [] : offenders) console.log(`       ${o}`);
      await page.close();
    }
  }
  await browser.close();
}
process.exit(failed ? 1 : 0);
