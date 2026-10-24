"""Self-check for concept.py; no network. Run: python -I test_concept.py"""
import base64, json, os, sys, tempfile, urllib.error

TMP = tempfile.mkdtemp()
os.environ["CONCEPT_ROOT"] = TMP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept  # noqa: E402

# the project's house style is required, and travels after the prompt
try:
    concept.house_style()
    raise AssertionError("a missing art/house-style.md must stop the run")
except SystemExit as e:
    assert "house-style.md" in str(e), e
os.makedirs(os.path.join(TMP, "art"))
open(os.path.join(TMP, "art", "house-style.md"), "w", encoding="utf8").write("Flat low-poly.\n")

ref = os.path.join(TMP, "ref.png")
open(ref, "wb").write(b"\x89PNG fake")

# refs travel as image_url parts after the text part
content = concept.build_body("p", "m", "16:9", [ref])["messages"][0]["content"]
assert content[0]["type"] == "text" and content[0]["text"] == "p\n\nSTYLE: Flat low-poly.", content[0]
assert content[1]["type"] == "image_url", content[1]
assert content[1]["image_url"]["url"].startswith("data:image/png;base64,"), content[1]
assert [p["type"] for p in concept.build_body("p", "m", "16:9", [])["messages"][0]["content"]] == ["text"]

# 429 on the first model falls through to the second, and provenance names the model that answered
png = base64.b64encode(b"\x89PNG one").decode()


def fake(body):
    if body["model"] == concept.MODELS[0]:
        raise urllib.error.HTTPError("u", 429, "rate limited", {}, None)
    return {"choices": [{"message": {"images": [{"image_url": {"url": "data:image/png;base64," + png}}]}}],
            "usage": {"cost": 0.1}}


files = concept.generate("t", "p", post=fake)
assert files == ["art/concept/t-1.png"] and os.path.exists(os.path.join(TMP, files[0])), files
log = [json.loads(l) for l in open(os.path.join(TMP, "art", "provenance.jsonl"), encoding="utf8")]
assert log[-1]["model"] == concept.MODELS[1] and log[-1]["usage"]["cost"] == 0.1, log[-1]

# a second run never overwrites the first
assert concept.generate("t", "p", post=fake) == ["art/concept/t-2.png"]

# picks are logged with their reason
concept.pick("art/concept/t-1.png", "why")
last = json.loads(open(os.path.join(TMP, "art", "provenance.jsonl"), encoding="utf8").readlines()[-1])
assert last["pick"] == "art/concept/t-1.png" and last["reason"] == "why", last

print("ok")
