// Renders a move sheet page in a silent headless browser, saves it as one picture and prints the
// page's own report (the share of a carried prop inside the body or under the ground, per clip).
// Playwright comes from a skill's folder, never from the project's dependencies.
//
//   node sheet.mjs <playwright module path> "<url of move-sheet.html with its query>" <out.png>
//
// Exit code 1 when the page reports an error or a missing clip, so a script can gate on it.

import { pathToFileURL } from 'node:url';

const [pwPath, url, out] = process.argv.slice(2);
if (!pwPath || !url || !out) {
  console.error('usage: node sheet.mjs <playwright module path> "<url>" <out.png>');
  process.exit(2);
}
const { chromium } = await import(pathToFileURL(pwPath).href);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--mute-audio'] });
const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });
const problems = [];
page.on('pageerror', (e) => problems.push(`page error: ${e.message}`));
try {
  await page.goto(url);
  await page.waitForFunction(() => window.sheetReady === true, null, { timeout: 180000 });
  const report = await page.evaluate(() => window.sheet);
  console.log(report.join('\n'));
  if (report.some((line) => line.startsWith('no such clip'))) problems.push('a clip named in the query does not exist on this rig');
  await page.locator('canvas').screenshot({ path: out, timeout: 10000 }).catch(() => problems.push('nothing was drawn'));
} catch (e) {
  problems.push(String(e));
}
await browser.close();
for (const p of problems) console.error(p);
process.exit(problems.length ? 1 : 0);
