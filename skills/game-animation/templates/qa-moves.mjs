// PROTOTYPE - NOT FOR PRODUCTION
// Every hero's moves against its own body, in one run: renders the move sheet for each role on both
// model sets and prints, per clip, the worst share of what the hero carries that is inside its body
// or under the ground. Sheets are saved for looking at. The dev server must be running.
//
//   node scripts/qa-moves.mjs <playwright module path> [role,role] [baseUrl] [outDir]
//
// Exit code 1 when a clip is over its allowance, a clip is missing or a page fails.
// A run that read at least one sheet leaves evidence/moves/last-run.txt, which moves-gate.mjs reads.

import { mkdirSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const [pwPath, only = '', base = 'http://127.0.0.1:4310/', out = 'evidence/moves'] = process.argv.slice(2);
if (!pwPath) {
  console.error('usage: node scripts/qa-moves.mjs <playwright module path> [role,role] [baseUrl] [outDir]');
  process.exit(2);
}

const PACK = 'Idle,Running_A,Walking_Backwards,Running_Strafe_Left,Running_Strafe_Right,Dodge_Forward,Dodge_Backward,Dodge_Left,Dodge_Right,Cheer,Hit_A,Spellcasting,Jump_Idle';
/**
 * What to sheet for each role: the thing it carries, its arms-only attack and what plays beneath it,
 * the rest of its clips and what plays beneath those, and the share allowed inside the body.
 * The mage's book has few points to test; one of them is where its inner edge rests on the collar, in
 * the pack's own clips too, so it reads as a quarter to a third.
 */
const ROLES = {
  archer: [{ prop: 'Bow', attack: 'Bow_Shot', rest: `${PACK},Use_Item`, under: 'Bow_Carry', allow: 2 }],
  mage: [
    { prop: '1H_Wand', attack: 'Wand_Flick,Wand_Sweep,Wand_Point', rest: `${PACK},Spellcast_Raise,Spellcast_Long`, under: '', allow: 2 },
    { prop: 'Spellbook_open', attack: 'Wand_Flick,Wand_Sweep,Wand_Point', rest: '', under: '', allow: 34 },
  ],
  healer: [{ prop: '2H_Staff', attack: 'Staff_Bolt,Staff_Channel', rest: `${PACK},Spellcast_Raise,Spellcast_Long`, under: '', allow: 2 }],
};

const { chromium } = await import(pathToFileURL(pwPath).href);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--mute-audio'] });
const problems = [];
let read = 0;

async function sheet(name, query) {
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });
  page.on('pageerror', (e) => problems.push(`${name}: page error: ${e.message}`));
  try {
    await page.goto(`${base}scripts/move-sheet.html?${query}`);
    await page.waitForFunction(() => window.sheetReady === true, null, { timeout: 240000 });
    const lines = await page.evaluate(() => window.sheet);
    await page.locator('canvas').screenshot({ path: `${out}/${name}.png`, timeout: 20000 });
    return lines;
  } catch (e) {
    problems.push(`${name}: ${String(e).split('\n')[0]}`);
    return [];
  } finally {
    await page.close();
  }
}

for (const role of Object.keys(ROLES).filter((r) => !only || only.split(',').includes(r))) {
  for (const set of ['placeholder', 'generated']) {
    const models = set === 'generated' ? 'models=generated&' : '';
    for (const { prop, attack, rest, under, allow } of ROLES[role]) {
      const runs = [['attack', `clips=${attack}&under=Legs_Idle&cols=8&views=play,toward,away,front,side&cell=200`]];
      if (rest) runs.push(['rest', `clips=${rest}&under=${under}&cols=6&views=front&cell=140`]);
      for (const [label, query] of runs) {
        const name = `${role}-${set}-${prop}-${label}`;
        for (const line of await sheet(name, `${models}role=${role}&prop=${prop}&span=1.7&${query}`)) {
          const share = Number(/worst (\d+)%/.exec(line)?.[1] ?? NaN);
          const clip = line.split(' ')[0];
          read += 1;
          const bad = Number.isNaN(share) || share > allow;
          if (bad) problems.push(`${role} ${set} ${prop}: ${line}`);
          console.log(`${bad ? 'OVER' : 'ok  '} ${role.padEnd(7)} ${set.padEnd(11)} ${prop.padEnd(15)} ${clip.padEnd(22)} ${Number.isNaN(share) ? line : `${share}%`}`);
        }
      }
    }
  }
}
await browser.close();
// The stamp says the check ran, not that it passed: a run that read nothing (the server down) leaves none.
if (read) {
  mkdirSync(new URL('../evidence/moves/', import.meta.url), { recursive: true });
  writeFileSync(new URL('../evidence/moves/last-run.txt', import.meta.url), `${new Date().toISOString()} roles ${only || 'all'}: ${read} clips read, ${problems.length} problem(s)\n`);
}
console.log(problems.length ? `\n${problems.length} problem(s):\n${problems.join('\n')}` : `\nall within allowance; sheets in ${out}/`);
process.exit(problems.length ? 1 : 0);
