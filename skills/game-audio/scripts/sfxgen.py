"""Generates sound effects with ElevenLabs from a prompt plan, and logs every take's provenance.

    python -I sfxgen.py <plan.json> <out dir> [--dry-run]

plan.json maps a sound name to its prompt:
    {"bow-release": {"text": "A single dry bow string release...", "duration": 0.5,
                     "influence": 0.6, "takes": 4}, ...}
"duration" (0.1-30 s) and "influence" (0-1: how literally the prompt is followed) are optional.
Takes come back as <out dir>/<name>-<n>.mp3; generation.json records, per file, the prompt, the
model, the settings, the date, the credit cost the API reported and its request id. That record
is the provenance the game's own log takes over, and the evidence of human selection: a
person still picks which takes ship. Cut and normalise the takes with slice.py (they often peak
late and quiet), then measure the mix with mixcheck.py.

The key is read from ELEVENLABS_API_KEY - the process environment, or on Windows the user's
environment in the registry, so a key set after the shell started still works - and is never
printed. A key scoped to sound generation alone is enough. Paid plans only for commercial use.
Never send a Sonniss sound to any AI tool: its licence forbids it.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://api.elevenlabs.io/v1/sound-generation"
MODEL = "eleven_text_to_sound_v3"


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key and sys.platform == "win32":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = winreg.QueryValueEx(k, "ELEVENLABS_API_KEY")[0]
        except OSError:
            key = ""
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set")
    return key.strip()


def generate(key: str, spec: dict) -> tuple[bytes, dict]:
    body = {"text": spec["text"], "model_id": spec.get("model", MODEL)}
    if "duration" in spec:
        body["duration_seconds"] = spec["duration"]
    if "influence" in spec:
        body["prompt_influence"] = spec["influence"]
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310 - a fixed https URL
            return r.read(), {"credits": r.headers.get("character-cost"), "request_id": r.headers.get("request-id")}
    except urllib.error.HTTPError as e:
        # The error body names the problem (a missing permission, no credits); it never holds the key.
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    plan = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    out = Path(args[1])
    takes = sum(s.get("takes", 1) for s in plan.values())
    print(f"{len(plan)} sounds, {takes} takes")
    if "--dry-run" in sys.argv:
        return 0
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "generation.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    key = api_key()
    total = 0
    for name, spec in plan.items():
        for n in range(1, spec.get("takes", 1) + 1):
            fn = f"{name}-{n}.mp3"
            if fn in log:
                continue  # already made: a rerun never pays twice
            audio, meta = generate(key, spec)
            (out / fn).write_bytes(audio)
            log[fn] = {"prompt": spec["text"], "model": spec.get("model", MODEL), "duration": spec.get("duration"),
                       "influence": spec.get("influence"), "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "tool": "ElevenLabs Sound Effects API", "ai": True, **meta}
            log_path.write_text(json.dumps(log, indent=1))
            total += int(meta["credits"] or 0)
            print(f"{fn}: {meta['credits']} credits")
    print(f"done: {total} credits this run; log in {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
