# Audio sourcing: licences, AI tools and provenance

Read 2026-11-13. Terms change; re-read the page before a ship decision.

## Libraries

| Source | Licence | Attribution | Use for |
|---|---|---|---|
| Kenney | CC0 | none | UI, generic impacts; thin on fantasy combat |
| Sonniss GDC bundles (sonniss.com/gameaudiogdc) | "unlimited number of projects for the entirety of their life time", covers games; you may not "distribute, publish, sub-license or otherwise supply the sound effects as sound effects"; AI training forbidden | none | the best free source for combat, magic and impacts. GDC 2024 is 23.5 GB in 9 parts; GDC 2026 is 7.5 GB |
| Freesound | per sound: CC0, CC BY, CC BY-NC, Sampling+ | CC BY needs author, link and licence | filter `license:"Creative Commons 0"`; never NC for an ad-supported game; full downloads need an account |
| 99Sounds | "any number of personal and commercial projects"; credit "is not obligatory"; no redistribution of the files; names "game development" | none | impacts, foley, whooshes |
| Pixabay | royalty-free, commercial use allowed, no attribution; no standalone resale | none | fine inside a game; check each file's "AI-generated" label |
| Mixkit | commercial use, no attribution; games not named | none | ambiguous for games: ask or skip |
| Zapsplat (free tier) | credit "ZapSplat" wherever reasonably possible | required | low priority |
| incompetech (Kevin MacLeod) | CC BY 4.0, with a required credit line | required | atmospheric filler; no stems |
| Ovani Sound and similar packs | royalty-free; three intensity versions per track (not true stems) | none per the listing | the closest cheap thing to adaptive; check the tempo before crossfading |
| OpenGameArt | mixed, including share-alike and GPL | per file | avoid share-alike and GPL; AI uploads go unlabelled |
| patch.gg | indexes Kenney audio only | n/a | adds nothing for audio |

## AI sound effects

| Tool | Commercial use | Price | Notes |
|---|---|---|---|
| ElevenLabs Sound Effects | paid plans only ("The free plan does not include a commercial license") | Starter $6/mo (first month $1), about 150 sounds | 0.1–30 s; MP3 or WAV 48 kHz; set `model_id` to the v3 model explicitly; strongest for short one-shots; standalone resale of the output is forbidden |
| Stable Audio 3.0 Small SFX | Stability Community License: you own the output; free under $1M annual revenue | free, runs locally | open weights on Hugging Face (gated); quality untested; Gemma use restrictions apply |
| Stable Audio API | same | $0.08 per generation | |
| Meta AudioGen | weights are CC BY-NC | n/a | not for a commercial game |
| Adobe Firefly sound effects | "commercially safe" (claimed) | $9.99 for 2,000 credits | the API is enterprise only |
| OpenRouter | no sound-effects model | n/a | only Lyria music clips and speech |

## AI music

| Tool | Commercial use in a game | Stems |
|---|---|---|
| Eleven Music | paid plans exclude "Studio Games"; an "Indie Game" (under $500k revenue, and a publisher under $1M) appears allowed: confirm in writing | not documented |
| Google Lyria 3.5 / 3 Clip | Google claims no ownership; no explicit commercial grant | none; no tempo control. Lyria RealTime is experimental and only good for ideas at dev time |
| Stable Audio 3 Small/Medium | Community License, as above | none; inpainting extends loops |
| Suno | Pro plan only, "solely to the extent it adheres" to its terms; Universal and Sony are still suing | unclear |
| Udio | downloads removed | n/a |
| AIVA | Pro only (€33/mo), you own the copyright | MIDI export |
| Mubert | Ultra only ($89/mo) for games | 4–6 stem splits |

## Platform rules

- **Steam (Content Survey):** "Pre-Generated" is AI content that ships with the game; Valve
  evaluates it "the same way we evaluate all non-AI content". "Live-Generated" is made while the
  game runs and needs stated guardrails.
- **CrazyGames:** no rule on AI assets found (ask support). "Your game must be PEGI 12
  compliant"; "Audio levels are consistent"; 50 MB initial download, 250 MB total, 1,500
  files.
- **US Copyright Office (Part 2, January 2025):** "prompts alone do not provide sufficient human
  control". Human selection, arrangement and editing remain protectable.

## Provenance record (JSONL, one line per shipped file)

`id`, `file`, `role`, `source`, `source_url`, `author`, `licence` (an SPDX id or a named licence
such as "Sonniss-GDC-v2.0"), `licence_url`, `licence_read_date`, `licence_snapshot` (a saved copy
or hash), `attribution_required`, `credit_line`, `ai` (true or false), `tool`, `model_id`,
`plan_tier`, `invoice_ref`, `prompt`, `seed`, `generated_at`, `output_sha256`, `human_edits`
(layers and the ffmpeg command), `shipped_as`, `steam_disclosure`, `variant` (safe or mature).
Generate `credits.txt` from it.

## Loudness with ffmpeg

Two passes: measure, then apply with the measured values.

```
ffmpeg -i in.wav -af loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json -f null -
ffmpeg -i in.wav -af loudnorm=I=-18:TP=-1.5:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:linear=true -ar 48000 -ac 1 -c:a libopus -b:a 48k out.ogg
```

Integrated loudness is unreliable on hits shorter than 0.4 s. Normalise those by peak instead
(−1 dBTP), then trim each category by ear.
