"""End-to-end check of glb.mjs and views.mjs on fixtures/box.mjs (1 wide, 2.5 tall with its cap, 4 long,
pink cap at the nose). Needs Playwright's Chromium. Run: python -I test_views.py"""
import json, os, subprocess, tempfile

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = tempfile.mkdtemp()
glb, out = os.path.join(T, "box.glb"), os.path.join(T, "views")

subprocess.run(["node", os.path.join(HERE, "glb.mjs"), os.path.join(HERE, "fixtures", "box.mjs"), glb], check=True)
assert open(glb, "rb").read(4) == b"glTF"
subprocess.run(["node", os.path.join(HERE, "views.mjs"), glb, out, "--size", "512"], check=True)

meta = json.load(open(os.path.join(out, "views.json")))
d = meta["dims"]
assert abs(d["x"] - 1) < 1e-3 and abs(d["y"] - 2.5) < 1e-3 and abs(d["z"] - 4) < 1e-3, d
ppu = meta["pxPerUnit"]


def bbox(view):
    a = cv2.imread(os.path.join(out, view + ".png"), cv2.IMREAD_UNCHANGED)[..., 3]
    ys, xs = np.nonzero(a > 127)
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, xs.mean(), a.shape[1]


# one shared scale: each view's size in pixels is its true size times pxPerUnit
for view, (w, h) in {"side": (4, 2.5), "front": (1, 2.5), "back": (1, 2.5), "top": (4, 1)}.items():
    bw, bh, _, _ = bbox(view)
    assert abs(bw - w * ppu) <= 2 and abs(bh - h * ppu) <= 2, (view, bw, bh, w * ppu, h * ppu)


def pink_x(view):
    img = cv2.imread(os.path.join(out, view + ".flat.png"), cv2.IMREAD_UNCHANGED)
    pink = (np.abs(img[..., :3].astype(int) - (0x8E, 0x4F, 0xE6)).sum(axis=2) < 12) & (img[..., 3] > 127)
    return np.nonzero(pink)[1].mean(), img.shape[1] / 2


# the nose (pink cap) points left in the side and top views
for view in ("side", "top"):
    x, centre = pink_x(view)
    assert x < centre, (view, x, centre)

# a perspective three-quarter hero view comes with every run, for people to look at
hero = cv2.imread(os.path.join(out, "hero.png"), cv2.IMREAD_UNCHANGED)
assert hero is not None and (hero[..., 3] > 127).mean() > 0.05, "hero view missing or empty"
assert "hero" not in [v for v in meta["views"] if not meta["views"][v].get("perspective")]

# the unlit pass keeps the material's own colour (#3D63DD)
flat = cv2.imread(os.path.join(out, "front.flat.png"), cv2.IMREAD_UNCHANGED)
b, g, r, _ = flat[flat.shape[0] // 2 + int(0.6 * ppu), flat.shape[1] // 2]
assert abs(int(r) - 0x3D) <= 3 and abs(int(g) - 0x63) <= 3 and abs(int(b) - 0xDD) <= 3, (r, g, b)

print("ok")
