---
name: crazygames-publishing
description: Use when building, preparing, submitting or updating a web game for CrazyGames - SDK integration, ads, progress save, covers and preview videos, the submission form, Basic Launch metrics, or a rejection such as "the overall quality of the game does not yet meet the expectations of our platform".
---

# Publishing on CrazyGames

CrazyGames reviews a game three times, and each review asks something different. Most rejections
come from the subjective quality review, not from technical failures. So build the technical rules
in from the first commit, and spend the time before submission on the game's first five minutes.

- `checklist.md`: every rule, grouped by area, with its page and its Basic or Full Launch tier, plus
  22 places where the docs contradict themselves.
- `docs-digest.md`: all 48 doc pages, one section each with its URL.

Both were read on 2026-10-23. Re-check the live page for any number a build depends on.

Load `games-doctrine` for how the game itself is built. The portal SDK lives behind its `platform/`
adapter.

## The three reviews

| Stage | What it judges | When you fail |
|---|---|---|
| **QA review** | Works, follows the rules, and is "good" and original. The judgement is subjective. | A generic "overall quality" notice, with no feedback by default. |
| **Basic Launch** | Real players with ads off, for 7–21 days and 500+ plays. Judged on average playtime (target 10+ min), share of players who play at least 1 min (80%+), day-1 return (10–15%; platform average 6.7%), load time under 10 s and a build under 20 MB. | Mostly below target: you may only come back as a **new game**. |
| **Full Launch** | A second QA pass with the full SDK: ads, accounts and progress save. | Rejected until fixed. Repeated non-compliant submissions can restrict the account. |

## Hard rules that shape the build

Build these in from the start. Retrofitting them is where the time goes.

- **Size and loading.**
  - Initial download at most 50 MB, measured up to the first `gameplayStart`.
  - Under 20 MB earns a place on the mobile homepage.
  - Total at most 250 MB and 1,500 files, with relative paths only.
- **Devices.**
  - Must run in Chrome and Edge, and smoothly on a 4 GB Chromebook.
  - Mouse and keyboard, plus touch if the game supports mobile.
  - Playable in landscape on desktop.
- **Legibility.** All text must be readable at device pixel ratio 1 at the ten iframe sizes in
  `checklist.md` (smallest 800×450). The docs only say "legible", so use our own floor: 14 CSS px.
- **Physics.** Must behave the same at 144 Hz and 165 Hz: use a fixed step driven by real frame time.
  `games-doctrine` covers how to set it up.
- **Chromebook stand-in.** Without a 4 GB Chromebook, test in Chromium with the CPU throttled 4× to
  6×. Each frame's work should average under 10 ms, with the 90th percentile under 16.7 ms, on the
  busiest level.
- **SDK from day one.** The SDK is optional for Basic Launch, but integrate it anyway.
  `gameplayStart` is how the initial download gets measured. And the ads-off path is reviewed in
  Basic Launch whether you prepared for it or not.
- **Ads.** Only through the SDK. Never during play or on navigation buttons.
  - Pause and mute when `adStarted` fires. Resume when `adFinished` or `adError` fires.
  - A rewarded offer must be optional, carry a video icon, and have a "no thanks" option of the
    same size. Grant the reward only on `adFinished`.
  - Revive offers: at most once per session.
- **Ads switched off.** The game must play fully with Basic Launch's ads off and behind an ad
  blocker. A rewarded button that does nothing is grounds for rejection.
- **Accounts.**
  - No external logins.
  - Guests always play.
  - At Full Launch: the CrazyGames username and avatar, automatic login, users identified by the
    server-verified `userId`, and progress in the Data module.
- **Keys.**
  - Never bind Esc, which exits fullscreen. Never bind Ctrl or Cmd+W.
  - Read keys by physical position (`event.code`), so AZERTY players get ZQSD.
  - Block page scrolling and the context menu.
- **Page.**
  - No custom fullscreen button.
  - No cross-promotion and no App Store links.
  - No other portal's name anywhere in the build.
- **Audience.** PEGI 12, ages 13+, English required, original name and assets.
- **Covers.**
  - 1920×1080, 800×1200 and 800×800, with no text except the title, no borders and no logos.
  - Keep the title out of the top-left corner, where the portal overlays its labels.
- **Preview videos.**
  - Two videos: 1080p 16:9 and 1080p 2:3.
  - 15–20 s each, at most 50 MB, silent, no fast-forward.
  - Each opens on its static cover.

## Prove each rule with a test

A rule that is only stated drifts. Each one below is a test that runs on every build:

| Rule | Test |
|---|---|
| `gameplayStart`/`gameplayStop` pairing | Wrap the SDK in a spy. Script a run through start, pause, wreck, finish and menus, then assert the call sequence. |
| Ads off, ad blocker, unfilled ads | Run three fake ad modes, `pay`, `fail` and `adblock`, against every rewarded button. Assert that no button ever does nothing. |
| Legibility | Read every text object's on-screen font size and box at the ten sizes at DPR 1. Assert at least 14 CSS px and on screen, on every scene and every state, including the busiest results card. |
| Keys and page | No scroll on the game's keys, no context menu, and no Esc binding while in fullscreen. |
| Refresh rate | Replay recorded inputs headless at 60, 144 and 165 Hz and compare the final state hash. |
| Build hygiene | Scan the portal build for other portals' names, test hooks and outgoing URLs. Count bytes downloaded before `gameplayStart`. |
| Covers | Render each cover and assert that no title colour falls in the top-left label corner (about 40% × 22%). |

## Before submitting: the first five minutes

The quality review plays briefly and judges four things:
- **First impression:** cover, first frame, time to first input.
- **Polish:** consistent art, responsive feel, sound.
- **Depth:** whether there is clearly more than ten minutes.
- **Uniqueness:** "Is your game unique?"

So before submitting:

1. **Watch three to five top games in the same genre** on the site, as a visitor only. Recording or
   scraping hosted games is against the terms. Note how many seconds each takes to reach its first
   "wow".
2. **Play your own first five minutes against them**, and write down every place where yours is
   slower, flatter or plainer.
3. **Put the best thing in the game into the first minute.** Showpiece hazards and destruction
   placed only in later levels never reach the reviewer.
4. **If the genre is crowded** (driving, idle, hill-climb), state in one sentence what no other game
   in it does. If you can't, expect "overall quality".
5. **Test in the Developer Portal's Preview tool, and on a real phone in both orientations.**

## After a rejection

- **"Overall quality" is the generic template.**
  1. Email developer-relations@crazygames.com. Ask what fell short and whether a substantially
     improved build may be resubmitted.
  2. Fix any hard-rule gaps you find anyway.
  3. Resubmit only after visible, significant change, with a short changelog. An unchanged build
     risks restriction.
- **A failed Basic Launch is different.** The game can return only as a new game with significant
  improvements.
- **Meanwhile, publish elsewhere.** A game that is otherwise finished can earn on another portal.
  Check that portal's exclusivity terms first.

## Gotchas found in practice

- **Basic Launch with ads off.** The first ad request answers `adsDisabledBasicLaunch`. Grant that
  first reward free, then hide or relabel rewarded offers.
- **Progress save.**
  - Adopt the Data module only when it reads successfully.
  - Move local progress into it once.
  - An existing cloud save wins.
  - In the submission form, pick "Yes, using the Data Module". Otherwise the SDK switches the module
    off.
- **iPhone sound.** Silent mode mutes all web audio. That is the player's setting, not a bug.
- **The finish-screen photo.** Copy it on the GPU (`copyTexImage2D` into a texture). A
  `readPixels` call plus PNG encoding froze phones for most of a second.
- **Redrawing a scene after a resize.** In Phaser 4, `children.removeAll(true)` does not destroy
  anything. Destroy a copy of the scene's children instead, or invisible buttons keep taking taps,
  including rewarded ones.
- **The upload form refuses archives.** Drag in the build folder's contents, so `index.html` sits at
  the top level.
