/* Long tool outputs, cut down to what a reader decides on. Each takes the
   tool's JSON on stdout and the project root (to shorten paths), and may
   return { ok } to decide the step's result itself. */

const top = (map, n) => [...map].sort((a, b) => b[1] - a[1]).slice(0, n);

// With inline config off, ESLint notes each directive it ignored; those are not findings.
const messages = (results) =>
  results.flatMap((r) => r.messages.filter((m) => m.ruleId || !/inline config|noInlineConfig|has no effect/i.test(m.message)).map((m) => ({ ...m, filePath: r.filePath })));

/* The cycle gate fails on cycles only: a file the parser cannot read is
   listed, but it is not a cycle. */
function cycles(stdout, root) {
  const all = messages(JSON.parse(stdout));
  const found = all.filter((m) => m.ruleId === 'import-x/no-cycle');
  for (const m of found) console.log(`cycle: ${m.filePath.replace(root, '.')}:${m.line}`);
  const unread = [...new Set(all.filter((m) => !m.ruleId).map((m) => m.filePath))];
  for (const f of unread) console.log(`not parsed: ${f.replace(root, '.')}`);
  console.log(found.length ? `${found.length} import(s) in a cycle` : 'no import cycles');
  return { ok: found.length === 0 };
}

function eslint(stdout, root) {
  const byRule = new Map();
  const byFile = new Map();
  for (const m of messages(JSON.parse(stdout))) {
    const rule = m.ruleId ?? 'parse error';
    byRule.set(rule, (byRule.get(rule) ?? 0) + 1);
    byFile.set(m.filePath, (byFile.get(m.filePath) ?? 0) + 1);
  }
  const total = [...byRule.values()].reduce((a, b) => a + b, 0);
  console.log(`${total} finding(s) in ${byFile.size} file(s)`);
  for (const [rule, n] of top(byRule, 15)) console.log(`  ${String(n).padStart(5)}  ${rule}`);
  if (byFile.size) console.log('most findings:');
  for (const [file, n] of top(byFile, 8)) console.log(`  ${String(n).padStart(5)}  ${file.replace(root, '.')}`);
}

/* One line per vulnerable package: how many advisories, the worst score, and
   the highest version any of its advisories names as fixed - a version that
   clears them all only when the fixes sit on one release line. */
function osv(stdout, root) {
  const { results = [] } = JSON.parse(stdout);
  const rows = [];
  for (const source of results) {
    for (const pkg of source.packages ?? []) {
      const groups = pkg.groups ?? [];
      const worst = Math.max(0, ...groups.map((g) => Number(g.max_severity) || 0));
      const fixes = (pkg.vulnerabilities ?? [])
        .flatMap((v) => v.affected ?? [])
        .flatMap((a) => a.ranges ?? [])
        .flatMap((r) => r.events ?? [])
        .map((e) => e.fixed)
        .filter(Boolean);
      rows.push({
        name: `${pkg.package.name}@${pkg.package.version}`,
        ecosystem: pkg.package.ecosystem,
        count: groups.length,
        worst,
        fix: fixes.sort((a, b) => b.localeCompare(a, undefined, { numeric: true }))[0] ?? '-',
        source: (source.source?.path ?? '').split('\\').join('/').replace(root.split('\\').join('/'), '.'),
      });
    }
  }
  rows.sort((a, b) => b.worst - a.worst || b.count - a.count);
  const total = rows.reduce((n, r) => n + r.count, 0);
  console.log(`${total} known vulnerabilit${total === 1 ? 'y' : 'ies'} in ${rows.length} package(s)`);
  for (const r of rows) {
    console.log(`  ${r.worst.toFixed(1).padStart(4)}  ${String(r.count).padStart(3)}x  ${r.name.padEnd(36)} ${r.ecosystem.padEnd(5)} fixed in: ${r.fix.padEnd(10)} ${r.source}`);
  }
}

const SUMMARIES = { cycles, eslint, osv };

export function summarize(kind, stdout, root) {
  try {
    return SUMMARIES[kind](stdout, root) ?? {};
  } catch {
    console.log(stdout.slice(0, 4000));
    return {};
  }
}
