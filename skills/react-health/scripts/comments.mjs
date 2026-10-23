import { execFileSync } from 'node:child_process';
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { parseArgs } from 'node:util';

/* Three checks on the comments in an app (react-doctrine 4).
   1. Dangling pointers. The app ships alone, so a comment citing a doctrine
      rule number, a working file or a design-file node id points at something
      its reader cannot open. This fails.
   2. Density. Whether a comment earns its line is a judgement, so this only
      lists files over 30% comment.
   3. What the working diff added. Density barely moves when four lines go in;
      every comment line added since a revision is listed. Does not fail.

     node comments.mjs [srcDir] [--since HEAD~1] [--ban "PROJECT\\.md|QA-LOG"] [--skip Gallery]

   srcDir defaults to ./src. --ban adds patterns to the dangling check (the
   working files this project keeps beside the app); --skip excludes paths. */
const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    since: { type: 'string', default: 'HEAD' },
    ban: { type: 'string', multiple: true, default: [] },
    skip: { type: 'string', multiple: true, default: [] },
  },
});
const SRC = positionals[0] ?? 'src';
const RATIO = 0.3;
const FLOOR = 6; // a three-line note in a six-line file is not debt

const IS_COMMENT = /^\s*(\*|\/\/|\/\*|\{\/\*)/;
// Doctrine rule numbers, the doctrine and case-law files, design-file node ids and links.
const BASE = String.raw`\brule \d|AGENTS\.md|CLAUDE\.md|PROJECT\.md|figma\.com/|\b\d{1,5}:\d{3,6}\b`;
const DANGLING = new RegExp([BASE, ...values.ban].join('|'), 'i');

const walk = async (dir) => {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, e.name);
    if (values.skip.some((s) => path.includes(s))) continue;
    if (e.isDirectory()) out.push(...(await walk(path)));
    else if (/\.(tsx?|jsx?|css)$/.test(e.name) && !e.name.endsWith('.d.ts')) out.push(path);
  }
  return out;
};

const count = (src) => {
  let comment = 0;
  let code = 0;
  let block = false;
  for (const raw of src.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    if (block) {
      comment += 1;
      if (line.includes('*/')) block = false;
      continue;
    }
    if (line.startsWith('/*') || line.startsWith('{/*')) {
      comment += 1;
      if (!line.includes('*/')) block = true;
      continue;
    }
    if (line.startsWith('//') || line.startsWith('*')) {
      comment += 1;
      continue;
    }
    code += 1;
  }
  return { comment, code };
};

const short = (file) => file.replace(/.*src[\\/]/, '').replaceAll('\\', '/');

let total = { comment: 0, code: 0 };
const dense = [];
const dangling = [];

for (const file of await walk(SRC)) {
  const src = await readFile(file, 'utf8');
  // A block comment's later lines carry no marker, so track the block.
  let inBlock = false;
  src.split('\n').forEach((line, i) => {
    const start = line.indexOf('/*');
    const isComment = inBlock || start !== -1 || /(^|\s)\/\//.test(line);
    if (isComment && DANGLING.test(line)) dangling.push(`${short(file)}:${i + 1}  ${line.trim().slice(0, 70)}`);
    if (inBlock) inBlock = !line.includes('*/');
    else if (start !== -1) inBlock = !line.slice(start).includes('*/');
  });
  const c = count(src);
  total = { comment: total.comment + c.comment, code: total.code + c.code };
  const ratio = c.comment / (c.comment + c.code);
  if (ratio > RATIO && c.comment >= FLOOR) dense.push({ file, ...c, ratio });
}

for (const d of dangling) console.log(`points outside the shipped app: ${d}`);

dense.sort((a, b) => b.ratio - a.ratio);
for (const r of dense) {
  console.log(
    `${String(Math.round(r.ratio * 100)).padStart(3)}%  ${String(r.comment).padStart(3)} comment / ${String(r.code).padStart(3)} code  ${short(r.file)}`,
  );
}
const overall = total.comment / (total.comment + total.code || 1);
console.log(`\noverall ${total.comment}/${total.comment + total.code} = ${(overall * 100).toFixed(1)}%`);
console.log(dense.length ? `${dense.length} file(s) over ${RATIO * 100}% - read them, not this number` : 'nothing over threshold');

// Added since the revision, staged or not; line numbers are the new file's.
const added = [];
try {
  const diff = execFileSync('git', ['diff', values.since, '--', SRC], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  });
  let file = '';
  let line = 0;
  for (const raw of diff.split('\n')) {
    const head = /^\+\+\+ b\/(.+)$/.exec(raw);
    if (head) {
      file = head[1];
      continue;
    }
    const hunk = /^@@ -\d+(?:,\d+)? \+(\d+)/.exec(raw);
    if (hunk) {
      line = Number(hunk[1]);
      continue;
    }
    if (raw.startsWith('-') || raw.startsWith('\\')) continue;
    if (raw.startsWith('+') && IS_COMMENT.test(raw.slice(1))) added.push(`${file}:${line}  ${raw.slice(1).trim().slice(0, 76)}`);
    if (raw.startsWith('+') || raw.startsWith(' ')) line += 1;
  }
} catch {
  console.log('\nno git diff available - skipping the added-comment list');
}
console.log(added.length ? `\n${added.length} comment line(s) added since ${values.since}:` : `\nno comment lines added since ${values.since}`);
for (const a of added) console.log(`  ${a}`);

process.exit(dangling.length ? 1 : 0);
