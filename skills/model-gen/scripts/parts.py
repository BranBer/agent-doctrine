"""Paints each part of a parts or segmented GLB its own colour and spreads the parts apart, to see what was split.

  python -I parts.py <in.glb> <out.glb> [--spread 0.6]

Prints each part's name, colour and box (height, across, depth in the model's own frame), then writes a
copy turned to face +Z, ready for model-qa's views.mjs. Look at the hero view: a gear piece that came out
on its own (a helmet, a shoulder plate) is one colour; one fused to the body shares a colour with it.
"""
import colorsys, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orient import read_glb, write_glb, yaw  # noqa: E402


def explode(doc, spread=0.6):
    acc, doc["materials"], rows = doc["accessors"], [], []
    meshed = [n for n in doc["nodes"] if "mesh" in n]
    for i, node in enumerate(meshed):
        rgb = colorsys.hsv_to_rgb(i / len(meshed) * 0.93, 0.75, 0.95)
        doc["materials"].append({"name": node.get("name", "part%d" % i), "pbrMetallicRoughness": {
            "baseColorFactor": [*rgb, 1], "metallicFactor": 0, "roughnessFactor": 1}})
        for p in doc["meshes"][node["mesh"]]["primitives"]:
            p["material"] = len(doc["materials"]) - 1
        a = acc[doc["meshes"][node["mesh"]]["primitives"][0]["attributes"]["POSITION"]]
        t, s = node.get("translation", [0, 0, 0]), node.get("scale", [1, 1, 1])
        lo = [a["min"][k] * s[k] + t[k] for k in range(3)]
        hi = [a["max"][k] * s[k] + t[k] for k in range(3)]
        c = [(lo[k] + hi[k]) / 2 for k in range(3)]
        # ponytail: spreads by box centre, ignores node rotation; Tripo's parts carry none
        node["translation"] = [t[0] + c[0] * spread, t[1] + c[1] * spread / 2, t[2] + c[2] * spread]
        rows.append((node.get("name", "part%d" % i), rgb, lo, hi))
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    doc, rest = read_glb(a[0])
    for name, rgb, lo, hi in explode(doc, float(a[a.index("--spread") + 1]) if "--spread" in a else 0.6):
        print("%-14s #%02x%02x%02x  height %+.2f..%+.2f  across %+.2f..%+.2f  depth %+.2f..%+.2f" % (
            name, *(round(v * 255) for v in rgb), lo[1], hi[1], lo[2], hi[2], lo[0], hi[0]))
    write_glb(a[1], yaw(doc, -90), rest)
    print("wrote", a[1])
