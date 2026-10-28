"""End-to-end check of symmetry.mjs on fixtures/racked.mjs: the centred model passes; its roof rack 56 mm off the centre
line, the fault the check exists for, fails both the mirrored front view and the rack's centre; a mirror 10 mm out of
line with its twin fails; the antenna it declares one-sided is left out. Needs Playwright's Chromium.
Run: python -I test_symmetry.py"""
import json, os, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T = tempfile.mkdtemp()


def check(name, args):
    glb = os.path.join(T, name + ".glb")
    subprocess.run(["node", os.path.join(HERE, "glb.mjs"), os.path.join(HERE, "fixtures", "racked.mjs"), glb, "--args", json.dumps(args)],
                   check=True)
    out = os.path.join(T, name)
    run = subprocess.run(["node", os.path.join(HERE, "symmetry.mjs"), glb, out, "--size", "512"], capture_output=True, text=True)
    return run, json.load(open(os.path.join(out, "symmetry.json")))


# the centred model passes, every pair is judged once, and the one-sided antenna is neither rendered nor judged
run, r = check("centred", {})
assert run.returncode == 0, run.stdout + run.stderr
assert r["views"]["front"]["iou"] >= 0.995 and r["views"]["top"]["iou"] >= 0.995, r["views"]
assert r["parts"]["roof-rack"] == {**r["parts"]["roof-rack"], "check": "centred", "pass": True}, r["parts"]
assert r["parts"]["mirror-left"]["check"] == "pair" and r["parts"]["mirror-left"]["pass"], r["parts"]
assert "mirror-right" not in r["parts"], r["parts"]
assert r["parts"]["antenna"]["check"] == "one-sided" and r["dropped"] == ["antenna"], r
assert os.path.exists(os.path.join(T, "centred", "symmetry.png"))

# the rack 56 mm to one side: the mirrored front view and the rack's own centre both see it, and nothing else fails
run, r = check("offset", {"rackX": 0.056})
assert run.returncode == 1 and "roof-rack" in run.stdout, run.stdout
assert r["views"]["front"]["iou"] < 0.995, r["views"]
assert not r["parts"]["roof-rack"]["pass"] and abs(r["parts"]["roof-rack"]["error"] - 0.056) < 1e-3, r["parts"]["roof-rack"]
assert all(p.get("pass", True) for n, p in r["parts"].items() if n != "roof-rack"), r["parts"]

# a twin 10 mm out of line fails its pair, though its silhouette barely moves
run, r = check("gap", {"mirrorGap": 0.01})
assert run.returncode == 1 and not r["parts"]["mirror-left"]["pass"], r["parts"]
assert abs(r["parts"]["mirror-left"]["error"] - 0.01) < 1e-4, r["parts"]["mirror-left"]

print("ok")
