import { AxeBuilder } from '@axe-core/playwright';
import { parseArgs } from 'node:util';
import { chromium, webkit } from 'playwright';

/* axe-core (WCAG 2.2 A/AA plus best practice) over each URL at each width,
   in Chromium and WebKit. Only the states a URL loads into are scanned: a page
   whose content appears after interaction needs a project script that drives
   it there and calls AxeBuilder itself.

     node axe-scan.mjs <url...> [--widths 375,768,1440] [--engine both] [--json out.json]
                              [--exclude footer --exclude "#cookie-banner"]

   --exclude leaves out markup the project does not own (a host site's
   footer, a vendor widget); report it to its owner instead.            */
const { values, positionals: urls } = parseArgs({
  allowPositionals: true,
  options: {
    widths: { type: 'string', default: '375,768,1440' },
    engine: { type: 'string', default: 'both' },
    json: { type: 'string' },
    exclude: { type: 'string', multiple: true, default: [] },
  },
});
if (!urls.length) throw new Error('usage: node axe-scan.mjs <url...>');
const engines = values.engine === 'both' ? [chromium, webkit] : [values.engine === 'webkit' ? webkit : chromium];
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'];

const results = [];
let violations = 0;
for (const engine of engines) {
  const browser = await engine.launch();
  for (const url of urls) {
    for (const width of values.widths.split(',').map(Number)) {
      // axe injects into every frame, which it can only do in a context it owns.
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.goto(url, { waitUntil: 'networkidle' });
      const builder = new AxeBuilder({ page }).withTags(TAGS);
      for (const selector of values.exclude) builder.exclude(selector);
      const r = await builder.analyze();
      violations += r.violations.length;
      results.push({ engine: engine.name(), url, width, violations: r.violations, incomplete: r.incomplete.length });
      console.log(`${r.violations.length ? 'FAIL' : 'PASS'} ${engine.name()} ${width} ${url}  violations=${r.violations.length} needs-review=${r.incomplete.length}`);
      for (const v of r.violations) {
        console.log(`   [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length})`);
        for (const n of v.nodes.slice(0, 3)) console.log(`      ${n.target.join(' ')}`);
      }
      await context.close();
    }
  }
  await browser.close();
}
if (values.json) {
  const { writeFileSync } = await import('node:fs');
  writeFileSync(values.json, JSON.stringify(results, null, 2));
}
process.exit(violations ? 1 : 0);
