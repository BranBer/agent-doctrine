"""Self-check for compare.py on synthetic shapes with known answers; no browser. Run: python -I test_compare.py"""
import json, os, subprocess, sys, tempfile

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare  # noqa: E402

BG = (216, 228, 232)        # BGR of a flat cream sheet
YELLOW = (61, 194, 255)     # #FFC23D
NAVY = (64, 35, 31)         # #1F2340


def draw(img, rects, outline):
    """Yellow rectangles inside an ink band exactly `outline` px wide, all of it outside the fill."""
    for x0, y0, x1, y1 in rects:
        cv2.rectangle(img, (x0 - outline, y0 - outline), (x1 + outline, y1 + outline), NAVY, -1)
    for x0, y0, x1, y1 in rects:
        cv2.rectangle(img, (x0, y0), (x1, y1), YELLOW, -1)


def car(img, x, y, scale=1.0, nose_left=True, tall=1.0, outline=3):
    """A side profile: a 400x200 body with an 150x80 cab over its nose half, bottom-left at (x, y)."""
    s = scale
    bw, bh, cw, ch = int(400 * s), int(200 * s * tall), int(150 * s), int(80 * s)
    body = (x, y - bh, x + bw, y)
    cx = x + int(40 * s) if nose_left else x + bw - int(40 * s) - cw
    cab = (cx, y - bh - ch, cx + cw, y - bh)
    draw(img, (body, cab), outline)


def nose(img, x, y, scale=1.0, tall=1.0, outline=3):
    """A front profile: a 180x200 body under a centred 120x80 cab."""
    s = scale
    bw, bh, cw, ch = int(180 * s), int(200 * s * tall), int(120 * s), int(80 * s)
    body = (x, y - bh, x + bw, y)
    cab = (x + (bw - cw) // 2, y - bh - ch, x + (bw + cw) // 2, y - bh)
    draw(img, (body, cab), outline)


def sheet(path, front_tall=1.0):
    img = np.full((800, 1200, 3), BG, np.uint8)
    car(img, 100, 400)
    nose(img, 700, 400, tall=front_tall)
    cv2.putText(img, "SIDE", (100, 700), cv2.FONT_HERSHEY_SIMPLEX, 2, NAVY, 4)  # a label outside every rect
    cv2.imwrite(path, img)
    return {"sheet": path, "views": {"side": [60, 60, 480, 380], "front": [660, 60, 260, 380]}}


def renders(d, side_kw=None, front_kw=None):
    """Model renders at half scale on transparent, with no outline, as views.mjs writes them."""
    os.makedirs(d, exist_ok=True)
    for name, draw, kw in (("side", car, side_kw or {}), ("front", nose, front_kw or {})):
        rgb = np.zeros((512, 512, 3), np.uint8)
        draw(rgb, 40, 400, scale=0.5, outline=0, **kw)
        alpha = np.where(rgb.any(axis=2), 255, 0).astype(np.uint8)
        rgba = np.dstack([rgb, alpha])
        cv2.imwrite(os.path.join(d, name + ".png"), rgba)
        cv2.imwrite(os.path.join(d, name + ".flat.png"), rgba)
    json.dump({"size": 512, "pxPerUnit": 50, "views": {"side": {}, "front": {}}}, open(os.path.join(d, "views.json"), "w"))


T = tempfile.mkdtemp()
cfg = sheet(os.path.join(T, "sheet.png"))
json.dump(cfg, open(os.path.join(T, "concept.json"), "w"))

# a faithful model scores near 1 in every view, with tiny size errors and matching colour
renders(os.path.join(T, "good"))
r = compare.compare(os.path.join(T, "concept.json"), os.path.join(T, "good"), os.path.join(T, "out-good"), outline=3)
for v in ("side", "front"):
    m = r["views"][v]
    assert m["iou"] >= 0.985, (v, m)  # the outline is added back exactly once
    assert abs(m["w_err"]) < 0.006 and abs(m["h_err"]) < 0.006, (v, m)
    assert m["flip"] == "none", (v, m)
    assert m["edge_mean"] < 0.01, (v, m)
assert r["views"]["side"]["dE"] < 8, r["views"]["side"]
# the hull floor: the concept against its own convex hull; the stepped side profile sits well under 1
assert 0.85 < r["views"]["side"]["hull"] < 0.99 and r["views"]["side"]["iou"] > r["views"]["side"]["hull"], r["views"]["side"]
assert os.path.exists(os.path.join(T, "out-good", "sheet.png"))
assert r["consistency"]["H"] < 0.02, r["consistency"]

# the concept's true outline width (3 px outside the silhouette) matches better than one either side of it
iou = {o: compare.compare(os.path.join(T, "concept.json"), os.path.join(T, "good"), os.path.join(T, "o%d" % o),
                          outline=o)["views"]["side"]["iou"] for o in (2, 3, 4)}
assert iou[3] >= iou[2] and iou[3] > iou[4], iou

# a model built facing the other way is matched mirrored, and the mirror is reported
renders(os.path.join(T, "mirrored"), side_kw={"nose_left": False})
r = compare.compare(os.path.join(T, "concept.json"), os.path.join(T, "mirrored"), os.path.join(T, "out-m"), outline=3)
assert r["views"]["side"]["flip"] == "h" and r["views"]["side"]["iou"] >= 0.97, r["views"]["side"]

# a body 10% too tall shows as a height error against the side view's length
renders(os.path.join(T, "tall"), side_kw={"tall": 1.1}, front_kw={"tall": 1.1})
r = compare.compare(os.path.join(T, "concept.json"), os.path.join(T, "tall"), os.path.join(T, "out-t"), outline=3)
assert 0.05 < r["views"]["side"]["h_err"] < 0.10, r["views"]["side"]
assert r["views"]["side"]["iou"] < 0.95, r["views"]["side"]

# the CLI's default gates (IoU 0.94, size 3%, outline p95 3%) pass a faithful model and fail a tall one
cli = [sys.executable, "-I", os.path.join(HERE, "compare.py"), os.path.join(T, "concept.json")]
run = lambda renders, out, *extra: subprocess.run(cli + [os.path.join(T, renders), os.path.join(T, out), "--outline", "3", *extra],
                                                  capture_output=True, text=True)
assert run("good", "o2").returncode == 0
assert run("tall", "o1").returncode == 1
assert run("tall", "o1", "--min-iou", "0.5", "--max-size", "0.2", "--max-p95", "0.2").returncode == 0

# a 4% height error fails the size gate even while IoU stays high, and --gate leaves that view out
renders(os.path.join(T, "tall4"), side_kw={"tall": 1.06})
r = compare.compare(os.path.join(T, "concept.json"), os.path.join(T, "tall4"), os.path.join(T, "o3"), outline=3)
assert r["views"]["side"]["iou"] > 0.94 and r["views"]["side"]["h_err"] > 0.03, r["views"]["side"]
failed = run("tall4", "o3")
assert failed.returncode == 1 and "FAIL" in failed.stdout, failed.stdout
assert run("tall4", "o3", "--gate", "front").returncode == 0

# components finds both drawings and the label, largest first
boxes = compare.components(os.path.join(T, "sheet.png"))
assert len(boxes) >= 3, boxes
x, y, w, h = boxes[0]
assert abs(x - 98) <= 4 and abs(w - 404) <= 6 and abs(h - 284) <= 6, boxes[0]

# a concept whose front view is 10% taller than its side view is flagged as inconsistent
cfg = sheet(os.path.join(T, "sheet2.png"), front_tall=1.1)
json.dump(cfg, open(os.path.join(T, "concept2.json"), "w"))
r = compare.compare(os.path.join(T, "concept2.json"), os.path.join(T, "good"), os.path.join(T, "out-c"), outline=3)
assert 0.05 < r["consistency"]["H"] < 0.10, r["consistency"]

# check reads the same consistency from the sheet alone, before any model exists
c = compare.check(os.path.join(T, "concept2.json"), outline=3)
assert abs(c["H"] - r["consistency"]["H"]) < 1e-3, (c, r["consistency"])

print("ok")
