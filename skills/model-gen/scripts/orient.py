"""Turns a GLB about +Y by wrapping its scene in one rotated node; the meshes are not touched.

  python -I orient.py <in.glb> <out.glb> [--yaw -90]

Tripo exports face +X; glTF and model-qa expect the front toward +Z, which is --yaw -90.
A wrapper node keeps the rotation a plain transform, so a later rig or re-export is unaffected.
"""
import json, math, struct, sys


def read_glb(path):
    raw = open(path, "rb").read()
    magic, version, _ = struct.unpack_from("<III", raw, 0)
    if magic != 0x46546C67 or version != 2:
        raise SystemExit("%s is not a glTF 2 binary" % path)
    chunks, off = [], 12
    while off < len(raw):
        n, kind = struct.unpack_from("<II", raw, off)
        chunks.append((kind, raw[off + 8:off + 8 + n]))
        off += 8 + n
    return json.loads(chunks[0][1]), chunks[1:]


def write_glb(path, doc, rest):
    js = json.dumps(doc, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js
    for kind, data in rest:
        body += struct.pack("<II", len(data), kind) + data
    open(path, "wb").write(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


def yaw(doc, degrees):
    s = doc["scenes"][doc.get("scene", 0)]
    half = math.radians(degrees) / 2
    doc["nodes"].append({"name": "orient", "rotation": [0, math.sin(half), 0, math.cos(half)], "children": s["nodes"]})
    s["nodes"] = [len(doc["nodes"]) - 1]
    return doc


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    doc, rest = read_glb(a[0])
    write_glb(a[1], yaw(doc, float(a[a.index("--yaw") + 1]) if "--yaw" in a else -90), rest)
    print("wrote", a[1])
