"""python -I test_tripo.py - runs tripo.py against a fake API; spends nothing."""
import json, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
tmp = tempfile.mkdtemp()
os.environ["TRIPO_ROOT"] = tmp
import tripo  # noqa: E402


class Fake:
    def __init__(self, statuses=("running", "success"), create_error=None):
        self.calls, self.statuses, self.create_error = [], list(statuses), create_error

    def call(self, method, path, body=None, upload=None):
        self.calls.append((method, path, upload))
        if path == "/account/balance":
            return {"data": {"balance": 5000}}
        if path == "/files":
            return {"data": {"file_token": "tok-" + os.path.basename(upload)}}
        if method == "POST":
            if self.create_error:
                err, self.create_error = self.create_error, self.create_error[2:] or None
                raise tripo.ApiError(err[0], {"code": err[1]})
            return {"data": {"task_id": "t1"}}
        s = self.statuses.pop(0)
        return {"data": {"task_id": "t1", "status": s, "progress": 50, "credits_consumed": 40,
                         "output": {"model_url": "https://x/m.glb?sig=1", "rendered_image_url": "https://x/r.webp"} if s == "success" else None}}

    def download(self, url, path):
        open(path, "wb").write(url.encode())


def test_estimates():
    assert tripo.estimate("generation/multiview-to-model", {"model": "v3.1-20260211", "smart_low_poly": True}) == 40
    assert tripo.estimate("generation/multiview-to-model", {"model": "v3.1-20260211", "texture": False, "pbr": False, "generate_parts": True}) == 40
    assert tripo.estimate("generation/multiview-to-model", {"model": "P2-20260801", "pbr": False}) == 110
    assert tripo.estimate("generation/multiview-to-model", {"model": "P2-20260801", "texture": False, "pbr": False}) == 100
    assert tripo.estimate("generation/multiview-to-model", {"model": "P2-20260801", "texture_quality": "detailed"}) == 120
    assert tripo.estimate("animations/retarget", {"animations": ["preset:idle", "preset:run"]}) == 20
    assert tripo.estimate("models/convert", {"format": "GLTF"}) == 5
    assert tripo.estimate("models/convert", {"format": "GLTF", "texture_size": 1024}) == 10


def test_unconfirmed_spends_nothing():
    http = Fake()
    img = os.path.join(tmp, "front.png"); open(img, "wb").write(b"png")
    assert tripo.run(http, "tank", "generation/multiview-to-model", {"model": "v3.1-20260211"}, [("front", img)]) == 2
    assert http.calls == []


def test_run_uploads_waits_downloads_and_logs():
    http = Fake()
    front, left = (os.path.join(tmp, n) for n in ("front.png", "left.png"))
    for p in (front, left):
        open(p, "wb").write(p.encode())
    body = {"model": "v3.1-20260211"}
    assert tripo.run(http, "tank", "generation/multiview-to-model", body, [("front", front), ("left", left)], yes=True, sleep=lambda s: None) == 0
    assert body["inputs"] == [{"front": "tok-front.png"}, {"left": "tok-left.png"}]
    out = os.path.join(tmp, "art", "gen", "tank", "t1")
    assert sorted(os.listdir(out)) == ["model.glb", "rendered_image.webp", "task.json"]
    rec = json.loads(open(tripo.LOG).read().splitlines()[-1])
    assert rec["task_id"] == "t1" and rec["credits"] == 40 and rec["estimate"] == 30 and len(rec["inputs"]) == 2


def test_repaint_sends_the_sheet_views_as_the_texture_prompt():
    http = Fake()
    front = os.path.join(tmp, "front.png"); open(front, "wb").write(b"png")
    body = {"model": "v3.5-20260815", "pbr": False}
    assert tripo.run(http, "tank", "models/texture", body, source="gen1", yes=True, sleep=lambda s: None, tex_views=[("front", front)]) == 0
    assert body["input"] == "gen1" and body["texture_prompt"] == {"images": [{"front": "tok-front.png"}]}


def test_create_never_retries_a_500_but_waits_out_a_429():
    try:
        tripo.create(Fake(create_error=(500, 1000)), "generation/image-to-model", {})
        raise AssertionError("a 500 must not be retried")
    except tripo.ApiError:
        pass
    tripo.time.sleep = lambda s: None
    assert tripo.create(Fake(create_error=(429, 2000)), "generation/image-to-model", {}) == "t1"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
