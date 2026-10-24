"""Concept art via OpenRouter, for any project. Reference only: concepts never ship in a build.

  python -I concept.py <slug> "<prompt>" [--n 2] [--model M] [--aspect 16:9] [--ref art/concept/x.png]... [--dry-run]
  python -I concept.py pick <file> "<one-sentence reason>"

Run from the project root (or set CONCEPT_ROOT). The project's rendering rules live in
art/house-style.md and are appended to every prompt, so every concept shares one look. Writes
art/concept/<slug>-N.png, numbering on from any earlier run, and appends every call (with each file's
sha256) and every pick to art/provenance.jsonl. --dry-run prints the request instead of sending it. With no --model, MODELS are tried in order, moving on only when one is
rate-limited or unavailable. The key comes from OPEN_ROUTER_API_KEY in the environment, else the
Windows user environment, and is never printed.
"""
import base64, datetime, glob, hashlib, json, os, re, sys, urllib.error, urllib.request

ROOT = os.environ.get("CONCEPT_ROOT") or os.getcwd()
OUT = os.path.join(ROOT, "art", "concept")
LOG = os.path.join(ROOT, "art", "provenance.jsonl")
STYLE = os.path.join(ROOT, "art", "house-style.md")
MODELS = ["google/gemini-3-pro-image", "google/gemini-nano-banana-2.1"]


def key():
    k = os.environ.get("OPEN_ROUTER_API_KEY")
    if not k and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
                k = winreg.QueryValueEx(h, "OPEN_ROUTER_API_KEY")[0]
        except OSError:
            pass
    if not k:
        raise SystemExit("OPEN_ROUTER_API_KEY is not set")
    return k


def house_style():
    if not os.path.exists(STYLE):
        raise SystemExit("write the project's rendering rules to %s first" % STYLE.replace("\\", "/"))
    return open(STYLE, encoding="utf8").read().strip()


def build_body(prompt, model, aspect, refs):
    parts = [{"type": "text", "text": "%s\n\nSTYLE: %s" % (prompt, house_style())}]
    for r in refs:
        b64 = base64.b64encode(open(r, "rb").read()).decode()
        parts.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}})
    return {"model": model, "modalities": ["image", "text"], "image_config": {"aspect_ratio": aspect},
            "messages": [{"role": "user", "content": parts}]}


def openrouter(body):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.load(r)


def log(record):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    record = {"at": datetime.datetime.now().isoformat(timespec="seconds"), **record}
    with open(LOG, "a", encoding="utf8") as f:
        f.write(json.dumps(record) + "\n")


def call(prompt, models, aspect, refs, post):
    """First model that answers wins; 429/503 move on to the next, anything else is raised."""
    for i, m in enumerate(models):
        try:
            return m, post(build_body(prompt, m, aspect, refs))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or i == len(models) - 1:
                raise
            print("%s returned %d, trying %s" % (m, e.code, models[i + 1]))


def next_index(slug):
    taken = [int(m.group(1)) for p in glob.glob(os.path.join(OUT, glob.escape(slug) + "-*.png"))
             if (m := re.fullmatch(re.escape(slug) + r"-(\d+)[a-z]?\.png", os.path.basename(p)))]
    return max(taken, default=0) + 1


def generate(slug, prompt, n=1, model=None, aspect="16:9", refs=(), post=None):
    os.makedirs(OUT, exist_ok=True)
    models = [model] if model else MODELS
    written = []
    for _ in range(n):
        try:
            used, d = call(prompt, models, aspect, refs, post or openrouter)
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, (e.read() if e.fp else b"")[:500].decode("utf8", "replace"))
            continue
        msg = d["choices"][0]["message"]
        i = next_index(slug)
        files, hashes = [], {}
        for k, img in enumerate(msg.get("images") or []):
            raw = base64.b64decode(img["image_url"]["url"].split(",", 1)[1])
            p = os.path.join(OUT, "%s-%d%s.png" % (slug, i, chr(97 + k) if k else ""))
            open(p, "wb").write(raw)
            files.append(os.path.relpath(p, ROOT).replace("\\", "/"))
            hashes[files[-1]] = hashlib.sha256(raw).hexdigest()
        if not files:
            print("no image returned:", (msg.get("content") or "")[:300])
        log({"slug": slug, "model": used, "aspect": aspect, "refs": list(refs),
             "prompt": build_body(prompt, used, aspect, [])["messages"][0]["content"][0]["text"],
             "files": files, "sha256": hashes, "usage": d.get("usage")})
        written += files
    return written


def dry_run(prompt, model, aspect, refs):
    """The request that would be sent first, for reviewing a prompt without spending anything."""
    return build_body(prompt, model or MODELS[0], aspect, refs)


def pick(file, reason):
    log({"pick": file, "reason": reason})


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pick"] and len(a) == 3:
        pick(a[1], a[2])
        raise SystemExit(0)
    if len(a) < 2:
        raise SystemExit(__doc__)
    opt = lambda name, default: a[a.index(name) + 1] if name in a else default
    refs = [a[i + 1] for i, x in enumerate(a) if x == "--ref"]
    if "--dry-run" in a:
        body = dry_run(a[1], opt("--model", None), opt("--aspect", "16:9"), refs)
        for part in body["messages"][0]["content"]:
            if part["type"] == "image_url":
                part["image_url"]["url"] = part["image_url"]["url"][:40] + "..."
        print(json.dumps(body, indent=2))
        raise SystemExit(0)
    for p in generate(a[0], a[1], int(opt("--n", 1)), opt("--model", None), opt("--aspect", "16:9"), refs):
        print("wrote", p)
