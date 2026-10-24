"""Compare a model's orthographic renders with the matching views of a concept sheet.

  python -I compare.py components <sheet.png> [--tol 10]
  python -I compare.py check <concept.json> [--outline 0]
  python -I compare.py <concept.json> <renders-dir> <out-dir> [--ref side:w] [--outline 0]
                       [--min-iou 0.94] [--max-size 0.03] [--max-p95 0.03] [--max-colour 1] [--gate side,front,top]
                       [--bar bar.json]

`components` lists the separate drawings on a sheet, largest first, and writes <sheet>-components.png
with each one boxed and numbered, so the views can be named in concept.json:

  {"sheet": "art/concept/hatchback-ortho-1.png",
   "views": {"side": [x, y, w, h], "front": [x, y, w, h], "back": [...], "top": [...]}}

Paths in concept.json are relative to the working directory (the project root). Views use the
orientations views.mjs renders: side and top with the nose left, front and back face on.

The comparison takes one scale for every view, from the --ref view's bounding box ("side:w" is the
side view's length). Proportion errors between views therefore show up rather than being scaled
away. --outline is the width of the concept's ink line outside the true silhouette, in sheet pixels.
It is taken off the concept's bounding box before scaling and added back around the model's mask.
Each view is aligned on its bounding box, bottom-centre (centre for top), and tried mirrored too.

Writes <out-dir>/sheet.png (per view: concept, model, and an overlay where red is concept-only and
blue is model-only) and <out-dir>/report.json, and prints a table. A view passes when its IoU is at
least --min-iou, its width and height errors are within --max-size, and its edge_p95 is within
--max-p95. The defaults come from breaking a good model in known ways (roof 15% low, wheels 15% small,
wheelbase 10% long, 10% narrower, a part removed): each fault failed at least one view and the good
model passed every one. Exits 1 if any view named in --gate (default: all) fails.

Per view:
  iou        shared silhouette area over combined silhouette area
  w_err      model width minus concept width, over concept width (+ is too wide)
  h_err      the same for height
  edge_mean  mean distance between the two outlines, as a share of the view's longer side
  edge_p95   95th-percentile distance, as a share; a high value with a good mean is one bad part
  hull       the concept view against its own convex hull: the IoU a featureless blob would score.
             Where iou is not clearly above hull, that view can't tell a right model from a wrong one
  dE         median colour difference (CIE76) between concept and unlit model where both overlap
  colour_miss  share of the overlap whose colour differs by more than 25: the measure that sees a
             missing or wrong surface panel (door, window, decal), which no silhouette can
  flip       the mirroring that matched best; anything but "none" means the model faces the other way

consistency checks the concept against itself: the spread of length (L), width (W) and height (H)
across the views that show each one. `check` names any view more than 3% from the median (leave it
out of --gate) and exits 1 only when side and front, the master views, disagree on height by more
than 5%, which needs a new sheet.
"""
import json, os, sys

import cv2
import numpy as np

AXES = {"side": ("L", "H"), "top": ("L", "W"), "front": ("W", "H"), "back": ("W", "H")}
FLIPS = {"none": None, "h": 1, "v": 0, "hv": -1}
PAD = 24
# A colour this far off (CIE76) is a different paint, not shading: a wrong or missing panel.
COLOUR_MISS_DE = 25
RED, BLUE, GREY = (60, 60, 230), (230, 120, 40), (150, 150, 150)


def lab(bgr):
    return cv2.cvtColor(bgr.astype(np.float32) / 255, cv2.COLOR_BGR2Lab)


def fill_from_border(bg_like):
    """Foreground is everything not connected to the border through background-like pixels, so
    enclosed holes count as solid on both sides of the comparison."""
    _, labels = cv2.connectedComponents(bg_like.astype(np.uint8), connectivity=4)
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    return ~np.isin(labels, edge[edge > 0])


def keep_large(mask, share=0.05, bridge=5):
    """Drops pieces smaller than `share` of the largest, such as a sheet's labels. Pieces within
    `bridge` px of each other count as one, so a knob a hairline from its rod joins the body, while a
    label's letters join only each other and still fall under `share` as a word."""
    joined = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((bridge, bridge), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    if n <= 1:
        return mask
    areas = stats[1:, cv2.CC_STAT_AREA]
    big = 1 + np.flatnonzero(areas >= areas.max() * share)
    return mask & np.isin(labels, big)


def concept_mask(bgr, tol=10.0):
    l = lab(bgr)
    border = np.concatenate([l[:2].reshape(-1, 3), l[-2:].reshape(-1, 3), l[:, :2].reshape(-1, 3), l[:, -2:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    return keep_large(fill_from_border(np.linalg.norm(l - bg, axis=2) <= tol)), bg


def render_mask(rgba):
    # Every rendered piece counts: renders carry no labels, and dropping a piece would hide an error.
    return fill_from_border(rgba[..., 3] < 128)


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


def components(sheet, tol=10.0):
    img = cv2.imread(sheet)
    fg, _ = concept_mask(img, tol)
    # Merge the pieces of one drawing (wheels, a spoiler) that the background separates.
    merged = cv2.dilate(fg.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, _, stats, _ = cv2.connectedComponentsWithStats(merged, connectivity=8)
    boxes = sorted((tuple(int(v) for v in s[:4]) for s in stats[1:] if s[4] > 0.001 * fg.size), key=lambda b: -b[2] * b[3])
    out = img.copy()
    for i, (x, y, w, h) in enumerate(boxes):
        # The dilation added 7 px all round; report the drawing's own box.
        boxes[i] = (x + 7, y + 7, w - 14, h - 14)
        cv2.rectangle(out, (x, y), (x + w, y + h), RED, 3)
        cv2.putText(out, str(i), (x + 6, y + 34), cv2.FONT_HERSHEY_SIMPLEX, 1.2, RED, 3)
    cv2.imwrite(os.path.splitext(sheet)[0] + "-components.png", out)
    return boxes


def edges(mask):
    m = mask.astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0


def edge_distance(a, b):
    """Symmetric outline distances in pixels: mean and 95th percentile."""
    ea, eb = edges(a), edges(b)
    da = cv2.distanceTransform((~ea).astype(np.uint8), cv2.DIST_L2, 3)
    db = cv2.distanceTransform((~eb).astype(np.uint8), cv2.DIST_L2, 3)
    d = np.concatenate([db[ea], da[eb]])
    return float(d.mean()), float(np.percentile(d, 95))


def place(canvas_shape, img, bottom):
    """Centres img on a canvas horizontally, and at the bottom or the middle vertically."""
    H, W = canvas_shape
    out = np.zeros((H, W) + img.shape[2:], img.dtype)
    h, w = img.shape[:2]
    x = (W - w) // 2
    y = H - PAD - h if bottom else (H - h) // 2
    out[y:y + h, x:x + w] = img
    return out


def concept_views(cfg):
    sheet = cv2.imread(cfg["sheet"])
    if sheet is None:
        raise SystemExit("can't read sheet %s" % cfg["sheet"])
    views = {}
    for name, (x, y, w, h) in cfg["views"].items():
        crop = sheet[y:y + h, x:x + w]
        cmask, bg = concept_mask(crop)
        cx, cy, cw, ch = bbox(cmask)
        views[name] = {"concept": crop[cy:cy + ch, cx:cx + cw], "cmask": cmask[cy:cy + ch, cx:cx + cw], "bg": bg}
    return views


def load_views(cfg, renders):
    views = concept_views(cfg)
    for name, v in views.items():
        lit = cv2.imread(os.path.join(renders, name + ".png"), cv2.IMREAD_UNCHANGED)
        flat = cv2.imread(os.path.join(renders, name + ".flat.png"), cv2.IMREAD_UNCHANGED)
        if lit is None or lit.shape[2] != 4:
            raise SystemExit("no RGBA render %s.png in %s; run views.mjs first" % (name, renders))
        mmask = render_mask(lit)
        mx, my, mw, mh = bbox(mmask)
        v.update(lit=lit[my:my + mh, mx:mx + mw], flat=flat[my:my + mh, mx:mx + mw], mmask=mmask[my:my + mh, mx:mx + mw])
    return views


def check(concept_json, outline=0):
    """The concept sheet against itself: the spread of each dimension across the views showing it."""
    return consistency(concept_views(json.load(open(concept_json, encoding="utf8"))), outline)


def consistency(views, outline):
    dims = {}
    for name, v in views.items():
        if name in AXES:
            h, w = v["cmask"].shape
            for axis, size in zip(AXES[name], (w - 2 * outline, h - 2 * outline)):
                dims.setdefault(axis, []).append(size)
    return {a: (max(s) - min(s)) / np.mean(s) for a, s in dims.items() if len(s) > 1}


def compare_view(name, v, scale, outline):
    ch, cw = v["cmask"].shape
    mh, mw = v["mmask"].shape
    size = (max(1, round(mw * scale)), max(1, round(mh * scale)))
    m = cv2.resize(v["mmask"].astype(np.float32), size, interpolation=cv2.INTER_AREA) >= 0.5
    lit = cv2.resize(v["lit"], size, interpolation=cv2.INTER_AREA)
    flat = cv2.resize(v["flat"], size, interpolation=cv2.INTER_AREA)
    if outline:
        pad = lambda img: cv2.copyMakeBorder(img, outline, outline, outline, outline, cv2.BORDER_CONSTANT, value=0)
        lit, flat = pad(lit), pad(flat)
        m = cv2.dilate(pad(m.astype(np.uint8)), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline + 1,) * 2)) > 0
    bh, bw = m.shape
    shape = (max(ch, bh) + 2 * PAD, max(cw, bw) + 2 * PAD)
    bottom = name != "top"
    C = place(shape, v["cmask"], bottom)
    best = None
    flips = ("none", "h", "v", "hv") if name == "top" else ("none", "h")
    for f in flips:
        code = FLIPS[f]
        fm, fl, ff = (m, lit, flat) if code is None else (cv2.flip(m.astype(np.uint8), code) > 0, cv2.flip(lit, code), cv2.flip(flat, code))
        M = place(shape, fm, bottom)
        iou = float((C & M).sum() / max(1, (C | M).sum()))
        if best is None or iou > best[0] + 1e-9:
            best = (iou, f, M, place(shape, fl, bottom), place(shape, ff, bottom))
    iou, flip, M, LIT, FLAT = best
    mean, p95 = edge_distance(C, M)
    longer = max(ch, cw)
    concept = place(shape, v["concept"], bottom)
    core = cv2.erode((C & M).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    diff = np.linalg.norm(lab(concept)[core] - lab(FLAT[..., :3])[core], axis=1) if core.any() else np.array([np.nan])
    dE = float(np.median(diff))
    colour_miss = float((diff > COLOUR_MISS_DE).mean())
    hull = np.zeros(v["cmask"].shape, np.uint8)
    cv2.fillPoly(hull, [cv2.convexHull(cv2.findNonZero(v["cmask"].astype(np.uint8)))], 1)
    metrics = {"iou": round(iou, 4), "hull": round(float(v["cmask"].sum() / max(1, hull.sum())), 4),
               "w_err": round((bw - cw) / cw, 4), "h_err": round((bh - ch) / ch, 4),
               "edge_mean": round(mean / longer, 4), "edge_p95": round(p95 / longer, 4), "dE": round(dE, 2),
               "colour_miss": round(colour_miss, 4), "flip": flip}
    return metrics, panels(v, shape, concept, C, M, LIT)


def panels(v, shape, concept, C, M, LIT):
    bg = np.uint8(cv2.cvtColor(np.float32([[v["bg"]]]), cv2.COLOR_Lab2BGR)[0, 0] * 255)
    paper = np.empty(shape + (3,), np.uint8)
    paper[:] = bg
    left = paper.copy()
    left[C] = concept[C]
    model = paper.copy()
    a = LIT[..., 3:4].astype(np.float32) / 255
    model = (LIT[..., :3] * a + model * (1 - a)).astype(np.uint8)
    over = np.full(shape + (3,), 255, np.uint8)
    over[C & M] = GREY
    over[C & ~M] = RED
    over[M & ~C] = BLUE
    return np.hstack([left, model, over])


def sheet_image(rows):
    width = max(r.shape[1] for _, r, _ in rows)
    out = []
    for name, img, m in rows:
        text = "%s  IoU %.3f  w %+.1f%%  h %+.1f%%  edge %.1f%% (p95 %.1f%%)  dE %.1f  flip %s" % (
            name, m["iou"], 100 * m["w_err"], 100 * m["h_err"], 100 * m["edge_mean"], 100 * m["edge_p95"], m["dE"], m["flip"])
        bar = np.full((44, width, 3), 255, np.uint8)
        cv2.putText(bar, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 35, 31), 2)
        row = np.full((img.shape[0], width, 3), 255, np.uint8)
        row[:, :img.shape[1]] = img
        out += [bar, row]
    return np.vstack(out)


def compare(concept_json, renders, out_dir, ref="side:w", outline=0):
    cfg = json.load(open(concept_json, encoding="utf8"))
    views = load_views(cfg, renders)
    ref_view, axis = (ref.split(":") + ["w"])[:2]
    if ref_view not in views:
        raise SystemExit("--ref view %s is not in %s" % (ref_view, concept_json))
    r = views[ref_view]
    i = 1 if axis == "w" else 0
    scale = (r["cmask"].shape[i] - 2 * outline) / r["mmask"].shape[i]
    report = {"ref": ref, "scale": round(scale, 5), "outline": outline, "views": {},
              "consistency": {a: round(s, 4) for a, s in consistency(views, outline).items()}}
    rows = []
    for name, v in views.items():
        metrics, img = compare_view(name, v, scale, outline)
        report["views"][name] = metrics
        rows.append((name, img, metrics))
    os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(os.path.join(out_dir, "sheet.png"), sheet_image(rows))
    json.dump(report, open(os.path.join(out_dir, "report.json"), "w", encoding="utf8"), indent=2)
    return report


def main(a):
    opt = lambda name, default: a[a.index(name) + 1] if name in a else default
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))]
    if pos[:1] == ["components"] and len(pos) == 2:
        for i, b in enumerate(components(pos[1], float(opt("--tol", 10)))):
            print(i, list(b))
        return 0
    if pos[:1] == ["check"] and len(pos) == 2:
        outline = int(opt("--outline", 0))
        views = concept_views(json.load(open(pos[1], encoding="utf8")))
        sizes = {n: dict(zip(AXES[n], (v["cmask"].shape[1] - 2 * outline, v["cmask"].shape[0] - 2 * outline))) for n, v in views.items()}
        median = {a: float(np.median([s[a] for s in sizes.values() if a in s])) for a in "LWH"
                  if any(a in s for s in sizes.values())}
        for name, s in sizes.items():
            print("%-6s " % name + ", ".join("%s %d px (%+.1f%% from median)" % (a, s[a], 100 * (s[a] / median[a] - 1)) for a in s))
        for axis, spread in check(pos[1], outline).items():
            print("%s spread across views: %.1f%%" % (axis, 100 * spread))
        drifting = [n for n, s in sizes.items() if any(abs(s[a] / median[a] - 1) > 0.03 for a in s)]
        if drifting:
            print("drifting (over 3%% from the median): %s; leave it out of --gate" % ", ".join(drifting))
        # Side and front are the masters; when they disagree on height the sheet can't be modelled from.
        if "side" in sizes and "front" in sizes:
            gap = abs(sizes["side"]["H"] - sizes["front"]["H"]) / np.mean([sizes["side"]["H"], sizes["front"]["H"]])
            if gap > 0.05:
                print("side and front heights differ by %.1f%%: get a new sheet" % (100 * gap))
                return 1
        return 0
    if len(pos) != 3:
        raise SystemExit(__doc__)
    r = compare(*pos, ref=opt("--ref", "side:w"), outline=int(opt("--outline", 0)))
    min_iou, max_size, max_p95 = float(opt("--min-iou", 0.94)), float(opt("--max-size", 0.03)), float(opt("--max-p95", 0.03))
    max_colour = float(opt("--max-colour", 1))
    # --bar: per-view limits written by calibrate.mjs; its views are the gated ones unless --gate says.
    bar = json.load(open(opt("--bar", ""), encoding="utf8")) if "--bar" in a else {}
    gated = opt("--gate", ",".join(bar or r["views"])).split(",")
    failed = []
    print("%-6s %6s %6s %7s %7s %6s %6s %5s %6s %-5s %s" % ("view", "IoU", "hull", "w", "h", "edge", "p95", "dE", "cmiss", "flip", "gate"))
    for name, m in r["views"].items():
        b = bar.get(name, {"min_iou": min_iou, "max_size": max_size, "max_p95": max_p95, "max_colour": max_colour})
        ok = (m["iou"] >= b["min_iou"] and max(abs(m["w_err"]), abs(m["h_err"])) <= b["max_size"] and m["edge_p95"] <= b["max_p95"]
              and m["colour_miss"] <= b["max_colour"])
        if name in gated and not ok:
            failed.append(name)
        print("%-6s %6.3f %6.3f %+6.1f%% %+6.1f%% %5.1f%% %5.1f%% %5.1f %5.1f%% %-5s %s" % (
            name, m["iou"], m["hull"], 100 * m["w_err"], 100 * m["h_err"], 100 * m["edge_mean"], 100 * m["edge_p95"], m["dE"],
            100 * m["colour_miss"], m["flip"],
            ("PASS" if ok else "FAIL") if name in gated else "(not gated)"))
    for axis, spread in r["consistency"].items():
        print("concept %s spread across views: %.1f%%%s" % (axis, 100 * spread, "  <- the sheet disagrees with itself" if spread > 0.03 else ""))
    print("wrote %s" % os.path.join(pos[2], "sheet.png"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
