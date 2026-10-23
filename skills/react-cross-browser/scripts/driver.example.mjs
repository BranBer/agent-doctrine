/* The contract `sweep.mjs` and `snap.mjs` drive a project through.
 *
 * Copy this beside the app (a harness folder, never inside the app - the
 * shipped repo carries no browser dependency for its own QA) and fill it in.
 * Everything the app knows lives here; everything the check knows lives in the
 * skill. */

/** Where the production build is served. `--url` overrides it. */
export const url = 'http://localhost:4173/';

/** The widths to walk: the edges the design actually has, plus the narrowest
 *  the page must still fit. `--widths` overrides it. */
export const widths = [375, 768, 1440];

/** Viewport height. One screen, so "the fold" means something. */
export const height = 900;

/** How long a move needs before it has landed. Raise it for an app whose
 *  transitions run longer than half a second. */
export const settle = 600;

/** The boxes a layout is built from, by name. These are compared between
 *  engines to a pixel and a half, so pick the elements whose position carries
 *  meaning - a pinned bar, the heading, the first card of a grid, the footer -
 *  rather than every element on the page. A name that resolves to nothing in
 *  one engine and something in the other is itself a finding. */
export const boxes = {
  header: 'header',
  h1: 'h1',
  main: 'main',
  footer: 'footer',
};

/** The states to visit, in order.
 *
 *  Each is `{ name, go?, reload? }`. `go(page, { width, url })` drives the
 *  page into the state; `reload: false` keeps whatever the previous state left
 *  on screen, which is how you walk a flow without paying for a fresh load at
 *  every step. Without it each state starts from a fresh load of `url`.
 *
 *  Name a state after the content it shows, not the route: the name is what a
 *  failure is reported against, and it has to mean something months later. */
export const states = [
  { name: 'home' },
  {
    name: 'pricing',
    async go(page) {
      await page.getByRole('link', { name: 'Pricing' }).click();
      await page.waitForURL(/pricing/);
    },
  },
  {
    // Continues from the state above rather than loading again.
    name: 'pricing-annual',
    reload: false,
    async go(page) {
      await page.getByRole('button', { name: 'Annual' }).click();
    },
  },
  {
    // A state that only exists at some widths still has to be named: drive
    // whichever control that width actually shows.
    name: 'menu-open',
    async go(page, { width }) {
      if (width >= 768) return;
      await page.getByRole('button', { name: 'Menu' }).click();
      await page.waitForTimeout(400);
    },
  },
];
