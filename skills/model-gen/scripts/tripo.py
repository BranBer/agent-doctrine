"""Tripo API client for generating game models from concept sheets. Prepaid API credits only.

  python -I tripo.py balance
  python -I tripo.py run <asset> <endpoint> '<json body>' [--view front=path]... [--tex-view front=path]...
                                                        [--file path] [--from task_id] [--yes]
  python -I tripo.py wait <asset> <task_id>
  python -I tripo.py recent

Run from the project root (or set TRIPO_ROOT). `run` uploads any --view (multiview `inputs`), --tex-view
(a repaint's `texture_prompt.images`) or --file (`input`) images, or sets `input` to a previous task (--from), then prints the estimated credits. Without
--yes it stops there: a paid call needs an explicit yes. With --yes it creates the task, waits for it,
downloads every output into art/gen/<asset>/<task_id>/ with task.json, and appends the call, the input
hashes, the actual credits and the files to art/provenance.jsonl.

Exit codes: 0 done, 2 not confirmed (estimate shown), 3 still running after the wait (resume with
`wait`, never run again), 4 task failed, 5 API error. A create that times out or returns 500 is never
retried, because the task may exist: check `recent` first. The key comes from TRIPO_API_KEY in the
environment, else the Windows user environment, and is never printed.
"""
import datetime, hashlib, json, os, sys, time, urllib.error, urllib.parse, urllib.request, uuid

BASE = "https://openapi.tripo3d.ai/v3"
ROOT = os.environ.get("TRIPO_ROOT") or os.getcwd()
LOG = os.path.join(ROOT, "art", "provenance.jsonl")
TERMS = "2026-11-13"  # the Tripo terms in force when this client was written; re-read them when they change

# Credits per call from developers.tripo3d.ai/en/pricing (read 2026-11-15). P-series prices are from the
# changelog (2026-08) and match the 110 charged for a textured P2 multiview on 2026-11-15.
GEN_BASE = {"text-to-model": (10, 20), "image-to-model": (20, 30), "multiview-to-model": (20, 30)}
TEXTURE_ADDONS = {("texture_quality", "detailed"): 10, ("texture_quality", "extreme"): 20}
GEN_ADDONS = {**TEXTURE_ADDONS, ("geometry_quality", "detailed"): 20, ("quad", True): 5,
              ("smart_low_poly", True): 10, ("generate_parts", True): 20}
P_SERIES = (100, 110)  # untextured, textured
FLAT = {"mesh/uv": 20, "mesh/segment": 40, "animations/rig-check": 0, "animations/rig": 25}
SAFE_429 = (1007, 2000)


def estimate(endpoint, body):
    """Credits the call should cost, from the published price table (actual charge is in task.json)."""
    name = endpoint.split("/")[-1]
    if name in GEN_BASE:
        textured = body.get("texture", True) or body.get("pbr", True)
        if str(body.get("model", "")).startswith("P"):
            return P_SERIES[textured] + sum(c for (k, v), c in TEXTURE_ADDONS.items() if body.get(k) == v)
        return GEN_BASE[name][1 if textured else 0] + sum(c for (k, v), c in GEN_ADDONS.items() if body.get(k) == v)
    if endpoint in FLAT:
        return FLAT[endpoint]
    if endpoint == "models/texture":
        return {"detailed": 20, "extreme": 30}.get(body.get("texture_quality"), 10)
    if endpoint == "models/convert":
        advanced = ("quad", "face_limit", "flatten_bottom", "flatten_bottom_threshold", "texture_size",
                    "texture_format", "pivot_to_center_bottom", "scale_factor")
        return 10 if any(k in body for k in advanced) else 5
    if endpoint == "mesh/decimate":
        v = body.get("model", "v2.0")
        return {"v3.0": 40 if body.get("quad") else 35, "v2.0": 30, "v1.0": 10}[v]
    if endpoint == "mesh/complete":
        return 30 if body.get("completion_mode") == "quick_cap" else 50
    if endpoint == "animations/retarget":
        return 10 * len(body.get("animations") or [body.get("animation")])
    raise SystemExit("no price known for %s; add it to tripo.py before spending" % endpoint)


def key():
    k = os.environ.get("TRIPO_API_KEY")
    if not k and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
                k = winreg.QueryValueEx(h, "TRIPO_API_KEY")[0]
        except OSError:
            pass
    if not k:
        raise SystemExit("TRIPO_API_KEY is not set")
    return k


class ApiError(Exception):
    def __init__(self, status, payload):
        super().__init__("HTTP %s: %s" % (status, json.dumps(payload)[:400]))
        self.status, self.code = status, (payload or {}).get("code")


class Http:
    """The only part that touches the network; tests replace it."""

    def call(self, method, path, body=None, upload=None):
        headers = {"Authorization": "Bearer " + key()}
        data = None
        if upload:
            boundary = uuid.uuid4().hex
            name = os.path.basename(upload)
            data = (("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                     "Content-Type: application/octet-stream\r\n\r\n" % (boundary, name)).encode()
                    + open(upload, "rb").read() + ("\r\n--%s--\r\n" % boundary).encode())
            headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
        elif body is not None:
            data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
        req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                payload = json.load(e)
            except ValueError:
                payload = {}
            raise ApiError(e.code, payload) from None

    def download(self, url, path):
        with urllib.request.urlopen(url, timeout=300) as r, open(path, "wb") as f:
            f.write(r.read())


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def log(record):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    record = {"at": datetime.datetime.now().isoformat(timespec="seconds"), "vendor": "tripo-api", **record}
    with open(LOG, "a", encoding="utf8") as f:
        f.write(json.dumps(record) + "\n")


def upload(http, path):
    return http.call("POST", "/files", upload=path)["data"]["file_token"]


def create(http, endpoint, body):
    """429 waits and retries; anything else is raised, because a lost response may hide a real task."""
    for attempt in range(5):
        try:
            return http.call("POST", "/" + endpoint, body)["data"]["task_id"]
        except ApiError as e:
            if e.status != 429 and e.code not in SAFE_429:
                raise
            time.sleep(2 ** attempt * 2)
    raise SystemExit("still rate-limited after 5 tries; nothing was created")


def wait(http, asset, task_id, timeout=900, every=3, sleep=time.sleep):
    """Polls until the task ends, downloads every output URL, and returns (task, files)."""
    waited = 0
    while True:
        t = http.call("GET", "/tasks/" + task_id)["data"]
        if t["status"] in ("success", "failed", "cancelled", "banned", "expired"):
            break
        if waited >= timeout:
            print("task %s still %s at %d%%; resume with: tripo.py wait %s %s" % (task_id, t["status"], t.get("progress", 0), asset, task_id))
            raise SystemExit(3)
        sleep(every)
        waited += every
    out = os.path.join(ROOT, "art", "gen", asset, task_id)
    os.makedirs(out, exist_ok=True)
    json.dump(t, open(os.path.join(out, "task.json"), "w"), indent=1)
    files = {}
    for k, url in (t.get("output") or {}).items():
        if isinstance(url, str) and url.startswith("http"):
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".bin"
            p = os.path.join(out, k.replace("_url", "") + ext)
            http.download(url, p)
            files[os.path.relpath(p, ROOT).replace("\\", "/")] = sha(p)
    return t, files


def run(http, asset, endpoint, body, views=(), file=None, source=None, yes=False, sleep=time.sleep, tex_views=()):
    cost = estimate(endpoint, body)
    inputs = {p: sha(p) for _, p in [*views, *tex_views]} | ({file: sha(file)} if file else {})
    print("%s on %s: about %d credits ($%.2f)" % (endpoint, asset, cost, cost / 100))
    if not yes:
        print(json.dumps({**body, **({"inputs": [v for v, _ in views]} if views else {})}, indent=1))
        print("not sent: add --yes to spend")
        return 2
    balance = http.call("GET", "/account/balance")["data"]["balance"]
    if balance < cost:
        raise SystemExit("balance %.0f is below the estimate %d" % (balance, cost))
    if views:
        body["inputs"] = [{v: upload(http, p)} for v, p in views]
    if tex_views:
        body["texture_prompt"] = {"images": [{v: upload(http, p)} for v, p in tex_views]}
    if file:
        body["input"] = upload(http, file)
    if source:
        body["input"] = source
    task_id = create(http, endpoint, body)
    print("task", task_id)
    t, files = wait(http, asset, task_id, sleep=sleep)
    log({"asset": asset, "endpoint": endpoint, "body": body, "inputs": inputs, "task_id": task_id,
         "status": t["status"], "estimate": cost, "credits": t.get("credits_consumed"), "files": files,
         "terms": TERMS})
    if t["status"] != "success":
        print("failed:", t.get("error_code"), t.get("error_message"))
        return 4
    for f in files:
        print("wrote", f)
    print("credits", t.get("credits_consumed"))
    return 0


def main(a):
    http = Http()
    try:
        if a[:1] == ["balance"]:
            print(http.call("GET", "/account/balance")["data"])
            return 0
        if a[:1] == ["recent"]:
            for row in http.call("GET", "/account/usage")["data"][:10]:
                print(row)
            return 0
        if a[:1] == ["wait"] and len(a) == 3:
            t, files = wait(http, a[1], a[2])
            log({"asset": a[1], "task_id": a[2], "status": t["status"], "credits": t.get("credits_consumed"),
                 "files": files, "resumed": True, "terms": TERMS})
            print(t["status"], "credits", t.get("credits_consumed"), *files)
            return 0 if t["status"] == "success" else 4
        if a[:1] == ["run"] and len(a) >= 4:
            def opt(name):
                return a[a.index(name) + 1] if name in a else None
            def pairs(flag):
                return [tuple(a[i + 1].split("=", 1)) for i, x in enumerate(a) if x == flag]
            return run(http, a[1], a[2], json.loads(a[3]), pairs("--view"), opt("--file"), opt("--from"), "--yes" in a,
                       tex_views=pairs("--tex-view"))
    except ApiError as e:
        print(e)
        return 5
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
