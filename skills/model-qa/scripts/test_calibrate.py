"""End-to-end check of calibrate.mjs on fixtures/box.mjs, scored against a sheet made from the box's own
renders, so the good model matches exactly and every fault has a known size. Run: python -I test_calibrate.py"""
import json, os, subprocess, tempfile

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = tempfile.mkdtemp()
glb = os.path.join(T, "box.glb")
subprocess.run(["node", os.path.join(HERE, "glb.mjs"), os.path.join(HERE, "fixtures", "box.mjs"), glb], check=True)
subprocess.run(["node", os.path.join(HERE, "views.mjs"), glb, os.path.join(T, "r"), "--size", "400", "--views", "side,front"], check=True)

# The "concept": the good renders pasted onto a flat grey sheet.
sheet = np.full((440, 880, 3), 238, np.uint8)
views = {}
for i, name in enumerate(("side", "front")):
    rgba = cv2.imread(os.path.join(T, "r", name + ".png"), cv2.IMREAD_UNCHANGED)
    a = rgba[..., 3:] / 255
    x = 20 + i * 440
    sheet[20:420, x:x + 400] = (rgba[..., :3] * a + sheet[20:420, x:x + 400] * (1 - a)).astype(np.uint8)
    views[name] = [x, 20, 400, 400]
cv2.imwrite(os.path.join(T, "sheet.png"), sheet)
json.dump({"sheet": os.path.join(T, "sheet.png"), "views": views}, open(os.path.join(T, "concept.json"), "w"))

out = os.path.join(T, "cal")
run = subprocess.run(["node", os.path.join(HERE, "calibrate.mjs"), os.path.join(HERE, "fixtures", "box.mjs"),
                      os.path.join(T, "concept.json"), out, "--size", "400"], capture_output=True, text=True)
assert run.returncode == 0, run.stdout + run.stderr
cal = json.load(open(os.path.join(out, "calibration.json")))
faults = {f["fault"]: f for f in cal["faults"]}

# the good model passes; every named part gets a shrunk and a removed fault, plus whole-model faults
assert cal["good"]["pass"], cal["good"]
for name in ("body-small", "body-gone", "cap-small", "cap-gone", "long", "narrow", "low"):
    assert name in faults, (name, list(faults))
# removing the cap (a fifth of the height) is caught
assert faults["cap-gone"]["caught"], faults["cap-gone"]
# the suggested bar is per view, just inside the good model's own numbers, written to bar.json
bar = json.load(open(os.path.join(out, "bar.json")))
for view, b in bar.items():
    g = cal["good"]["views"][view]
    assert b["min_iou"] <= g["iou"] and b["max_p95"] >= g["edge_p95"] and b["max_colour"] >= g["colour_miss"], (view, b, g)
assert faults["cap-gone"]["caughtBySuggested"], faults["cap-gone"]
assert "catches" in run.stdout and "--bar" in run.stdout, run.stdout

# compare.py gates with that bar: the good model passes, the model without its cap fails
cmp = lambda d: subprocess.run(["python", "-I", os.path.join(HERE, "compare.py"), os.path.join(T, "concept.json"),
                                os.path.join(out, d), os.path.join(out, d, "regate"), "--bar", os.path.join(out, "bar.json")],
                               capture_output=True, text=True)
assert cmp("good").returncode == 0, cmp("good").stdout
assert cmp("cap-gone").returncode == 1

print("ok")
