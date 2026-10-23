<!-- Digest of docs.crazygames.com, read 2026-10-23, one section per page with its URL. Near-verbatim; the live page wins if they differ. -->
# CrazyGames developer documentation: complete digest (2026)

- Fetched: 2026-10-23 from https://docs.crazygames.com/ (48 pages), one page at a time with WebFetch. No hosted games were fetched or inspected.
- Fidelity: the fetch tool returns structured extractions, so prose is **near-verbatim**, not exact. Numbers, API names, signatures, events, error codes, domains and code were requested exactly.
- Labels: the docs rarely use literal MUST/SHOULD/INFO badges. They tag items **[Basic Implementation]** / **[Full Implementation]** / **Guideline** and use Info/Warning/Tip callouts plus "must"/"should"/"not allowed" wording. Each page section below records the page's own wording.
- Per-page files and the list of failed or skipped pages: see `index.md` in this folder.
- **The last section is the deduplicated pre-submission checklist and the contradictions between pages.**

## Contents
1. Introduction
2. Requirements: Introduction
3. Requirements: Technical
4. Requirements: Gameplay
5. Requirements: Advertisement
6. Requirements: Account integration
7. Requirements: Multiplayer
8. Requirements: Game covers
9. Requirements: Quality guidelines
10. SDK: Introduction
11. SDK: Video ads
12. SDK: Banners
13. SDK: Game module
14. SDK: User module
15. SDK: Data module (progress save)
16. SDK: In-game purchases
17. SDK: User account linking (HTML5 v3)
18. SDK: Leaderboards introduction
19. SDK: Leaderboards SDK (client-side)
20. SDK: Leaderboards API (server-side)
21. Automatic Progress Save (APS)
22. Resources: index
23. Resources: Mouse control
24. Resources: CrazyGames App
25. Resources: Basic Launch Guide (metrics)
26. Resources: Game Loading Tips (Getting to the first frame)
27. Resources: Ad Monetization Guide
28. Resources: Mastering Rewarded Ads
29. Resources: Optimizing Midgame Ads (pacing and placement)
30. Resources: Banner Ad Best Practices
31. Resources: Ad tips for Hypercasual & IO
32. Resources: Ad tips for Midcore, RPG & Idle
33. Resources: Ad tips for Puzzle
34. Resources: Ad tips for Action
35. Resources: Ad tips for Clicker & Incremental
36. Resources: Ad tips for Word
37. Resources: Ad tips for Driving
38. Resources: HTML5 Sitelock
39. Resources: HTML5 Common fixes
40. Resources: Unity custom build (brief)
41. Resources: Unity optimization tips (brief)
42. Resources: Unity Optimizer package (brief)
43. Resources: Unity common issues (brief)
44. Resources: Unity Addressables guide (brief)
45. Resources: External resources
46. Partners
47. FAQ & Contact
48. Payouts
49. Pre-submission checklist and contradictions

---

## Introduction

- URL: https://docs.crazygames.com/
- Title: Introduction - CrazyGames Documentation
- Fetched: 2026-10-23 (WebFetch, summarised extraction; the fetch tool paraphrases, so wording is near-verbatim, not exact)

### Labels
No MUST/SHOULD/INFO labels on this page. It points to the Requirements section for rules.

### Benefits listed
- Games reach desktop and mobile
- Millions of gamers, many of them registered
- Revenue from ads, plus in-game purchases (selected games only)
- Easy cloud save of progress
- In-game friend invites
- Statistics and feedback on games
- Developer community

### Launch process (two stages)
Stated goal: shorten the initial launch timeline and test real-world performance before a global release.

#### Basic Launch
- Limited audience, **7 to 21 days**
- Basic Implementation only; no CrazyGames-specific integration needed
- Basic QA review only
- Monetization **disabled** (video ads, banners, in-game purchases)
- Moves to Full Launch if the metrics are good

#### Full Launch
- Triggered when the game is selected for a global release
- Full Implementation plus a Full QA review
- Monetization enabled and revenue share begins
- While you integrate, the Basic version stays live for its original limited audience

#### When the Basic Launch period ends
- It ends only when **both** are true: live at least **7 days** AND at least **500 plays**.
- If 500 plays are not reached, it ends automatically after **21 days**.
- Near-quote: "Both thresholds must be met, so a game that reaches 500 plays sooner still runs for the full 7 days."

#### Outcomes at the end of the period
1. **All metrics meet or beat the benchmarks:** you are invited to update the game, implement the Full Implementation requirements, and submit the new version for Full Launch.
2. **Some metrics meet the benchmarks:** you may be invited to improve the game and ask for another Basic Launch period.
3. **Most metrics fall below the benchmarks:** the game cannot go to Full Launch. To resubmit, you must submit it **as a new game with significant improvements**.

#### Exceptions: these may skip Basic Launch and go straight to Full Launch
- Multiplayer titles that need a larger audience
- Games already published elsewhere that the CrazyGames team has specifically invited

#### Evaluation metrics
Average playtime, conversion to gameplay, and retention, each benchmarked against other games on the platform. This page does not publish benchmark values; see resources/basic-launch-metrics.

#### Review
The QA team reviews every submission against the technical and quality requirements.

### SDK
- Easy one-time integration, user-friendly ads, simple docs.
- If your engine is not listed, basic integration usually works through the HTML5 SDK, because most WebGL-capable engines can call JavaScript.
- Read the requirements before integrating.
- Engines listed: HTML5, Unity, GameMaker, Construct 3, Godot, Cocos, GDevelop (external wiki), Defold (external), Wonderland (external tutorial).
- Frameworks used by live games: Unity, Defold, Godot, Phaser, PlayCanvas, Construct, Pixi.js, BabylonJS and others.

### Testing
- Use the **Preview tool** (under "Submit a game" on developer.crazygames.com) to see how the game will look on CrazyGames and to test versions before submitting.

### Partners
Photon (backend), Xsolla (payments), ByteBrew (analytics), Lasso (moderation).

### Numbers
| Item | Value |
|---|---|
| Basic Launch duration | 7 to 21 days |
| Minimum time live | 7 days |
| Minimum plays | 500 |
| Automatic end | 21 days |
| Revenue share % | not stated here |
| Benchmark values | not stated here |

---

## Requirements: Introduction

- URL: https://docs.crazygames.com/requirements/intro/
- Title: Introduction - CrazyGames Documentation (Requirements)
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
Rows are not individually labelled MUST/SHOULD; each row is a requirement for its launch tier. Optional items elsewhere in the docs are marked **"Guideline"** (the Quality Guidelines).

### Launch process
- Two steps: Basic Launch, then Full Launch.
- **Basic Launch:** the game can go live without CrazyGames-specific customization. The SDK is optional and monetization is not available. Progression is judged by the Basic Launch Guide (resources/basic-launch-metrics).
- **Full Launch:** once selected, near-quote: "you are required to comply to all integration requirements listed below".
- Full Implementation must also meet every Basic Implementation requirement.

### Requirement matrix
| Area | Basic Implementation | Full Implementation |
|---|---|---|
| Technical | Initial download **<= 50 MB**; total file size **<= 250 MB** (**50 MB without the SDK**); file count **<= 1500** | SDK & `gameplayStart` event |
| Gameplay | Basic visual QA checks; adhere to **PEGI 12** | Full visual QA check; land directly in gameplay |
| Advertisement | CrazyGames monetization disabled; **no external ads** | Ads through the SDK, following the guidelines; works with AdBlock |
| Account integration (only when applicable) | **No external login options** | Progress linked to the CrazyGames account; use the CrazyGames username & avatar; automatic login for CrazyGames users |
| Multiplayer (only when applicable) | Full-implementation features optional in Basic Launch | User room info; invite link (if applicable); instant multiplayer flow; keep rooms across rounds; `disableChat` preference |
| In-game purchases (invite only) | Not available | Use the CrazyGames Xsolla account and `userId` |

- The HTML5 and Unity SDKs support every scenario; other SDKs may lack some functions.
- Submission also needs qualitative metadata (game description and controls) and game covers (images and videos).

### Monetization
- Main mechanism: advertisement revenue share.
- **Only ads served through the CrazyGames SDK are allowed.**
- Selected games can get in-game purchases. This needs a Full Implementation and Xsolla as the payment provider; contact the team to apply.

### Insights & analytics
- The Developer Dashboard shows players, average playtime, gameplay conversion, retention and revenue.
- ByteBrew (free) is recommended for advanced analytics: level progression, drop-off points and user journeys.
- **Warning:** if the game collects personal data beyond SDK events, it should show new players a Terms & Conditions and/or Privacy Policy notice. See User Consent (requirements/technical/#user-consent).

### Support threshold
- Technical support for SDK integration is offered once games reach **50k plays combined**.

### QA tool
- The Developer Portal preview runs the game as it would run on CrazyGames, checks it against the requirements, and tests the SDK features you implemented, with feedback.

### Not on this page
Review timings, resubmission rules and examples of accepted or rejected games.

---

## Requirements: Technical

- URL: https://docs.crazygames.com/requirements/technical/
- Title: Technical requirements - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
This page does not use MUST/SHOULD/INFO. It tags sections **[Basic Implementation]** or **[Full Implementation]** and uses the words "must", "should", "Never", "We require" and "strongly recommend", recorded below.

- Near-quote (MUST): "You must follow these technical requirements to get your game published on CrazyGames."

### File size & count [Basic Implementation]
| Rule | Limit | Wording |
|---|---|---|
| Total file size | **<= 250 MB** | must |
| File count | **<= 1,500 files** (a high file count slows loading) | must |
| Initial download size | **<= 50 MB** | must |
| Initial download for **mobile homepage** eligibility | **<= 20 MB** | must, for the homepage |
| Without the SDK | the total file size counts as the initial download, so **<= 50 MB** (**<= 20 MB** for the mobile homepage) | must |
| Files hosted or loaded externally | QA times the wait to reach gameplay, which must be **<= 20 seconds** | must |

- With the SDK (optional for Basic, mandatory for Full), the initial download is measured **from the start of loading to the first `gameplayStart` event** of the Game module. That event should fire when the user reaches a playable state: not menus, not extra loading steps.
- **Paths:** use only relative paths. Near-quote: "Never use absolute paths, as they will fail to load." (MUST NOT)
- For optimization, see the Resources pages and the Unity custom build.

### Device & browser compatibility [Basic Implementation]
- Games are expected to work on **Chrome and Edge**.
- Games that don't work well on **Safari** will be **disabled on Safari**.
- **Chromebook / ChromeOS:** a game is disabled there if it doesn't run smoothly on a **4 GB RAM** device.
- **Input:** support mouse and keyboard; if the game supports mobile, support touch too.
- **Orientation:** must be playable in **landscape on desktop**. Portrait games are allowed (especially mobile-friendly ones) with black bars or background images on the sides.
- **Device detection:** CrazyGames "strongly recommend[s]" the SDK's system info (`sdk/user/#system-info`) for device-specific behaviour. The SDK can tell desktop, mobile, tablet, OS, browser and application type apart.

#### Mobile
- Mobile homepage: initial download **<= 20 MB**.
- Supported orientations are set in the submission form. The site asks the user to rotate the device, so the game needs no orientation lock of its own.
- To stop the magnifier and selection menus on tablets, add to `body`:
  ```css
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  ```
- **Unity on iOS is disabled by default** (memory crashes). The team may test it and turn it on once the game has enough plays.
- **CrazyGames App:** games open fullscreen and can be affected by device safe areas; see the Safe area page (resources/crazygames-app).
- **Unity DPR:** iOS and low-memory Android devices use **DPR 1** (higher DPR crashes them). Other devices use `window.devicePixelRatio`. CrazyGames can override this by hand when needed.

#### Resuming audio after iOS interrupts it
- Android keeps the `AudioContext` `running` when the user switches apps. iOS puts it in an `interrupted` state when the app is backgrounded or a call comes in, and it often comes back `suspended`.
- Unity handles this automatically. Problems were seen with **Howler** and **PlayCanvas**.
- Fix: call `resume()` inside a user gesture (`touchend` or `click`). A visibility-change listener alone is not enough, because WebKit blocks audio until the user interacts directly.
  ```js
  document.addEventListener("touchend", () => {
    if (audioContext.state === "suspended") audioContext.resume();
  });
  ```
- Where the context lives: Howler `Howler.ctx`; PlayCanvas `pc.app.soundManager.context`.

### SDK integration
The page calls the SDK "important" for the best experience and for access to the platform's value.

#### Basic SDK integration [Basic Implementation]
- If you integrate the SDK, you must fire a `gameplayStart` event from the Game module when the player reaches game state; it is used to measure the initial download size.
- **Ads are not allowed in Basic Launch**; they are disabled even if integrated.

#### Full SDK integration [Full Implementation]
Everything in Basic, plus:
- `gameplayStart` / `gameplayStop` events, used to measure and report the gameplay experience
- the Data module for progress save, if applicable (see Account integration, Progress save)
- the User module for account integration and username/avatar, if applicable
- `loadingStart` / `loadingStop` are **optional**; they measure in-game loading times and failure rates

### Sitelock & whitelisting [Basic Implementation]
- A sitelock is optional, to help prevent theft of game files.
- CrazyGames runs on **several `crazygames.com` origins**. If you sitelock, whitelist each domain that applies.
- The iOS and Android apps have their own origins, which must also be whitelisted (see resources/html5/sitelock and resources/crazygames-app).

### User consent
- If the game collects personal data beyond SDK events, add a **Terms & Conditions** and/or **Privacy Policy** notice for new players.
- A simple notice is recommended over a pop-up that blocks the user.
- Examples cited: Bloxd.io (in-game privacy policy); Racing Limits (opens the privacy policy in a new tab).

### Not on this page
Iframe rules, a fullscreen section, and performance benchmarks beyond the above.

---

## Requirements: Gameplay

- URL: https://docs.crazygames.com/requirements/gameplay/
- Title: Gameplay requirements - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
Uses **[Basic Implementation]**, **[Full Implementation]** and **Guideline**, plus "must"/"should" wording. No MUST/SHOULD/INFO badges.

### Intro
- The aim is well-crafted games, not "perfect" ones; only games that put quality and gameplay first are allowed.
- **Developers who repeatedly submit non-compliant games may be restricted from future submissions.**
- The quality guidelines draw on Facebook Instant Games best practices.

### Basic gameplay requirements [Basic Implementation]
"Ensure your game meets the following criteria." QA runs visual and functional checks on every submission.

#### Readable content (must)
Text and images must be legible at **`devicePixelRatio: 1`**, at responsive **16:9** iframe sizes, and on mobile screens where applicable. "The most important iframe sizes for our audience":

| Size | Context |
|---|---|
| 907 x 510 | desktop, not fullscreen |
| 1216 x 684 | desktop, not fullscreen |
| 1077 x 606 | desktop, not fullscreen |
| 821 x 462 | desktop, not fullscreen |
| 1366 x 768 | desktop fullscreen |
| 1920 x 1080 | desktop fullscreen |
| 1536 x 864 | desktop fullscreen |
| 1280 x 720 | desktop fullscreen |
| 800 x 450 | mobile |
| 1080 x 607 | tablet |

#### Consistent physics (must)
Physics must behave the same at any monitor refresh rate; the page names **144 Hz and 165 Hz** as examples.

#### Language support
- **English localization is required.**
- Translations must be accurate and of high quality.
- The game should use the user's language from the SDK system-info `locale` value, falling back to English when it is missing or unset.

#### Intuitive controls (must)
Controls must be intuitive on every device type. See "restricted keys" in the Quality Guidelines.

#### Smooth performance (must)
Loads quickly; no errors or crashes.

#### Originality (must)
Game names, assets and overall content must be original.

#### Fullscreen
- CrazyGames provides fullscreen automatically.
- **Custom in-game fullscreen buttons are prohibited** because they can interfere with features such as monetization.

#### No cross-promotion (must)
- Games must not cross-promote external or internal games or platforms.
- Exception: a Privacy Policy and Terms & Conditions, where applicable.
- Links allowed, as long as none is a main call to action on the menu:
  - community links (Discord, developer website), **on the game menu only** and never straight to a playable web version
  - desktop store links (Epic, Steam), **only on the main menu or at the end of a demo**
  - backlinks to the CrazyGames home or category page (accepted, but not promoted)
  - links to other games in the same series
- **App Store links are never allowed in-game.** Put them in the configurable metadata fields in the Developer Portal instead.

#### Suited for minors (must)
- The site targets players **13 and over**; games must be **PEGI 12** compliant.
- A separate kids site exists (kids.crazygames.com) where monetization is disabled.

### Full gameplay requirements [Full Implementation] ("mandatory for full implementations")
- Games should drop new users **straight into gameplay**.
- If that isn't feasible for the game, **at most 1 click** is allowed before gameplay.

### Additional quality guidelines [Guideline]
Not mandatory but strongly recommended; see the Quality Guidelines page.

### Not on this page
No list of prohibited content beyond PEGI 12, no rules on splash screens, credits or pausing, and no example games.

---

## Requirements: Advertisement

- URL: https://docs.crazygames.com/requirements/ads/
- Title: Advertisement requirements - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
No MUST/SHOULD/INFO badges. The page carries a **Warning** callout at the top and links to [Full Implementation]. The "must", "should", "not allowed" and "do NOT" wording is recorded below.

### Warning: Basic Launch
- In Basic Launch, ads are **disabled** and **no revenue is shared**.
- If the ads SDK is integrated, QA checks that the game runs smoothly **with ads disabled**. **Games that fail are rejected.**
- Examples of what QA checks: "Game doesn't freeze between levels"; "There should not be rewarded ad buttons without effect."

### Ad source
- Near-quote (MUST): "Only Ads requested through the CrazyGames SDK are allowed." No external ad networks.

### Ad types available through the SDK
- Video ads: **midgame** (between levels or stages) and **rewarded**. CrazyGames provides fallback banners.
- In-game **banners**.

### General principles
- In-game ads and purchases should be meaningful and should not appear before a reasonable amount of gameplay.
- Ads must not interrupt gameplay, trigger deceptively, or be chained.

### Video ads
- Near-quote: "Video ads can not interrupt gameplay and shouldn't come as a surprise."
- Show them at logical breaks: level transitions, or a map change after death.
- **No midgame ad on navigation buttons** (main menu, settings, shop).
- Near-quote: "Your game should be paused during a video ad."
- Disable buttons or show a blocking spinner while an ad is being requested or shown. Block the UI until `adFinished` or `adError` fires, because the auction takes time.
- **Unfilled calls:** a midgame request can go unfilled (timing limits, adblock, low demand) and then fires `adError`. The game must handle it and carry on.
- Near-quote: "Your game should be muted during a video ad." Mute only when the ad actually **starts** (`adStarted`) and unmute when it ends. Do not mute on request, since there may be no ad.

#### Midgame frequency (the SDK handles it)
- You don't need to manage frequency or minimum intervals yourself.
- The SDK allows at most **1 midgame ad every 3 minutes**, accounts for the start of the game, and allows for rewarded ads shown nearby.
- Requests that come too early are ignored with no effect on the user, so you can request at any good moment.

### Rewarded ads
- Rewarded ads should be a special opportunity, not an expectation. **Levels that can only be completed by watching a rewarded ad are not acceptable.**
- Don't offer them too often; tell users with a timer, or hide the button.
- **No chaining** (more than one ad for a single reward).
- Don't promote them too aggressively.
- **The request button must not appear on an active gameplay screen** (for example, during a race).
- The button should be easy to find and always in the same place.
- **Not misleading:** the "continue without ad" option must match the request button's size, font and colour.
- It must be clear at once that the reward is optional. **Hiding or delaying the skip/close button is not allowed.**
- Show that an ad must be watched (for example, a video icon).
- Offer an alternative, such as buying the reward with in-game coins.
- `adFinished`: make the reward clear (an animation or notification).
- Near-quote (MUST NOT): "When our rewarded ad returns with an adError callback, do NOT reward the player."
- CrazyGames aims for a high fill rate and recommends other incentives when no ad is available.

#### Example placements
- **In-game store:** works for players already in a buying mindset; give the currency or items they would otherwise buy.
- **End-of-game multiplier:** double the level reward with a video.
- **Out-of-lives:** tempting, but restricted:
  - Near-quote: "It is not allowed to offer an Out-of-lives rewarded video each time the users lose a life." Don't offer it after every death.
  - If it is offered often, put a timer on the button.
  - If no ad is available, encourage the player to try again later.
  - Offer an alternative (coins); never hide or delay skip/close.

#### Level transitions
- Near-quote: "It's not allowed to combine a midgame ad between levels with a rewarded to keep playing the current level." Between two levels, use **either** a midgame ad with a restart **or** a "watch a rewarded ad to keep playing" offer, not both.

### In-game banners
- Only on useful screens whose content stays open **at least 5 seconds on average**.
- Must not cover any game UI at any size, mobile included.
- **Not allowed during gameplay.**
- Must be clearly distinct from game content.
- **At most 2 banners on the same screen**, provided the experience stays clear, unobtrusive and user-friendly.
- Banners can hurt performance and reduce quality and usability.

### Adblockers [Full Implementation: "Works with AdBlock"]
- CrazyGames discourages adblock by turning off some features and blocking rewarded ads when it detects one. Detection is not 100% accurate.
- **Players with adblockers must still be able to play normally. Blocking them or giving them a disadvantage is never allowed.**
- Some features may be blocked if a notice explains they are unavailable because of the adblocker.
- **Don't use popups** for that notice, because they interfere with fullscreen and with CrazyGames' own adblock notices.
- **Don't leave rewarded ad buttons clickable with no effect.**

### Not on this page
No rewarded cooldown number, banner pixel sizes or percentages; see sdk/banners and the monetization resources.

---

## Requirements: Account integration

- URL: https://docs.crazygames.com/requirements/account-integration/
- Title: Account integration requirements - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
Only **[Basic Implementation]** and **[Full Implementation]** tags, plus "we require" and "not allowed" wording.

### Overview
- The CrazyGames account lets users save progress, play across devices, set a username and avatar, and play with friends.
- "Over **35 million** players have a CrazyGames account."
- The intended experience: no separate in-game username or avatar, no extra in-game login flow, and guests can play too.

### Integration scenarios
| Scenario | Tier | Rules |
|---|---|---|
| Game has no accounts | Basic | No need to use the User module. Progress can use the Data module or APS. |
| Uses the CrazyGames profile | Full | Show the username and avatar from the User module. If the result is `null`, the user is not logged in: **continue as guest**. |
| In-game account (basic) | Basic | Let guests and registered users play as guests by default. **Turn off every external login option (Facebook, Google, email).** Full integration will be required once the game proves successful. |
| In-game account (full) | Full | 1) New logged-in CrazyGames users are registered and logged in automatically. 2) Returning logged-in users are logged in automatically. 3) CrazyGames guests can play as guests. 4) **Logging out in-game and external login options are not allowed.** If you offer account import or export, "you are responsible for transferring progress correctly." |

### Progress save [Full Implementation]
- Near-quote (MUST): "Unless progress is not applicable for your game, we require you to implement one of these methods." Players expect progress to sync across devices.
1. **Data module (preferred):** saves to the user's CrazyGames account. Guest progress is saved locally automatically, and on login it syncs to the cloud "as long as no cloud progress was present."
2. **Your own back end plus the User module:** link your data to the CrazyGames account and follow the in-game account flows for guests. Remember that one user may log in on several devices, and several accounts may share one device.
3. **Automatic Progress Save (APS):** syncs local progress to the cloud. Near-quote: "This is not allowed for games with in-game purchases as it relies on local data."

### In-game account integration [Full Implementation]
#### Preparation
- The CrazyGames `userId` (a unique string tied to the account, from the User module) must work as your in-game identifier.

#### At game launch
- Call `getUserToken()` to get a JWT, then verify it **on your server** to get the `userId`.
- **Request the current user account every time the game starts**, because users share devices and change their avatar or username.
- **Not logged in (`userNotAuthenticated` error):**
  - Let them play as a guest by default.
  - Creating in-game accounts for guests is discouraged. If you do, you "should be able to link it" to a CrazyGames account when the guest logs in.
  - "Avoid relying solely on local data to identify Guests across sessions", because several users may share a device.
  - A "Login with CrazyGames" button is allowed, but not as the main call to action.
  - "Don't trigger the Auth prompt automatically as this might confuse the user."
- **Logged in (`userId` returned):** check whether the `userId` already exists in your back end.
  - Known: update the stored username and avatar (they can change), fetch the data and start playing.
  - Unknown: create a game account automatically. "Make sure to make the link based on the `userId` unique field, as other fields like `username` might change." You may move the guest's local progress into the new account.

#### During gameplay
- Detect a guest logging in mid-game with the **auth listener**, follow the logged-in flow, and refresh the game if necessary. This applies to guests only.
- "When a user logs out during gameplay, the entire web page is refreshed", so the game restarts from the beginning.
- **Login button:** not the main call to action and never blocking; top-right corner suggested; it must trigger the SDK's **auth prompt**. "Don't allow Guests to use different login methods than 'Login with CrazyGames'."
- **Logout and account linking:** no in-game logout and no external login. The optional **account link prompt** handles importing and exporting accounts, and you are responsible for migrating progress. "Strongly recommended if you create in-game accounts for CrazyGames guests", and also recommended for games with in-game purchases that create accounts for guests.

### SDK names on this page
`getUserToken()` (JWT), `userId`, the `userNotAuthenticated` error, a `null` user result, the auth listener, the auth prompt, the account link prompt, the User module, the Data module, and APS (`/other/aps`).

### Not on this page
Storage quotas, token lifetime, username or avatar formats.

---

## Requirements: Multiplayer

- URL: https://docs.crazygames.com/requirements/multiplayer/
- Title: Multiplayer requirements - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### How it works
- Claim: games with online multiplayer have **"2x higher long term retention"** than single-player games.
- The **Friends** feature needs a CrazyGames account and a logged-in user. Users send and receive friend requests.
- When a user is somewhere joinable, friends can join them and they can invite friends (who get a notification if online). The Game module of the SDK provides this.
- Games that support Friends are featured on the **Multiplayer landing page**.

### Requirements for "Online with Friends" [Full Implementation] ("requirements must be met")
These are the conditions for appearing on the Multiplayer landing page.

#### Multiplayer flows
- **Share room and status:** pass room info through the SDK so Join/Invite works. Near-quote: "Avoid onboarding scenes for players joining like this, or make them skippable."
  - (New) Use **Update Room** to set the `room` (unique within the game at any moment) and whether it is open (`isJoinable`). Use `inviteParams` to pass information from the inviter to friends. The old **Invite Button** still works for existing games.
- **Invite link:** optional; integrate it so players can copy direct invite links inside the game.
- **Instant multiplayer:** the first player in a party goes straight into a new private room with default settings.
  - When `isInstantMultiplayer` is `true` (the game was launched from CrazyGames UI such as the Multiplayer landing page), launch straight into multiplayer.
  - An intermediate configuration screen (game mode, player count) is acceptable.
  - Games with **20+ players** may put the player straight into public gameplay instead.
  - In every case the user should be joinable **right after launch** so friends can join.
- **Round-based games:** at the end of a match, players carry on with the same group without going through CrazyGames UI, either by starting the next match in the same room or by sending everyone to the same new room.

#### Additional requirements
- **Lobby size:** give the lobby sizes when you upload the build. For changes to an existing game, contact the team.
- **CrazyGames usernames must be shown in-game** so players recognise friends (User module).
- **Chat:** if you have it, see below.

### Guidelines [Guideline, "strongly recommended"]
- Players should be able to join an existing room at any time, entering **spectator mode** during a round in progress; otherwise, show a popup saying the room is unavailable.
- Implement the **room join listener** so joining works without a page reload, since users often load the game before joining or inviting.
- Use the User module's **Get friends** for joining, notification and matchmaking UX.

### Multiplayer in Basic Launch [Basic Implementation]
- Multiplayer games that need a large audience may **skip Basic Launch** and go straight to Full Launch, which then needs the full integration.
- Multiplayer games with a single-player part that don't need a big test audience **require** a Basic Launch.
- QA decides which flow applies and may give feedback.

### Chat and user-generated content (UGC) [Basic and Full Implementation]
- Chat is optional and carries risk.
- **Turn chat off according to the game settings** (sdk/game/#game-settings; the setting is `disableChat`, see the SDK Game page). If complaints arise, chat must be removed entirely.
- **Chat moderation is required.** The simplest form is a **profanity filter** (a non-exhaustive word list is linked as a spreadsheet).
- The advanced option is AI moderation through the partner **Lasso Moderation** (referral bonus available); not recommended for Basic Launch games.
- **UGC (custom images, drawings) also requires moderation**; Lasso covers it.

### Numbers
2x retention claim; 20+ players may go straight into public play; lobby sizes declared at upload. No timings or room-size limits are given.

### Not on this page
Bots, servers and matchmaking details.

---

## Requirements: Game covers

- URL: https://docs.crazygames.com/requirements/game-covers/
- Title: Game covers - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
No MUST/SHOULD/INFO badges. The page uses "must", "mandatory", "advise", "recommend", and headed lists called "Restrictions", "Video Requirements" and "Avoid these elements".

### The requirement
- Near-quote (MUST): "You must add 3 cover images (landscape, portrait and square) and upload preview videos."
- Covers display the game on the site and must catch users quickly.

### General guidelines
- "Don't reinvent the wheel": study games in the same genre and stores such as Steam and Epic for inspiration.
- Update the covers now and then, ideally with new content or for seasonal events, but **not too often**, because users lose familiarity.
- Without the skills or tools, hire a designer (Fiverr, UpWork).

### Cover images: 3 mandatory sizes
| Type | Ratio | Pixels |
|---|---|---|
| Landscape | 16:9 | **1920 x 1080** |
| Portrait | 2:3 | **800 x 1200** |
| Square | 1:1 | **800 x 800** |

- The three covers should share consistent visuals and aesthetics.
- No file format, file size or DPI is given on this page.

#### Restrictions (MUST NOT)
- "Don't put borders around your game covers"
- "Don't write anything else other than your game's title" (for example, no "New", "Updated", "Play" or "Play now")
- "Don't put icons or store logos in the visuals"
- "Don't use copyrighted visuals that you don't have the right to use"
- "Don't use blurry or pixelated visuals"

#### Guidelines (SHOULD)
1. **Don't just take a screenshot.** Use the main character, a big stylised title, or a graphic tied to the game. A cover need not show gameplay accurately, because hovering previews the gameplay. Examples: Build Now, Shell Shockers.
2. **Keep it simple.** Cluttered covers are hard to scan, especially on small screens; keep them clean, balanced and readable. Examples: Tiny Fishing, Capybara Clicker.
3. **Put the game's name on the cover**, for memorability and to stand apart from similar titles. Examples: Helix Jump, Stick War.
4. **Use a nice, stylised font** that fits the game; avoid default-looking fonts (Times New Roman is named as a bad first choice). Examples: Wild Roots, Highway Racer 2.
- Cover sets shown: Highway Racer 2, CrazyMx, Smash Karts, Crazy Crypt. Good covers are "clear and eye-catching"; badly designed covers don't get clicked.

### Preview video
Most thumbnails play a video preview on hover. Make a "compelling gameplay video" of exciting, visually appealing moments.

#### Video requirements (MUST)
| Item | Rule |
|---|---|
| Length | **15 to 20 seconds**; "longer videos will be cut to 20 seconds" |
| Size | **<= 50 MB** |
| Landscape (mandatory) | full-screen, **1080p, 16:9** |
| Portrait (mandatory) | full-screen, **1080p, 2:3** |
| Count | **2** videos (one per orientation) |
| Frame rate, format | not stated |

#### Avoid these elements (MUST NOT)
- a black screen and logo transition
- black bars at the top and bottom
- the default mouse cursor
- "Play Now" text or other promotional text
- app or social media icons

#### Other rules
- **No fast-forwarding**: "We automatically speed up the video slightly when processing it."
- **No sound.**
- **Open on the static cover**, so the thumbnail flows smoothly into the preview.
- Animated video is allowed "as long as it represents the gameplay and is not misleading."

#### What to show, by genre
- Driving: expensive cars, varied maps and weather, dashboard camera.
- Multiplayer: a full lobby, cycling through maps, the biggest celebration or prize.
- Action: intense battles across modes, weapons, killstreaks, impressive builds.
- Progression: evolution and customisation, varied modes.

#### Tools
ClipChamp (Windows), iMovie (Mac), HandBrake (converter).
- Example videos embedded: Holey.io, MMA Manager 2, Horror Tale 2 (no text description).

---

## Requirements: Quality guidelines

- URL: https://docs.crazygames.com/requirements/quality/
- Title: Quality guidelines - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction, near-verbatim)

### Labels
The whole page sits under a **Guideline** banner (recommended, not mandatory). The page says it is not exhaustive and that success is subjective. "The guidelines should be used alongside our mandatory requirements." There are no numbers on the page.

### Onboarding
- Give new users a simple onboarding phase they land in directly.
  - Put onboarding inside gameplay.
  - Teach the core, not every feature.
  - "Make the onboarding phase skippable."
- Favour visuals and keep text short.
- Show the controls with a keyboard overlay or mouse gestures.
- UI clarity:
  - Buttons are clearly labelled with how to proceed.
  - "Buttons are not sized to encourage ads or other behaviors."
  - Buttons have no delays that confuse users or push other behaviour.

### General principles
Clear, reachable goals; easy to learn; easy to understand (correct, clear, well-translated language, or universal graphic prompts); consistent, intuitive controls throughout.

### What makes your game fun
1. Responds quickly to player actions.
2. Challenge, strategy and story are balanced and well paced.
3. A comfortable, intuitive layout.
4. Comfortable, fitting audio.
5. An interface designed for the device (desktop, optionally mobile).
6. Different player segments can enjoy it.
7. An interesting story or scenario, where it applies.
8. No overly repetitive or "boring" tasks.
9. Information is processed quickly, for smooth flow.
10. Solo play is as prominent as playing with friends when both exist; if solo play is not available, the game says so clearly.

### Is your game unique?
- Easy to extend with new levels, art or story.
- "Major features such as the game's genre should not change after submission."
- Maintained and updated often.
- Not easily confused with a game that has a similar name or iconography.
- No common identifier as the name unless you own the IP: "Super Chess" is unique and "Chess" is not; "Scrabble" is unique but only its IP holder may use it.

### Is your game aesthetically pleasing?
- Graphics: high quality and high resolution, consistent resolution throughout, no defects such as compression artefacts.
- Audio: consistent levels, not too loud or too quiet, music that suits the visuals.
- A consistent, coherent style: no switching between realistic and cartoony, or between high and low resolution.
- Honest about its genre: the name and imagery on CrazyGames must reflect the gameplay. Change the name or imagery only when needed, such as after a big update or a visual overhaul.

### Restricted keys
- Controls should be intuitive and easy to learn.
- "Preferably make your key bindings adapt to the user's keyboard layout" instead of making users rebind keys. For example, on French AZERTY keyboards WASD becomes **ZQSD**.
- Avoid common browser keys:
  - **Escape** closes fullscreen.
  - **Ctrl/Cmd + W** closes the tab (you can disable this while the user is in fullscreen).

---

## SDK: Introduction

- URL: https://docs.crazygames.com/sdk/intro/
- Title: Introduction - CrazyGames Documentation (SDK)
- Fetched: 2026-10-23 (summarised extraction; code and API names kept as shown)

### Scope
- Follow the requirements (technical, gameplay, ads, account) while integrating.
- **The HTML5, Unity and Godot SDKs support every scenario.** Other SDKs may lack some functions, but basic integration often works through the HTML5 SDK.

### Modules
| Module | Purpose |
|---|---|
| `ad` | video ads and adblock detection |
| `banner` | banners (one engine row shows "Not supported") |
| `game` | game events and integration |
| `user` | the logged-in user |
| `data` | user data that persists across devices |
| In-game purchases | not a separate module |

### HTML5
```html
<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>
```
- Put it in the `<head>` of `index.html`, before the game code.
- `await window.CrazyGames.SDK.init();` **must be awaited**; the SDK can't be used until it has initialized. Do it before the game starts, for example on the loading screen.
- The SDK uses promises and **has no `callback` parameter**. Without `await`, use `.then(...).catch(...)`. The HTML5 docs show `await` only.

### Unity
- Package: `https://sdk.crazygames.com/UnityCrazySDK.unitypackage`; changelog: `https://sdk.crazygames.com/UnityChangelog.md`; namespace `using CrazyGames;`
- Info: delete any old `CrazySDK` and `CrazyOptimizer` folders before importing.
- `CrazySDK.Init(() => { /* initialization finished */ });` Don't call SDK methods before the callback fires.
- Don't initialize inside `[RuntimeInitializeOnLoadMethod(...)]`; it can clash with the SDK's own use of it (sitelock).
- Initialize in a separate scene, such as `CrazySDK/Demo/LoadingScene`. Make it the first scene in the build and set `nextSceneName` on the `CrazySDKLoadingScene` object.
- `CrazySDK.IsAvailable` must be true before you use the SDK. It is true on CrazyGames, in the Editor and on localhost; false on other platforms (Android, iOS builds) and on whitelisted domains.
- `CrazySDK.IsInitialized` can be polled.
- Iframed games: `IsAvailable` doesn't work there. Add a query parameter such as `isCrazyGames=true` to the iframe URL when you submit, and check `Application.absoluteURL.Contains("isCrazyGames=true")`.
- Use the custom build feature for leaner builds.
- **Only Brotli- or Gzip-compressed builds run on CrazyGames; uncompressed development builds will not run.**
- **Sitelock** is applied automatically at game start, so the game runs only on CrazyGames.com and affiliated sites. It blocks your own domain by default; whitelist yours in `CrazySDK/Resources/CrazyGamesSettings`. **Reimporting the SDK resets these settings.**

### GameMaker
- Download: https://github.com/YoYoGames/GMEXT-CrazyGames/releases ; import with Tools -> Import Local Package.
- Folders: `CrazyGames` (extension, enums, constants), `CrazyGames DEMO` (needs `GM Extensions`), and `ViewScaler`/`obj_view_scaler_controller` (recommended canvas scaling).
- `crazy_init(success_callback, error_callback)` and `crazy_started()`. Works on the HTML export only.

### Construct 3
- **Warning: not compatible with Worker mode.** Set Project -> Advanced -> "Use worker" = No.
- Loading layout (demo `CrazySDKLoadingDemo`): on "System > On start of layout", inject a `<script src="https://sdk.crazygames.com/Construct3CrazySDK-v3.js">`; on load call `window.ConstructCrazySDK.init()` then `runtime.goToLayout(nextLayoutName)`; on error log "Failed to load Construct3CrazySDK script."
- Make SDK calls from scripts in event sheets. Demo: https://sdk.crazygames.com/CrazySDKDemo-v3.c3p
- Construct uses its own save mechanism, not `localStorage`.

### Godot
- Download: https://store-beta.godotengine.org/asset/crazygames/crazysdk
- 3.x: copy `crazysdk-godot-3` to `res://addons/crazygames`, enable the plugin, then `yield(CrazyGames.is_initialised_async(), "completed")`.
- 4.x: copy `crazysdk-godot-4` to `res://addons/crazygames`, enable the plugin, then `await CrazyGames.is_initialised_async()`.
- Callback signals come through `CrazyGamesBridge.callbacks`. 3.x uses `JavaScript` and `yield`; 4.x uses `JavaScriptBridge` and `await`. On non-web exports the SDK marks itself initialized at once, so the call doesn't block.

### Cocos
- Download: https://sdk.crazygames.com/CocosCrazySDK.zip ; import with assets -> Import Asset Package. Demo: `CrazySDK/CrazySDKDemo`; loading scene `CrazySDKDemoLoadScene`.
- `import CrazySDK from "./CrazySDK";`, then `CrazySDK.isSupportedPlatform` (mobile and desktop browsers) and `await CrazySDK.init();`

### Migrating from v2 to v3 (HTML5)
- The SDK now needs manual `init()`.
- These are now plain properties (they used to be async getters): `SDK.environment`, `SDK.user.isUserAccountAvailable`, `SDK.user.systemInfo`.
- Renamed: `sdkGameLoadingStart()` -> `loadingStart()`, and `sdkGameLoadingStop()` -> `loadingStop()`.
- v3 errors always have `code` and `message`, for example `{code: 'userAlreadySignedIn', message: 'The user is already signed in'}`.

### Environments
| `environment` | Where | Behaviour |
|---|---|---|
| `local` | `localhost`, `127.0.0.1`, the Unity/Construct/Cocos editors | demo ads and banners, simulated behaviour, console logging |
| `crazygames` | CrazyGames domains | normal |
| `disabled` | any other domain, including your own host | **every SDK call throws** |
| Preview tool | `crazygames.com/preview` (QA environment) | the most realistic; **needed to get a working Xsolla token** |

- Read it with `window.CrazyGames.SDK.environment` (HTML5), `CrazySDK.environment` (Unity, Cocos) or `CrazyGames.get_environment()` (Godot).
- Recommendation: check the environment and don't call the SDK unless it is `local` or `crazygames`.
- In local mode, video ad requests show an overlay text, SDK console logging is on, user requests return demo data, and only demo banners show.
- **`?useLocalSdk=true`** forces local mode on any domain or IP.
- Testing: Unity in the Editor or on localhost (sitelock blocks it elsewhere); GameMaker in debug mode; Construct in preview or locally; Godot with the CrazyGames export preset, the HTML renamed to `index.html`, served on localhost.

---

## SDK: Video ads

- URL: https://docs.crazygames.com/sdk/video-ads/
- Title: Video ads - CrazyGames Documentation
- Module: `ad`
- Fetched: 2026-10-23 (summarised extraction; API names and code kept as shown)

### Labels on the page
Info and Warning callouts. Requirements are linked to the Ads requirements page.
- **Info:** "Games are rejected **without feedback** if they do not follow the advertisement requirements."

### Accessing the module
| Engine | Access |
|---|---|
| HTML5 | `window.CrazyGames.SDK.ad` |
| Unity | `CrazySDK.Ad` (demo scene `CrazySDK/Demo/AdModule`) |
| GameMaker | `crazy_ad_request_ad`, `crazy_ad_has_ad_block` |
| Construct | `window.ConstructCrazySDK.ad` |
| Godot 3/4 | `CrazyGames.Ad` |
| Cocos | `CrazySDK.ad` |

### Ad types
- `"midgame"` (Unity `CrazyAdType.Midgame`): at natural breaks, such as after a death or a completed level.
- `"rewarded"` (Unity `CrazyAdType.Rewarded`): the user asks for it in exchange for a reward, such as an extra life, a retry, a starting bonus item or extra starting health.

### HTML5 API
```js
const callbacks = {
  adFinished: () => console.log("End midgame ad"),
  adError: (error) => console.log("Error midgame ad", error),
  adStarted: () => console.log("Start midgame ad"),
};
window.CrazyGames.SDK.ad.requestAd("midgame", callbacks);
// or
window.CrazyGames.SDK.ad.requestAd("rewarded", callbacks);

const result = await window.CrazyGames.SDK.ad.hasAdblock(); // boolean
```
- `requestAd(type: "midgame" | "rewarded", callbacks)`; the callbacks are optional.
- `hasAdblock(): Promise<boolean>`

### Callbacks
| Callback | When | What to do |
|---|---|---|
| `adStarted` | the ad starts | pause the game, mute audio |
| `adFinished` | the ad completes | resume, unmute; **grant the reward here** for rewarded ads |
| `adError` | failed, unfilled or blocked | resume, unmute; no reward |
Godot names the signals `ad_started`, `ad_finished` and `ad_error`, on `CrazyGamesBridge.callbacks`.

### Error codes (`error.code`)
The shape is `{ code, message }`, for example `{"code": "unfilled", "message": "No ad available"}`.
- `adsDisabledBasicLaunch`: ads are off during Basic Launch
- `unfilled`: no ad available
- `adblock`: an adblocker prevented the ad
- `adCooldown`: requested too soon; the usual midgame interval is **3 minutes**, counting rewarded and preroll ads
- `other`

Games **must handle `adError`**. CrazyGames uses fallback banners and house ads to reduce unfilled calls.

### Rules
- **Warning:** mute audio and pause the game on `adStarted`; unmute and resume on `adFinished` or `adError`.
- **Info:** the page says the game is paused automatically when an ad is requested and resumes when it ends. In context this is the engine wrapper (Unity) behaviour; HTML5 games still pause themselves.
- **Construct warning:** set the time scale to 0 before the ad and back to 1 after it (use "Wait for previous action"), and stop the audio.
- **Adblock info:** games must work with an adblocker present, and detection is not foolproof. You may lock extras (custom skins, some levels) to encourage turning the adblocker off. Turning it off usually needs a page refresh, so **save progress first**.

### Adblock detection by engine
- HTML5 and Cocos: `await hasAdblock()` -> boolean.
- Unity: the `AdblockStatus` property (`Detecting` -> `Present`/`Missing`); `HasAdblock(Action<bool> cb)` (fires at once if detection is done; use it on singletons or `DontDestroyOnLoad` objects); `HasAdblockAsync()` -> bool.
- GameMaker: `crazy_ad_has_ad_block(successFn(result), errorFn(error))`.
- Construct: `runtime.globalVars.HasAdblock = await window.ConstructCrazySDK.ad.hasAdblock();` (the global must be boolean).
- Godot: the `CrazyGames.has_adblock` property.

### Other engines (brief)
- Unity: `CrazySDK.Ad.RequestAd(CrazyAdType type, Action adStarted, Action<error> adError, Action adFinished)`; `null` callbacks are allowed.
- GameMaker: `crazy_ad_request_ad("midgame"|"rewarded", startedFn, errorFn(err), finishedFn)`.
- Construct: `await window.ConstructCrazySDK.ad.requestAd("midgame")`.
- Godot 3: `yield(CrazyGames.Ad.request_ad_async("midgame"), "completed")`; Godot 4: `await CrazyGames.Ad.request_ad_async("rewarded")`. The result is `"finished"` or an error payload.
- Cocos: `CrazySDK.ad.requestAd('midgame', { adError, adStarted, adFinished })`.

---

## SDK: Banners

- URL: https://docs.crazygames.com/sdk/banners/
- Title: Banners - CrazyGames Documentation
- Module: `banner`
- Fetched: 2026-10-23 (summarised extraction; API names kept as shown)

### Labels
An Info note (demo scene) and a "Requirements for Advertisements" callout pointing to requirements/ads, which says non-compliant games are rejected without feedback.

### Static banner sizes (allowed)
| Name | px |
|---|---|
| Leaderboard | **728 x 90** |
| Medium | **300 x 250** |
| Mobile | **320 x 50** |
| Main | **468 x 60** |
| Large Mobile | **320 x 100** |

### Responsive banner sizes (allowed)
970x90, 320x50, 160x600, 336x280, 728x90, 300x600, 468x60, 970x250, 300x250, 250x250, 120x600.
A responsive banner is centred in its container, and **if the container fits none of these sizes, no ad renders.**

### HTML5 (`window.CrazyGames.SDK.banner`)
```html
<div id="banner-container" style="width: 300px; height: 250px"></div>
```
```js
try {
  await window.CrazyGames.SDK.banner.requestBanner({ id: "banner-container", width: 300, height: 250 });
} catch (e) { console.log("Banner request error", e); }

await window.CrazyGames.SDK.banner.requestResponsiveBanner("responsive-container");
window.CrazyGames.SDK.banner.clearBanner("banner-container");
window.CrazyGames.SDK.banner.clearAllBanners();
```
- `requestBanner({ id, width, height }): Promise`
- `requestResponsiveBanner(containerId): Promise`
- `clearBanner(containerId)`, `clearAllBanners()`

### Error codes (`{ code, message, containerId }`)
`bannersDisabledBasicLaunch`, `unfilled`, `missingId`, `notVisible`, `noAvailableSizes`, `notCreated`, `videoAdPlaying`, `invalidSize`, `bannerCooldown`, `maxRefreshReached`, `bannersDisabledMobileApp`, `other`.

### Limits and rules
- **Refresh at most once every 30 seconds per container**; a sooner call returns `bannerCooldown`.
- **At most 120 refreshes per gaming session, counted per banner size**; beyond that, `maxRefreshReached`.
- The same banner can be shown again only 30 seconds after it was last shown.
- The banner must sit **fully inside the game window**, and its container must be visible (`notVisible`).
- **Clear banners after hiding them** (`clearBanner`/`clearAllBanners` or the engine equivalent), or old banners may flash briefly.
- Banners are disabled in **Basic Launch** (`bannersDisabledBasicLaunch`) and **inside the mobile app** (`bannersDisabledMobileApp`).
- Banners can't render or refresh **while a video ad is playing** (`videoAdPlaying`).
- This page sets no maximum count; requirements/ads says **at most 2 per screen**.

### Other engines (brief)
- **Unity** (`CrazySDK.Banner`): drag the banner prefab from `CrazySDK/Resources` into the scene, and set the size and the position on the `Banner` child. Show or hide with `SetActive`. **Call `CrazySDK.Banner.RefreshBanners()`** after showing or hiding, when a scene with visible banners loads, and after a scene change. No responsive banners. Demo: `CrazySDK/Demo/BannerModule`. To test in a browser, use a WebGL template that fills the screen (such as PWA), or positions won't match the editor.
- **GameMaker:** `crazy_banner_request_banner(id, w, h, position, ok, err)` (with `CRAZY_BANNER_POSITION.CENTER_MIDDLE`), `crazy_banner_request_responsive_banner(...)`, `crazy_banner_clear_all_banners()`, `crazy_banner_clear_banner(id)`, `crazy_banner_clear_responsive_banner(id)`.
- **Construct:** `await window.ConstructCrazySDK.banner.requestBanners([{id,width,height,x,y}])`, with x/y measured from the bottom-left; calling it again replaces the previous banners. `await hideAllBanners()`. No responsive banners.
- **Godot:** the `CrazyBanner` control (`res://addons/crazygames/Utils/crazy_banner.tscn`, the 5 static sizes). Call `CrazyGames.Ad.refresh_banners()` after showing or hiding; `CrazyGames.Ad.request_banners([])` clears them all. No responsive banners.
- **Cocos:** banners not supported.

---

## SDK: Game module

- URL: https://docs.crazygames.com/sdk/game/
- Title: Game - CrazyGames Documentation
- Module: `game`
- Fetched: 2026-10-23 (summarised extraction; API names kept as shown)

### Access
HTML5 `window.CrazyGames.SDK.game` · Unity `CrazySDK.Game` · GameMaker `crazy_game_*` · Construct `window.ConstructCrazySDK.game` · Godot `CrazyGames.Game` · Cocos `CrazySDK.game`

### 1. Game settings
`window.CrazyGames.SDK.game.settings` (Unity `CrazySDK.Game.Settings`, GameMaker `crazy_game_settings()`, Godot `CrazyGames.Game.get_game_settings()`)

| Field | Meaning | Local test override |
|---|---|---|
| `disableChat: boolean` | when true, turn chat off (if the game has chat) | `?disableChat=true` |
| `muteAudio: boolean` | when true, turn game audio off | `?muteAudio=true` |

- **`muteAudio` must win over the in-game audio toggles.** An in-game "Audio On" control must not turn back on audio the SDK has muted.
- **A Full Implementation requires `muteAudio` support** for HTML5, Unity, Cocos and Construct.
- Info (Unity): a game submitted as Unity (not HTML5) has its muting handled automatically and doesn't need `muteAudio`.
- Listener:
  ```js
  const listener = (newSettings) => { /* apply disableChat / muteAudio */ };
  window.CrazyGames.SDK.game.addSettingsChangeListener(listener);
  window.CrazyGames.SDK.game.removeSettingsChangeListener(listener);
  ```
  Unity: `AddSettingsChangeListener(Action<GameSettings>)` / `RemoveSettingsChangeListener`.

### 2. gameplayStart / gameplayStop
```js
window.CrazyGames.SDK.game.gameplayStart();
window.CrazyGames.SDK.game.gameplayStop();
```
(Unity `GameplayStart()`/`GameplayStop()`, GameMaker `crazy_game_gameplay_start()`/`_stop()`, Godot `gameplay_start()`/`gameplay_stop()`)
- **MUST** call `gameplayStart` whenever play begins or resumes: game start, resume, revive, next level and so on.
- **The first `gameplayStart` determines the game's initial download size.**
- **MUST** call `gameplayStop` at every break: entering a menu, ending a level, pausing. Call `gameplayStart` again when play resumes.
- **Don't** call them when the user switches focus or leaves the game area; the platform handles that.
- Purpose: lets the site avoid heavy work during active play.

### 3. loadingStart / loadingStop
```js
window.CrazyGames.SDK.game.loadingStart();
window.CrazyGames.SDK.game.loadingStop();
```
- Call `loadingStart` when loading begins, and `loadingStop` when it ends and gameplay is about to start.
- Unity: not supported (the Unity loader handles it). Godot: not needed. Construct: not supported. GameMaker: `crazy_game_loading_start()`/`_stop()`.
- Optional (requirements/technical).

### 4. happytime
```js
window.CrazyGames.SDK.game.happytime();
```
(Unity `HappyTime()`, GameMaker `crazy_game_happytime()`, Godot `happy_time()`)
- Triggers a website celebration, such as confetti, for an achievement like beating a boss or setting a high score.
- **Info:** use it sparingly. Not for routine events such as finishing a level or picking up an item.

### 5. reportGameCompletedPercentage (HTML5 only)
```js
window.CrazyGames.SDK.game.reportGameCompletedPercentage(value); // 0..100
```
- Tells CrazyGames how far the player has got. It can enable restart options after completion, tell returning players about updates, and may unlock future features.
- At minimum, report 100; intermediate values are encouraged. Report as the player advances through levels, chapters or missions. Without milestones, report 100 at completion.
- Endless or sandbox games may define their own 100%, applied consistently. Progress should generally only rise. Report 100 only at a meaningful completion point.
- After a content update, report the corrected value on load; a player who was at 100% may drop lower.
- Not supported in Unity, GameMaker, Construct, Godot or Cocos.

### 6. Game context (feedback)
```js
window.CrazyGames.SDK.game.setGameContext({ level: "3", weapon: "bow" });
window.CrazyGames.SDK.game.clearGameContext();
```
- Attaches in-game data (level, weapon, gold, skins) to user feedback. That feedback is emailed to you and shown on the Developer Portal, which helps reproduce issues.
- Set it at the start of a relevant state; **MUST** clear it when it no longer applies (for example, on leaving the level).
- Unity: `SetGameContext(Dictionary<string,string>)` / `ClearGameContext()`. Not in GameMaker or Godot.

### 7. Multiplayer
#### Instant multiplayer
- `window.CrazyGames.SDK.game.isInstantMultiplayer` (boolean). Unity: `CrazySDK.Game.IsInstantMultiplayer`; GameMaker: `crazy_game_is_instant_multiplayer()`; Cocos: `CrazySDK.game.isInstantMultiplayer`.
- **Deprecated:** `isInstantJoin` / `IsInstantJoin`.
- Check it at SDK init. If true, create a new room or lobby at once; otherwise go to the normal next screen.

#### Room data
```js
window.CrazyGames.SDK.game.updateRoom({ roomId: "eu-1234" });
window.CrazyGames.SDK.game.updateRoom({ isJoinable: true, inviteParams: { roomId: "eu-1234" } });
window.CrazyGames.SDK.game.updateRoom({ isJoinable: false }); // room full
window.CrazyGames.SDK.game.leftRoom();
```
- A room is any unique place where the user plays or waits. It need not exist on a server; a WebRTC peer connection counts.
- `roomId` must be unique; for multi-region games, combine the room and region IDs. `isJoinable` lets others invite or join. `inviteParams` go to anyone who accepts an invite or joins.
- The fields can be combined in one call. Unity: `UpdateRoom(new UpdateRoomInput(){...})`, `LeftRoom()`. Not in GameMaker or Godot.

#### Room join listener
```js
const onJoin = (inviteParams) => { /* go to inviteParams' room */ };
window.CrazyGames.SDK.game.addJoinRoomListener(onJoin);
window.CrazyGames.SDK.game.removeJoinRoomListener(onJoin);
```
- If the user is already in the game, the listener fires. If they are sent to the game page, the game loads, so **MUST check `inviteParams` at game start**: if it is not null, the game came from an invite and should go to the right room.
- Unity: `AddJoinRoomListener`/`RemoveJoinRoomListener`, removed in `OnDestroy`. Not in GameMaker or Godot.

#### Invite link
```js
const link = window.CrazyGames.SDK.game.inviteLink({ roomId: "12345", region: "eu" });
const roomId = window.CrazyGames.SDK.game.getInviteParam("roomId"); // string | null
const all = window.CrazyGames.SDK.game.inviteParams; // null if not started from an invite
```
- Add `region` if the game only accepts players from one region.
- Unity: `InviteLink(Dictionary<string,string>)`, `CopyToClipboard(link)`, `GetInviteLinkParameter(name)`. GameMaker: `crazy_game_invite_link(json_stringify(params))`, `crazy_game_get_invite_param(name)`. Godot: `CrazyGames.Game.request_invite_url({...})`, `CrazyGamesBridge.copy_to_clipboard(url)`, `CrazyGames.Game.get_invite_link_param(name)`. Construct: `await inviteLink(...)`.
- Tip: read the invite parameters during SDK init and route straight to the room.

#### Invite button (deprecated; replaced by room data)
- `showInviteButton({...})` returns a link in the same format as `inviteLink`; `hideInviteButton()`.
- **MUST** hide it when the user can't be joined any more (room full, game started, lobby cancelled).
- Unity `ShowInviteButton`/`HideInviteButton`; GameMaker `crazy_game_show_invite_button`/`crazy_game_hide_invite_button`; Godot `show_invite_button`/`hide_invite_button`. Not in Construct.

---

## SDK: User module

- URL: https://docs.crazygames.com/sdk/user/
- Title: User - CrazyGames Documentation
- Module: `user`
- Fetched: 2026-10-23 (summarised extraction; API names kept as shown)

### Purpose
Authenticates players who are logged in to CrazyGames, so account games need no in-game registration. Players are also logged in automatically on their other devices.

Access: HTML5 `window.CrazyGames.SDK.user` · Unity `CrazySDK.User` (demo `CrazySDK/Demo/UserModule`) · GameMaker `crazy_user_*` · Construct `window.ConstructCrazySDK.user` (same as HTML5) · Godot `CrazyGames.User` · Cocos `CrazySDK.user`

### API (HTML5)
```js
const available = window.CrazyGames.SDK.user.isUserAccountAvailable; // property
const user = await window.CrazyGames.SDK.user.getUser();             // object | null
const systemInfo = window.CrazyGames.SDK.user.systemInfo;            // property
const friends = await window.CrazyGames.SDK.user.listFriends({ page: 1, size: 10 });
const token = await window.CrazyGames.SDK.user.getUserToken();       // JWT
const user2 = await window.CrazyGames.SDK.user.showAuthPrompt();
window.CrazyGames.SDK.user.addAuthListener(listener);
window.CrazyGames.SDK.user.removeAuthListener(listener);
const response = await window.CrazyGames.SDK.user.showAccountLinkPrompt(); // { response: "yes" | "no" }
```

#### isUserAccountAvailable
False on other domains that embed the game. **Check it before any account feature.**

#### getUser -> user | null
| Field | Notes |
|---|---|
| `__dangerousUserId` | **Warning: never use it for authentication**; anyone can inject IDs in the browser. Use the token. |
| `username` | **6 to 20 characters**: letters, digits, `.` and `_` |
| `profilePictureUrl` | URL |

#### systemInfo
| Field | Values |
|---|---|
| `countryCode` | e.g. `"US"` |
| `locale` | e.g. `"en-US"`. **Warning:** use this to pick the game language |
| `device.type` | `desktop`, `tablet`, `mobile` |
| `os.name`, `os.version` | ua-parser-js format |
| `browser.name`, `browser.version` | ua-parser-js format |
| `applicationType` | `google_play_store`, `apple_store`, `pwa`, `web` |

#### listFriends({ page, size })
- Pages start at **1**; the **maximum page size is 50**.
- Response: `{ friends: [{ id, username, profilePictureUrl }], page, size, hasMore, total }`
- Errors: `userNotAuthenticated`, `rateLimited` (**at most one call every 250 ms**), `requestInProgress` (one call at a time), `unexpectedError`.
- Not in GameMaker or Godot. (requirements/multiplayer calls this "Get friends".)

#### getUserToken -> JWT
- Send it to your server and verify it there.
- **The token lives 1 hour.** The method refreshes it, so **don't store the token**; call the method each time you need one.
- Errors: `userNotAuthenticated`, `unexpectedError`.
- Payload: `userId` (use this server-side), `gameId` (e.g. `"20267"`), `username`, `profilePictureUrl`, `iat`, `exp` (`iat` + 1 h).
- Verify with **RS256** against the public key at **`https://sdk.crazygames.com/publicKey.json`** (`resp.data["publicKey"]`). Fetch it each time, or cache it and re-fetch when decoding fails, because the key can change. The example uses axios plus `jsonwebtoken.verify(token, key, { algorithms: ["RS256"] })`.
- **Warning: don't decrypt tokens on the client.** Use `getUser` for the username and avatar.

#### showAuthPrompt -> user
- Opens the CrazyGames login/register popup.
- Errors: `showAuthPromptInProgress`, `userAlreadySignedIn`, `userCancelled`.

#### addAuthListener / removeAuthListener
- Fires when the player **logs in**. **Logging out does not fire it**, because the whole page refreshes.
- **Guideline:** if the CrazyGames account is your identifier, fetch the user's progress from your back end on login.
- **Info:** with the Data module or Automatic Progress Save, **the game reloads automatically on login**.

#### showAccountLinkPrompt
- Shows the modal asking permission to link the CrazyGames account to the in-game account.
- **Guideline:** use the provided modal; don't build your own.
- Response: `{ "response": "yes" | "no" }` (HTML5, GameMaker, Cocos); Unity returns a bool.
- Errors: `showAccountLinkPromptInProgress`, `userNotAuthenticated`.

### Error codes
`userNotAuthenticated`, `rateLimited`, `requestInProgress`, `unexpectedError`, `showAuthPromptInProgress`, `userAlreadySignedIn`, `userCancelled`, `showAccountLinkPromptInProgress`.

### Local testing (localhost / 127.0.0.1, hard-coded defaults)
| Query parameter | Values |
|---|---|
| `?user_account_available=false` | (default true) |
| `?show_auth_prompt_response=` | `user1`, `user2`, `user_cancelled` |
| `?link_account_response=` | `yes`, `no`, `logged_out` |
| `?user_response=` | `user1`, `user2`, `logged_out` |
| `?token_response=` | `user1`, `user2`, `expired_token`, `logged_out` |
- Defaults: getUser -> user1; token -> user1; link prompt -> yes; auth prompt -> user1.
- Unity Editor: configured in `CrazySDK/Resources/CrazyGamesSettings`. Godot and GameMaker: serve the web export on localhost.

### Other engines (brief)
Unity: `IsUserAccountAvailable`, `GetUser(cb)`/`GetUserAsync()`, `SystemInfo`, `ListFriends(page,size,cb)`/`ListFriendsAsync`, `GetUserToken(cb)`/`GetUserTokenAsync()`, `ShowAuthPrompt(cb)`/`ShowAuthPromptAsync()`, `AddAuthListener(Action<PortalUser>)`/`RemoveAuthListener`, `ShowAccountLinkPrompt(cb)`/`ShowAccountLinkPromptAsync()`.
GameMaker: `crazy_user_is_user_account_available()`, `crazy_user_get_user(ok, fail)`, `crazy_user_get_user_system_info()`, `crazy_user_get_user_token(ok, fail)`, `crazy_user_show_auth_prompt(ok, fail)`, `crazy_user_add_auth_listener(fn)`, `crazy_user_remove_auth_listener()`, `crazy_user_show_account_link_prompt(ok, fail)`.
Godot: `CrazyGames.User.is_user_account_available()`, `get_user_async()`, `CrazyGamesBridge.get_system_info()`, `get_user_token_async()`, `show_auth_prompt_async()`, the signal `CrazyGamesBridge.callbacks.auth_listener_complete`, `show_account_link_prompt_async()` (3.x uses `yield`, 4.x `await`).

---

## SDK: Data module (progress save)

- URL: https://docs.crazygames.com/sdk/data/
- Title: Data - CrazyGames Documentation
- Module: `data`
- Fetched: 2026-10-23 (summarised extraction; API names kept as shown)

### Overview
- Saves and loads data for logged-in CrazyGames users and syncs it across every device they play on.
- Guest data lives in localStorage; if the guest logs in later, it is synced and backed up to the account.

### Warnings and tips
- **Warning:** choose the right **Progress Save** toggle in the submission flow ("Yes, using the Data Module from the CrazyGames SDK"), **or the data module is disabled** (`dataModuleDisabled`).
- **Warning:** rely fully on the Data module for saves, for guests and logged-in users alike. **Don't rely on local saves.**
- **Tip ("Avoid losing user progress"):** always read the data before you write it, so you don't overwrite earlier progress.
- **The SDK must be initialized before any data call.** Initialize during the loading screen, because init preloads all game data and can take a while if a lot is stored.

### HTML5 API (mirrors localStorage)
```js
await window.CrazyGames.SDK.init();
window.CrazyGames.SDK.data.setItem("gold", 100);
const gold = window.CrazyGames.SDK.data.getItem("gold"); // string | null
window.CrazyGames.SDK.data.removeItem("gold");
window.CrazyGames.SDK.data.clear();
```
- `clear(): void`
- `getItem(key: string): string | null`
- `removeItem(key: string): void`
- `setItem(key: string, value: string): void`
(The calls are synchronous; the network sync happens in the background.)

### Limits and sync
- **Size limit: 1 MB = 1,048,576 bytes of JSON-stringified game data.** The console warns as you approach it; above it, data is **not backed up**.
- **Saves are debounced by 1 second** (several calls in that window save together), stretching **to as much as 30 seconds** in some cases.

### Errors (`{ code, message }`)
- `dataLimitExcedeed` (the page's spelling): "Game data when converted to a JSON string cannot exceed 1048576 bytes. Data was not saved"
- `dataModuleDisabled`: the Data module option wasn't chosen at submission
- `other`

### Guest and logged-in behaviour
- Guest: localStorage; nothing to do when the guest signs in.
- On sign-in: the SDK loads the account's data if there is any. **If the user hasn't played the game before, the guest data moves to the account.** (sdk/user: with the Data module, the game reloads automatically on login.)
- On sign-out: back to the guest data.

### Migrating an existing game
Copy existing localStorage keys (HTML5, Construct, Cocos) or PlayerPrefs keys (Unity) into the Data module on first run after the update, so returning players keep their progress. Godot: a one-time migration of browser-local saves into `CrazyGames.Data`.

### Other engines (brief)
- Unity `CrazySDK.Data` (like PlayerPrefs): `SetInt/GetInt(key[, default])`, `SetFloat/GetFloat`, `SetString/GetString`, `HasKey`, `DeleteKey`, `DeleteAll`. A PlayerPrefs wrapper script is linked for builds without the SDK (mobile).
- GameMaker: `crazy_data_get_item(key)`, `crazy_data_set_item(key, value)`, `crazy_data_remove_item(key)`, `crazy_data_clear()` (irreversible).
- Construct: `window.ConstructCrazySDK.data.getItem/setItem/removeItem/clear`.
- Godot: `CrazyGames.Data.data_set_item(key, value)`, `data_get_item(key)`, `data_has_key(key)`.
- Cocos: `CrazySDK.data.getItem/setItem/removeItem/clear`.

### Not on this page
Automatic Progress Save details (see the APS page) and conflict-resolution rules beyond "account data wins if present".

---

## SDK: In-game purchases

- URL: https://docs.crazygames.com/sdk/in-game-purchases/
- Title: In-game purchases - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; API names kept as shown)

### Eligibility
- **Invite only**: contact CrazyGames to use it.
- **Only signed-in users may buy.** Guests must not be able to buy items.
- Integrate the User module (if you have a back end) and the Data module, to save progress securely. (requirements/account-integration: APS is **not allowed** for games with in-game purchases.)
- If the game uses Xsolla or any external payment flow, **turn it off in the CrazyGames App**, that is, when `systemInfo.applicationType` is `google_play_store` or `apple_store`. On mobile-friendly web builds, hide or disable the purchase UI inside the App.
- No revenue share, pricing, currency or refund rules are on this page.

### Xsolla setup
**A. Standard (linked to CrazyGames accounts)**
1. Create the game on the Developer Portal and ask CrazyGames to generate the token credentials.
2. Use the token from `getXsollaUserToken()`; purchases link to the CrazyGames account automatically. Only the **Project ID** (from CrazyGames) is needed; Xsolla creates the account from the user ID in the token.

**B. Custom (your own accounts)**
1. Generate the Xsolla credentials yourself in the CrazyGames Xsolla project dashboard.
2. Orders must reference the CrazyGames `userId` (from the verified `getUserToken`), either as the user identifier or as `crazyGamesUserId` in `custom_parameters`. **Warning:** this applies whenever Xsolla is used without `getXsollaUserToken()`.

### Token method
```js
try {
  const token = await window.CrazyGames.SDK.user.getXsollaUserToken();
  const resp = await fetch(
    `https://store.xsolla.com/api/v2/project/${xsollaProjectId}/user/inventory/items`,
    { method: "GET", headers: { Authorization: `Bearer ${token}` } }
  );
} catch (e) { console.log(e); }
```
- It needs setup on CrazyGames' side, or it won't work.
- **Fetch the token before each use**; tokens are short-lived (about 1 hour) and the SDK refreshes them.
- **It works only on CrazyGames.com**, so test through the Developer Portal preview (sdk/intro: the Preview tool is needed for a working Xsolla token).
- Unity: `CrazySDK.User.GetXsollaUserToken((error, token) => ...)` / `GetXsollaUserTokenAsync()`, then `XsollaToken.Create(token)` and the Xsolla Unity SDK (`XsollaCatalog.Purchase(...)`). GameMaker: `crazy_user_get_xsolla_user_token(ok, err)`. Godot: `CrazyGames.User.get_xsolla_user_token_async()`.

### Xsolla REST endpoints listed
- Owned items: `GET https://store.xsolla.com/api/v2/project/{project_id}/user/inventory/items` (Bearer)
- Catalogue: `GET https://store.xsolla.com/api/v2/project/{project_id}/items/virtual_items` (Bearer optional)
- Payment token: `POST https://store.xsolla.com/api/v2/project/{project_id}/payment/item/{item_sku}`, with body such as `{ "quantity": 5, "sandbox": true }`
- Register orders with Xsolla's Shop Builder API.

### GameMaker PayStation helpers
`crazy_xsolla_open_paystation(token, callback, options_json)` and `crazy_xsolla_close_paystation`. Events: `CRAZY_XSOLLA_EVENT_INIT`, `_OPEN`, `_LOAD`, `_STATUS`, `_STATUS_INVOICE`, `_STATUS_DELIVERING`, `_STATUS_DONE`, `_CLOSE`, `_ERROR`.

### Order tracking (optional)
- Statuses: `new`, `done`, `canceled`. Track `done`; tracking `new` and `canceled` is recommended too.
- HTML5: `window.CrazyGames.SDK.analytics.trackOrder("xsolla", order)` (the order is the JSON from Xsolla's Order endpoint).
- Unity: `CrazySDK.Analytics.TrackOrder(PaymentProvider.Xsolla, orderStatus)`. GameMaker: `crazy_analytics_track_order(json_stringify(order))`. Not in Godot.

### Requirements (the page uses no MUST labels; written as requirements)
1. Register purchases against the CrazyGames account ID.
2. Give PayStation a **working close button**, so players can close it and carry on.
3. If PayStation opens in a new tab, tell players in text on the shop page to **allow browser popups**.
4. **Hide any "Back to the game" link after payment**: in the Xsolla dashboard, set "Manual redirect condition" to **None**.
5. **Never charge without crediting**, even if the player closes the window mid-payment. Use webhooks (`order_paid`, or the Webhooks API if you have no back end), the Inventory (described as the safest way to retrieve purchases), or client-side order tracking validated through webhooks or the inventory.
6. In the CrazyGames App, hide or disable the purchase UI.
- **Sandbox:** test with sandbox orders (`sandbox: true`). **Turn sandbox orders off before submitting.**

### Common mistakes
- The integration is complex; Xsolla's paystation-embed widget is simpler.
- On mobile the Back button can be hidden; Xsolla's close-button setting fixes it.
- Players can close the window by accident by clicking outside it or pressing Esc. Set `closeByClick` and `closeByKeyboard` to false (Unity: in `Assets/Xsolla/Core/Plugins/paystation.jslib`).

### Lootboxes and similar
- No special definition. The concern is hidden random content bought with money, or with virtual currency that money can buy. Wheels of fortune and card packs count. Other cases are reviewed one by one.
- Sales are restricted in **Belgium, China, the Netherlands, Serbia and Slovakia**.
- **Taiwan and South Korea:** restricted unless drop probabilities (for items of equal weight) are disclosed as percentages.
- **Japan:** restricted if both (a) the item received is worth at least the price of the box and (b) the Terms of Service do not forbid real-money trading and player-to-player resale.

---

## SDK: User account linking (HTML5 v3)

- URLs: https://docs.crazygames.com/sdk/user-linking/ (a stub linking to the two pages below), https://docs.crazygames.com/sdk/user-linking/user-linking-html5-v3/ and .../user-linking-unity/. These are linked from sdk/user but are not in the sidebar.
- Title: User account linking - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

### When it applies
- **Required if the game keeps other sign-in providers (Google, Facebook...) alongside CrazyGames accounts.**
- **Warning:** an advanced integration. Getting it wrong may delay release or lead to rejection. **Only the flows below are supported**, and CrazyGames gives **no technical support for merging or migrating accounts**.

### Preparation
- "Don't use the CrazyGames account as the identifier." Keep a back-end mapping between CrazyGames accounts and in-game account IDs. (This conflicts with requirements/account-integration; see the contradictions section of the digest.)

### Flow 1: at game launch (call `getUser()` every time)
**A. Not logged in to CrazyGames (`null`)**
1. Always let them play as a guest.
2. Optionally offer "Login with CrazyGames" (`showAuthPrompt`), other providers, or continue as guest.
3. Don't open the auth prompt automatically.

**B. Logged in to CrazyGames:** use `getUserToken()` on the server to check for a linked game account.
1. Linked: fetch the data and play. **A logged-in CrazyGames account always takes priority over in-game accounts.**
2. Not linked and no game account: **create one automatically**, linked to the CrazyGames account (fresh data).
3. Logged in in-game but not linked: show a "Link CrazyGames account" button that opens `showAccountLinkPrompt`. Linking only with fresh accounts is advised (avoid merging), or let the user choose which data to keep. **The outcome must always be a CrazyGames account linked to a new or existing in-game account.**

Diagram: game start -> get the CG user -> if logged out, show the CG auth prompt (cancel: play as guest; log in: go to the logged-in branch) -> if logged in: linked, then play; logged in-game but not linked, then ask to link, then play; has a linked account but not logged in-game, then log into it; not registered, then create an account or send to the login page.

### Flow 2: the game's login page
For games where users can log out or start as guests: add a CrazyGames login button that runs Flow 1. **If the user logs in with another method, show the account link prompt after login.**

### API
As sdk/user, plus: `showAccountLinkPrompt()` -> `{response: "yes"|"no"}`. The modal will get an "Always link accounts" option ("coming soon"). Errors: `showAccountLinkPromptInProgress`, `userNotAuthenticated`. The token lives 1 h and is verified with RS256 against `https://sdk.crazygames.com/publicKey.json`. Don't decrypt it on the client.

### Implementation suggestions
- **Custom DB:** add a `crazyGamesId` column. On start, send the token to the server and create or link the row. Send the token on every back-end auth and look the user up by `crazyGamesId`. **Sign the user out of your game if `getUser` returns null.** For a new arrival with an existing account, sign them in automatically.
- **Firebase:** never link on the client (anyone can inject a user ID). Use a Cloud Function: verify the token, create a link document (CG user ID to your user ID), and return a **custom Firebase token**. Later requests look up the link document.

### Unity version (https://docs.crazygames.com/sdk/user-linking/user-linking-unity/), brief
- The same warning, flows and rules: "Don't use the CrazyGames account as the **sole** identifier"; re-fetch the user at every start; always allow guests; no automatic auth prompt; the CG account takes priority; prefer fresh accounts; use the provided link modal.
- API: `IsUserAccountAvailable` (works only on CrazyGames domains, not partner or whitelisted ones), `GetUser(cb)` -> `PortalUser { username, profilePictureUrl }` or null, `SystemInfo`, `ShowAuthPrompt(cb(error, user))`, `GetUserToken(cb(error, token))`, `AddAuthListener/RemoveAuthListener(Action<PortalUser>)`, **`SyncUnityGameData()`** (saves player data manually), `ShowAccountLinkPrompt(cb(error, bool))`.
- Demo: `CrazySDK/Demo/UserModule`; editor test values live in `CrazyGamesSettings`.

---

## SDK: Leaderboards introduction

- URL: https://docs.crazygames.com/sdk/leaderboards/
- Title: Leaderboards - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

### Warnings
- **Leaderboards are only for invited games.**
- "Only one leaderboard per game is supported."
- **At least one of the Encryption Key or the API Key must be configured.**
- Recommended: submit from the server if your game has a back end, because the client cannot bypass server-side validation.

### Features
- **Weekly seasons, Monday to Monday, ending at 09:00 UTC**; scores reset automatically.
- Ranks: global, by country, among friends.
- Seasonal trophies for **1st, 2nd and 3rd**, and for the **top 1%, 5% and 10%**.
- Surfaces: the leaderboard drawer, a game-page widget, user-profile awards; plus a dedicated sidebar page, homepage carousels and widgets for games with leaderboards.

### Two ways to submit
| Approach | Source | Back end | Security | Credential |
|---|---|---|---|---|
| Client, through the SDK | game client | no | the client isn't trusted, so scores can be tampered with | Encryption Key |
| Server, through the API | your back end | yes (recommended) | validated server-side | API Key |

### Configuration
| Field | Rule |
|---|---|
| Leaderboard Guide (required, set outside the JSON) | **at most 50 characters**: the mode/level and how to score higher, e.g. "Endless Mode - Survive as long as possible", "Finish the race as fast as possible" |
| `encryptionKey` | a **32-byte base64** string, the same in every environment; can be generated in the Portal |
| `apiKey` | a 32-byte base64 string; only for API submissions |
| `scoreLabel` (metric) | `XP`, `KDA`, `POINTS`, `MINUTES` |
| `isIncremental` | true = scores add up; false = each session scores separately |
| `scoreSorting` | `"ASC"` (lower is better, e.g. time), `"DESC"` (higher is better) |
| `minValue` / `maxValue` | floats; scores outside them are rejected (e.g. 0.0 / 999999.0) |
| `cooldownSeconds` | an integer; the minimum gap between one user's submissions (e.g. 10). **SDK submissions only**, not the API |

Example: `{ encryptionKey, apiKey, scoreLabel: "POINTS", scoreSorting: "DESC", minValue: 0.0, maxValue: 500000.0, cooldownSeconds: 10, isIncremental: false }`

---

## SDK: Leaderboards SDK (client-side)

- URL: https://docs.crazygames.com/sdk/leaderboards-client/
- Title: Leaderboards SDK - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; procedure kept as shown)

### Step 1: Encrypt the score ("crucial" to make tampering harder)
**HTML5 / Construct / Cocos: `async encryptScore(score: number, encryptionKey: base64): Promise<string>`**
- AES-GCM through `window.crypto.subtle`.
- A 12-byte IV from `crypto.getRandomValues`.
- The key: `atob(encryptionKey)` gives raw bytes, imported with `importKey('raw', bytes, 'AES-GCM', false, ['encrypt'])`.
- The plaintext is `score.toString()` run through `TextEncoder`.
- The output is base64 (`btoa`) of the IV followed by the ciphertext.

Reconstruction from the description:
```js
async function encryptScore(score, encryptionKey) {
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const keyBytes = Uint8Array.from(atob(encryptionKey), c => c.charCodeAt(0));
  const key = await window.crypto.subtle.importKey("raw", keyBytes, { name: "AES-GCM" }, false, ["encrypt"]);
  const enc = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(score.toString()));
  const out = new Uint8Array(iv.length + enc.byteLength);
  out.set(iv); out.set(new Uint8Array(enc), iv.length);
  return btoa(String.fromCharCode(...out));
}
```

**Unity: `static string EncryptScore(float score, string encryptionKey)`**
- A 12-byte IV (`RandomNumberGenerator`); the key from `Convert.FromBase64String`; the plaintext `score.ToString(CultureInfo.InvariantCulture)` as UTF-8.
- A hand-rolled CTR mode on AES (`CipherMode.ECB`, `PaddingMode.None`). The counter block is the 12 IV bytes plus a 4-byte big-endian counter starting at 1.
- The output is base64 of **IV + ciphertext + a marker byte `0x55`** (the "Unity marker byte").
- The format differs from HTML5 on purpose (the marker byte); follow each engine's code exactly.

### Step 2: Submit (**pass both the encrypted and the plain score**)
```js
const encryptedScore = await encryptScore(152.1, 'your-32-byte-base64-key-here');
window.CrazyGames.SDK.user.submitScore({ encryptedScore, score: 152.1 });
```
- Unity: `CrazySDK.User.SubmitScore(encryptedScore, finalScore)`. Construct: `window.ConstructCrazySDK.user.submitScore({...})`. Cocos: `CrazySDK.user.submitScore({...})`.
- No return value or error codes are documented.

### Testing
- Use the Developer Portal preview tool (the "Leaderboard QA Tool"). Each submission logs a `submitScore` message in the logs and the browser console.
- **The server response is always "success"**: validation happens in CrazyGames' back end to stop hacking, so success does not mean the score was accepted.

---

## SDK: Leaderboards API (server-side)

- URL: https://docs.crazygames.com/sdk/leaderboard-api/
- Title: Leaderboards API - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; API shapes kept as shown)

### Endpoint
`POST https://leaderboard.crazygames.com/leaderboard/scores`
(Inconsistency: the page's full example class defaults `baseURL` to `https://userportal.crazygames.com`. The documented endpoint is `leaderboard.crazygames.com`.)

### Headers
- `X-API-Key: <game API key>` (required). The key is per game, in the Developer Portal's **Leaderboard** tab (visible only when leaderboards are enabled). **"API Key Security": keep it secret.**
- `Content-Type: application/json`

### Rate limit
**1000 requests per 60 seconds per API key.** Above that: `429 Too Many Requests` with a `Retry-After` header in seconds.

### Request
```json
{ "scores": [ { "userId": "string", "score": 1500, "timestamp": "2026-03-25T10:30:00.000Z" } ] }
```
- **At most 100 scores per request.**
- `userId` (required): from verifying and decoding the user token on your back end.
- `score` (required): a finite number.
- `timestamp` (required): ISO 8601 with date, time and timezone; **must not be in the future**; used to order rankings. Use the time the score was achieved, not the submission time.

### Response (200, or 400 with errors)
```json
{ "success": true, "total": 3, "successCount": 3, "failureCount": 0, "errors": [ { "score": {...}, "type": "user-not-found" } ] }
```
Per-score error `type`s: `no-active-season`, `user-not-found`, `privacy-disabled` (the user turned leaderboards off in privacy settings), `validation` (out of range, bad timestamp or bad format), `internal-server-error`.

### Status codes
| Status | Body | Meaning |
|---|---|---|
| 200 | standard | processed; check `errors` for per-score failures (partial success is possible) |
| 400 | `{"error":"Request body must contain a scores array"}` | no `scores` |
| 400 | `{"error":"Scores must be an array"}` | |
| 400 | `{"error":"Scores must be a non-empty array"}` | |
| 400 | `{"error":"Batch size must not exceed 100 scores"}` | |
| 400 | standard with `errors` | format or timestamp validation failed, so the **entire batch is rejected** |
| 401 | `{"error":"Unauthorized"}` | key missing, malformed or unknown |
| 429 | `{"error":"Too Many Requests"}` | wait for `Retry-After` |
| 500 | `{"error":"Internal Server Error"}` | |

- **Warning, "Validation errors abort the entire batch":** if any score fails format or timestamp validation, nothing is processed: `successCount` is 0, `failureCount` equals the total, and `errors` lists only the invalid scores. Fix them and resend the **whole** batch.
- `user-not-found`, `privacy-disabled` and `no-active-season` are per score, so partial success is possible.

### Best practices
1. Batch, splitting into chunks of 100.
2. Always check `errors`.
3. Back off exponentially on 429, honouring `Retry-After` (default 60 s in the example; `maxRetries` 3).
4. Validate against the configured min/max before sending (`Number.isFinite(s) && s >= min && s <= max`).
5. Keep the timestamp from when the score was achieved.

### Example
```bash
curl -X POST https://leaderboard.crazygames.com/leaderboard/scores \
  -H "X-API-Key: api-key-here" -H "Content-Type: application/json" \
  -d '{"scores":[{"userId":"user123","score":1500,"timestamp":"2026-03-25T10:30:00.000Z"}]}'
```
The page also has a full `CrazyGamesScoreAPI` class with `submitScores`, `submitScoresWithRetry`, `submitSingleScore`, `submitLargeBatch` and `validateScore`.

### Troubleshooting
- 401: check the key and the header.
- `user-not-found`: use the ID from the user token.
- `validation`: check min/max in the Portal and the timestamps.
- 429: batch, and back off.
- Scores missing from the board: read `errors`.

---

## Automatic Progress Save (APS)

- URL: https://docs.crazygames.com/other/aps/ (linked from requirements/account-integration; not in the sidebar)
- Title: Automatic progress save - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

### What it does
- It saves user data and syncs it across every device where the user is logged in to the same CrazyGames account (for example, start on a phone and continue on a PC).

| Storage | Typical engine | Developer action |
|---|---|---|
| `window.localStorage` | HTML5 | none; backed up and restored automatically |
| IndexedDB (Unity `PlayerPrefs` on WebGL) | Unity | none, if you save through `PlayerPrefs` |

### Restrictions
- **Not allowed for games with in-game purchases**, because automatically saving local progress is risky. Use the Data module or your own back end instead (requirements/account-integration#progress-save).
- No sizes, quotas, intervals, enabling steps or API names are given. (sdk/user: with APS, the game reloads automatically when the user logs in.)

---

## Resources: index

- URL: https://docs.crazygames.com/resources/
- Title: Introduction - CrazyGames Documentation (Resources)
- Fetched: 2026-10-23

Practical guides, troubleshooting and external references "to ship a stable game that performs well". The page itself has no rules or numbers.

| Group | Pages |
|---|---|
| General | Mouse control, CrazyGames App, Basic Launch Guide (basic-launch-metrics), Game Loading Tips (getting-to-the-first-frame) |
| Monetization | Ad Monetization Guide, Mastering Rewarded Ads, Optimizing Midgame Ads, Banner Ad Best Practices, Hypercasual & IO, Midcore/RPG & Idle, Puzzle, Action, Clicker, Word, Driving |
| HTML5 | Sitelock, Common fixes |
| Unity | Custom build, Optimization tips, Optimizer package, Common issues, Addressables guide |
| References | External resources |
Also Partners (resources/partners/).

---

## Resources: Mouse control

- URL: https://docs.crazygames.com/resources/mouse-control/
- Title: Mouse Control Tips - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

Near-quote: "Your game should avoid users accidentally leaving the game by clicking outside of the game frame." Many desktop users play outside fullscreen.

### Type 1: first-person games
- Lock the mouse in the centre of the screen during gameplay.
- Add a keyboard shortcut to unlock it (Escape, Tab). Example: Bloxd.io.

### Type 2: top-view games steered by the mouse ("we require your game to", so this is a MUST)
Examples: Agar.io, GunMaster.io, Stickman King.
- Lock the mouse and confine it to the game area.
- Show a custom pointer, or another way of showing the mouse position (a "joystick").
- Add a keyboard shortcut to unlock it (Escape, Tab).
- UI buttons shown during gameplay should be clickable, or have a keyboard shortcut shown.
- Any extra function such as drag-and-drop must be handled by the game.
- Optional: WASD and arrow keys. Examples: Little Big Fighters, GunMaster.io.

### Type 3: other games
Mostly UI clicks (clickers, bubble shooters): no confinement needed.

### Engines
- HTML5: the Pointer Lock API (MDN). No further detail.
- Unity: an example with a custom cursor `Image` clamped to the canvas `RectTransform`, `cursorSpeed = 20f`, `Cursor.lockState = CursorLockMode.Locked`, locking again on `Input.anyKeyDown`, and unlocking when `!Application.isFocused`.
  - **Warning:** "The fake cursor won't click on the Unity UI buttons, you will need to implement additional logic for that."

---

## Resources: CrazyGames App

- URL: https://docs.crazygames.com/resources/crazygames-app/
- Title: CrazyGames App - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

### Overview
- The CrazyGames apps are on the App Store (iOS) and Google Play (Android). They behave much like mobile web: auth, SDK calls, progress, ads and platform behaviour should all work as they do on the mobile site.
- Games open **fullscreen**; the app also has a **true fullscreen immersive mode** where games render edge to edge.

### Origins (for sitelock / CSP)
| Platform | Origin |
|---|---|
| iOS | **`capacitor://app.crazygames.com`** |
| Android | **`https://app.crazygames.com`** |
- The embedding page is **not** `www.crazygames.com`.
- If you sitelock with `Content-Security-Policy: frame-ancestors`, **list both origins explicitly**. Entries without a scheme only allow `https` ancestors, so **iOS gets blocked and players see a white screen**.

### Detecting the app
```js
const systemInfo = window.CrazyGames.SDK.user.systemInfo;
const isCrazyGamesApp = ["google_play_store", "apple_store"].includes(systemInfo.applicationType);
```
Unity: `CrazySDK.User.SystemInfo.applicationType == "google_play_store" || == "apple_store"`.

### Restrictions
- **Xsolla purchases are not available in the app.** Turn off Xsolla or any external payment flow there.
- **Warning:** don't show purchase buttons or payment flows that can't be completed in the app; hide or disable them.
- (sdk/banners: banners are disabled in the mobile app, `bannersDisabledMobileApp`.)

### Safe area padding
- Rounded corners, notches and dynamic islands can cover UI near the edges: buttons, menus, health bars, currencies, HUD.
- If your mobile build already supports safe areas, turn it on in the app; otherwise add padding for important UI when running in the app.
```css
.game-ui {
  padding-top: env(safe-area-inset-top, 0px);
  padding-right: env(safe-area-inset-right, 0px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
  padding-left: env(safe-area-inset-left, 0px);
}
```
- This can be combined with your own minimum padding.
- **Tip:** keep the gameplay fullscreen but move important UI into the safe area.

---

## Resources: Basic Launch Guide (metrics)

- URL: https://docs.crazygames.com/resources/basic-launch-metrics/
- Title: Basic Launch Guide - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; numbers exact)

### Process
- The first step toward launching. It measures engagement over a **7 to 21 day** test.
- It ends when **both** are true: live **7 days** and **500 plays**. If 500 plays aren't reached, it ends automatically at **21 days**.
- The Developer Dashboard (developer.crazygames.com) **refreshes daily**; **D1 retention appears a day later**.
- **You can update the game at any time, and updates are approved automatically.** Their effect shows at the next daily refresh.
- KPI tracking is automatic; **no SDK is needed**. If you integrate it, ads stay disabled.

### Metrics and benchmarks
| Metric | Definition | Benchmark |
|---|---|---|
| **Average play time** | the average time a player spends in one session | successful titles often reach **10+ minutes** |
| **Day 1 retention** | the % of players who come back the day after their first session | strong games often get **10 to 15%** |
| **Gameplay conversion** | the % of players who play **at least 1 minute** after starting the game | top titles: **80%+** conversion, load time **under 10 s**, build **under 20 MB** |

#### Tips
- **Play time:** a rewarding core loop, clear goals, new mechanics introduced gradually, a difficulty curve that is challenging but fair.
- **D1:** meaningful progression (levels, unlocks, upgrades), daily hooks (login bonuses, daily quests), **save progress** ("lost progress means lost players"), fix bugs and rough edges.
- **Conversion:** keep the build under 20 MB; load the first level first and the rest in the background (see the Unity Addressables guide); cut long intros so players are playing within seconds (see Game Loading Tips).

### Outcome
Strong KPIs lead to Full Launch, which means integrating the SDK for monetization. The KPIs are "a compass, not a final grade".

---

## Resources: Game Loading Tips (Getting to the first frame)

- URL: https://docs.crazygames.com/resources/getting-to-the-first-frame/
- Title: Getting to the First Frame: Making Web Games Load Fast and Feel Great
- Fetched: 2026-10-23 (summarised extraction)

There are no MUST/SHOULD labels; these are recommendations.

### Numbers
- CrazyGames has **over 50 million monthly players**.
- Perception thresholds: **under 100 ms** feels instant; **1 s** doesn't break flow; at **10 s** attention wanders, so give feedback or something to do while it loads.
- Bounce probability rises quickly with load time (per Google page-speed data; no figure given).
- The aim is for loading to *feel* instant, through immediate feedback.

### The CrazyGames load-size metric
- CrazyGames measures first-load time and size **up to the SDK `gameplayStart` call**, which should mark the first real gameplay, not a loading screen.
- The recommended setup: load the tutorial-critical assets first, **call `gameplayStart` as soon as the tutorial is playable**, keep loading the main game during the tutorial, and if content is still loading after the tutorial, show a loading screen before the full game.

### Load pipeline
Download (WASM, JS, textures, audio, models), then engine init (memory, shader compilation), then asset processing (decompress, parse, upload to the GPU), then startup code (Unity `Awake`/`Start`, Godot `_init`/`_ready`).

### Win 1: a smaller initial download
- Unity: **Addressables**. Split content into groups and load it async (`Addressables.LoadAssetAsync("IntroScene")`, `Addressables.Release(handle)`), optionally hosted externally.
- Godot: export sections as `.pck`, download with `HTTPRequest` to `user://`, then `ProjectSettings.load_resource_pack(...)`; use `ResourceLoader.load_interactive` polled each frame, with a progress bar.

### Win 2: a smaller build
- Unity: Brotli; ASTC textures; Vorbis audio, mono where possible; compressed models with Read/Write off; check the splash/logo settings; Build Report and Project Auditor; the CrazyGames optimizer package.
- Godot: Brotli on `.wasm`/`.js`/`.pck`, served as `.br` with `Content-Encoding: br`; an external PCK; S3TC/ETC2 textures; no debug symbols; Optimize Resources.

### Win 3: a shorter engine init
- Unity: aggressive code stripping (test it); light `Awake`/`Start`; heavy work in coroutines or async; don't overuse `Resources.Load()`.
- Godot: a custom web export template; turn off unused modules; light `_init`/`_ready`; `call_deferred()`; little logging.

### Runtime
Bottlenecks: CPU-heavy JS/WASM, transparency overdraw, physics, GC allocations, audio latency. Unity: IL2CPP, fewer per-frame allocations, profile in the browser, test low-end devices. Godot: lower physics FPS, tune vsync, profile, keep memory stable. WebGPU should improve shader compilation over time.

---

## Resources: Ad Monetization Guide

- URL: https://docs.crazygames.com/resources/ad-monetization-guide/
- Title: Ad Monetization Guide ("CrazyGames Monetization: The Guide to Maximizing Ad Revenue")
- Fetched: 2026-10-23 (summarised extraction)

No MUST/SHOULD labels. There are "Info" callouts (links to deeper guides) and "Restrictions" callouts (links to requirements/ads).

### Core metric
- **Revenue per 1000 plays.**
- **Conversion** is the % of players who play **at least 1 minute** after starting; it drives the share of plays that generate impressions. Better conversion raises revenue without adding impressions.
- Play time and impressions per play are linked: retain players longer. Too many ads cut retention and play time, and so revenue.
- Tailor monetization to the genre (7 genre guides).

### Formats
| Format | Revenue | Pros | Cons |
|---|---|---|---|
| Rewarded | **highest eCPM** | most revenue per impression; good for retention and satisfaction; opt-in | needs economy balancing; fewer impressions |
| Midgame | baseline, guaranteed impressions; steady | many impressions; easy to integrate | can frustrate players at the wrong moment |
| Banners | **lowest** revenue per impression; passive; "few games currently use them" | unobtrusive | screen space; UI work |
No eCPM or revenue-share figures are given.

### Rewarded
- Offer rewards players actually want: not too generous, not too weak.
- Examples: a **"Revive" button on the game-over screen, limited to once per session "to comply with platform frequency caps"**; "Double Coins" at the end of a level.
- By genre: action (revives, power-ups); idle/merge (time skips, offline multipliers); RPG/strategy (premium currency, gacha pulls); puzzle (hints, extra moves).

### Midgame
- At natural breaks, never during active play. The SDK caps them at **1 every 3 minutes**.
- **Request one at every natural break** (between levels, after a death, on summary screens); the SDK handles the pacing.
- Hypercasual/puzzle: between levels, but only if the levels are long enough. Shooter/IO: on the death or respawn screen, after a moment to recover.

### Banners
- Menus, shops, lobbies, level select; never during active play or over the active board.
- **Keep game buttons and joysticks well away from banners** to avoid accidental clicks.
- Puzzle, clicker, word: level select, menu, shop. Simulation: persistent planning UI. Board/card: menus and lobbies.

### Desktop vs mobile
- Desktop: large banners fit at the top or bottom; sessions are longer, so lean on rewarded ads in the economy and on midgames.
- Mobile: **a standard banner can take 10 to 15% of a landscape screen**; sessions are shorter, so consider an earlier first midgame or quick "Watch to Revive" offers.

### Adblock
Many players use adblockers; the game must still work without ads (sdk/video-ads#adblock-detection).

---

## Resources: Mastering Rewarded Ads

- URL: https://docs.crazygames.com/resources/rewarded-ads-deep-dive/
- Title: Mastering Rewarded Ads: A Deep Dive
- Fetched: 2026-10-23 (summarised extraction)

Callouts: Info, Tip, Restrictions (pointing to requirements/ads). No MUST/SHOULD labels, no named games, no uplift figures.

### Value exchange
- **Urgency and loss aversion** (the strongest motivator): "Watch to Revive" straight after a failure, **limited to once per session to stay within frequency guidelines**; "Keep your items" after a failed level.
- **Convenience:** "Skip 1 hour of waiting time", "Instantly complete this upgrade".
- **Exclusivity:** skins unlocked only through rewarded ads; a "Premium Chest" once per day.

### What top placements have in common
1. Designed in as a core feature from the start.
2. Easy to find, all through the loop (menus, level select, shop, natural breaks).
3. Impactful (double the end-of-level reward, a useful temporary booster).
4. At natural breaks (between levels, after a wave).
5. A lifeline on failure ("Respawn now", "Keep your score"), with **revives capped at once per session**.

### Economy
- Too generous and players stop playing and just watch ads; too weak and nobody clicks.
- **Tip:** scale rewards to progress, such as a % of the next upgrade's cost or a few minutes of play.
- Caps: **for example, at most 5 premium-currency ads per day**. Diminishing returns, for example **100, then 50, then 25 gems**, encourage players to come back daily.

### High-converting placements
Game over ("Watch to Revive", "Double your coins"); a "Free Daily Chest" at the top of the shop; a "Daily Ad Reward" button in the menu that lights up when ready; out of resources ("You need 50 more coins. Watch a quick ad to get them?").

### UI
- Be specific: "Watch Ad for +50 Gems", not "Watch Ad".
- Put a video-camera or play icon next to the reward icon.
- Games must still work with adblockers.

### By genre
Action and clicker games use rewarded ads heavily (top action games show more rewarded ads than the platform average despite shorter sessions). Word games show fewer ads but monetize well through retention. Puzzle games are generally the best performers overall (hints, undo).

### Optimise
A/B test reward sizes (for example, 50 vs 100 coins; if players watch just as often for 50, keep 50) and placements.

---

## Resources: Optimizing Midgame Ads (pacing and placement)

- URL: https://docs.crazygames.com/resources/midgame-ads-pacing/
- Title: Optimizing Midgame Ads: Pacing and Placement
- Fetched: 2026-10-23 (summarised extraction)

There are "Advertisement requirements" and "Restrictions" callouts (pointing to requirements/ads) and no MUST labels.

### Numbers
- Midgame ads (interstitials) often make up **40 to 60% of total earnings** in casual games.
- The SDK allows **at most 1 midgame every 3 minutes**, with extra safeguards around game start and rewarded ads. **You don't need your own cooldown timers**: request at every natural break.
- **First ad:** wait until the player has **finished the tutorial or played at least 3 to 5 minutes**, or start after **level 3 or 4**, not level 1. Hold off for the first few minutes of a player's first session (D1 retention).

### Where to put them
- Good: between levels or rounds (the most common and accepted); after a boss or milestone; before claiming a big reward (rewarded ads often fit better there); on a "Stage Clear" summary screen; on death screens (desktop and mobile).
- Bad: during active play; **right as the next level is loading**; while users are navigating menus or starting a task; in the first minutes or on level 1.
- Desktop sessions are longer, so death screens, transitions and summaries all work. On mobile, death screens and level transitions are the most natural.

### Track
Ads per active user; retention drop-off at the level where the first midgame appears; sessions ending right after an ad.

### Principle
If retention drops, **move the placement rather than requesting fewer ads**. Player experience over ad volume.

---

## Resources: Banner Ad Best Practices

- URL: https://docs.crazygames.com/resources/banner-ads-best-practices/
- Title: Banner Ad Best Practices: A Practical Developer Guide
- Fetched: 2026-10-23 (summarised extraction)

There are no MUST labels; read alongside requirements/ads#in-game-banner-ads.

- Banners give steady, passive income: less per ad than rewarded video, but consistently visible.

### Layout
- Design the UI with banners in mind from the start. Let the UI canvas resize around the banner, and put the banner in a solid, neutral container.
- **Flush against a screen edge**, never floating over gameplay or core UI.
  - Top: often better for portrait (thumbs rest at the bottom).
  - Bottom: best for landscape (health and score sit at the top).
  - Left/right on desktop: a fixed-width column (e.g. **160x600** or **300x250**) with the main UI centred.
  - No tall side banners on narrow mobile layouts.
- **Leave a 10 to 15 px gap** between the banner container and any clickable UI.
- Keep buttons, joysticks and menus well away from the banner.
- **Hide banners when active gameplay starts**; show them on menus and transitions.
- Don't show a banner right after a screen change in the spot the player was just clicking.

### Viewability
- **Banners only earn if they are on screen and active for at least 5 seconds.**
- High-dwell screens: inventory and crafting, city or base management, matchmaking lobbies and leaderboards, end-of-match summaries.

### Iterate
Test top, bottom and side placement; main menu vs level-complete screens; standard banner vs medium rectangle. Watch D1 retention and session length.

---

## Resources: Ad tips for Hypercasual & IO

- URL: https://docs.crazygames.com/resources/monetizing-hypercasual-io/
- Title: Ad Tips for Hypercasual & IO Games
- Fetched: 2026-10-23 (summarised extraction)

There are "Restrictions" callouts pointing to requirements/ads. No named games.

### Benchmarks
| Genre | Average play time | D1 retention |
|---|---|---|
| Hypercasual | **8.6 min** | **6%** |
| .io | **9 min** | **5.7%** |
These games rarely have deep economies or IAP, so revenue depends on keeping sessions going.

### Midgame
- At natural transitions: level-complete screens, death screens, the "Next Level" tap. For rounds of **30 to 45 s**, use these transitions.
- The SDK caps midgames at **1 every 3 minutes**, so don't count rounds yourself.
- "Next Level" flow: 1) show the summary and score and let the player enjoy the win; 2) **request the ad on the "Next Level" click, not on load**, so the player stays in control.

### Rewarded
- **Watch to Revive** is one of the best methods: **once per session** (not on every death) "to comply with platform frequency caps", a **5-second countdown** on the button, and **2 to 3 s of invincibility** (blinking) after respawn.
- Cosmetics: ad-gated skins, trails and hats; mystery boxes and wheel spins; "try before you buy" (one run with a locked premium character).

### Banners
Main menu or lobby, shop, level select.

### Experimental ideas borrowed from other genres
Offline progress (idle); level skips, shields or lives on hard levels (puzzle); quick gacha chests opened with an ad or coins (RPG).

---

## Resources: Ad tips for Midcore, RPG & Idle

- URL: https://docs.crazygames.com/resources/monetizing-midcore-idle/
- Title: Ad Tips For Midcore, RPG & Idle Games
- Fetched: 2026-10-23 (summarised extraction)

There are "Advertisement requirements" and "Restrictions" callouts. No named games.

### Genre metrics (CrazyGames top games)
| Genre | Play time | D1 | Ad impressions per play | Rewarded impressions |
|---|---|---|---|---|
| Strategy | **17 min** | **7.5%** | **21** | **14** |
| Adventure | **17 min** | **7.4%** | **9.8** | **4.5** |
| Simulation | **14 min** | **7.4%** | **7.9** | **3.3** |
- **Platform average D1 retention: 6.7%** (strategy's 7.5% is "12% above" it).

### Placements
- **Rewarded** (the main tool): small amounts of premium currency with a **daily cap (e.g. 5 per day)**; a free gacha pull or chest **once every few hours**; energy refills; rewards scaled to level, upgrade costs or grind speed.
- **Midgame:** "very sparingly, if at all"; only at major transitions (after a quest).
- **Banners:** menu banners instead of midgames.

### Economy
Daily caps; show the value of premium shop items; keep ad rewards scaled (100 gold matters at level 1 and is useless at level 50); avoid currency inflation; don't let ads undercut the store.

### Avoid
Forced midgames at sensitive moments (inventory checks, boss runs); flat rewards; inflation.

### Experimental ideas
Double or triple offline earnings with an ad; one-run trials of a high-level hero, weapon or vehicle; undo a move in tough battles.

---

## Resources: Ad tips for Puzzle

- URL: https://docs.crazygames.com/resources/monetizing-puzzle/
- Title: Ad Tips for Puzzle Games
- Fetched: 2026-10-23 (summarised extraction)

Callouts: "Restrictions", "Tip", "Important". No named games.

### Data
- Puzzle is **the largest category in the top 100 games by total earnings**.
- Play time **21 min** ("32% above platform average"); D1 **6.2%**; conversion **68%**; **8.9** impressions per play (rewarded **4.2**, midgame **4**, "about half" each; the page's own figures add up to 8.2).

### Banners
- On menus and pauses where the player isn't solving: the level-complete or level-select screen, and the main menu or level map (persistent). **Tip:** banners are underused passive revenue.
- Sizes: mobile **320x50**, desktop **728x90** leaderboard.
- **Leave a 15 to 20 px gap** between buttons and the ad container. (Banner Best Practices says 10 to 15 px.)

### Rewarded ("a helpful mechanic, not a paywall")
- **Hints** when stuck: a visible HUD button with a video icon, and a **1-minute cooldown** per hint so back-to-back ads can't solve the whole puzzle.
- **Extra moves / undo:** for example, **5 extra moves** when the player is one step from losing.
- **Level skips:** **no coins or stars for a skipped level**.
- **Daily challenge** unlocked with an ad.

### Midgame
- **Between levels only**, never during play. For very short levels (~**30 s**), still request at transitions; the SDK handles the pacing. **Important:** player experience over ad volume.

### Track
Hints per session (if they're low, make the button more prominent or make the first hint per level free); level churn (put "Watch to Skip" or "Free Hint" offers on the levels with the most drop-off).

### Experimental ideas
Gacha spins for themes, skins and music; passive income sped up with an ad; trying a premium power-up for one level.

---

## Resources: Ad tips for Action

- URL: https://docs.crazygames.com/resources/monetizing-action/
- Title: Ad Tips for Action Games
- Fetched: 2026-10-23 (summarised extraction)

### Data (CrazyGames top games)
- Action: about **13 min** play time; D1 **8.1%** ("21% above the platform average of 6.7%").
- Shooting: **12 min**; retention **6.5%**.

### Rewarded (high volume)
- **Revives:** once per session (the "platform frequency cap"), a **5 s countdown**, and **2 to 3 s of invincibility** with a flashing effect on spawn.
- **Pre-round trials:** a premium locked weapon or character for **one run**, in exchange for an ad.
- **Loot multipliers:** **double or triple** the end-of-match currency or items.

### Midgame
Never during active play (interrupting combat frustrates players and can lead to uninstalls).

### Banners
Lobbies, character setup, shops.

### Avoid
Ads during combat; a revive on every death; reviving into danger without invincibility.

### Experimental ideas
Offline gathering of materials, doubled with an ad; skipping a boss or level, or a shield buff; banners in gear customisation menus.

---

## Resources: Ad tips for Clicker & Incremental

- URL: https://docs.crazygames.com/resources/monetizing-clicker/
- Title: Ad Tips for Clicker & Incremental Games
- Fetched: 2026-10-23 (summarised extraction)

### Data (top clicker games)
Play time **15 min**; D1 **6.6%**; **5.5** ad impressions per play (about half rewarded, half midgame). Menu banners and rewarded ads bring steady revenue.

### Banners
Upgrade trees, shops, stat panels: places where players plan for a long time.

### Rewarded
- **Welcome-back multiplier:** show the offline earnings and offer to **double or triple** them for an ad. One of the highest-converting placements in idle games.
- **Auto-clicker boost:** for example, **2x click damage for 10 minutes**.

### Midgame
- At natural pauses: opening the shop, reaching a milestone, returning from the upgrade screen. The SDK does the pacing.
- **Show a clear 3 to 5 second warning first**, for example "Ad starting in 3...", so players stop clicking.

### Avoid
A midgame with no warning while the player is tapping; assuming the game has level breaks or death screens (clickers usually don't).

### Experimental ideas
Mystery chests with speed boosts; skipping to a milestone in prestige systems; renting an automation booster for a short time (e.g. 5 min).

---

## Resources: Ad tips for Word

- URL: https://docs.crazygames.com/resources/monetizing-word/
- Title: Ad Tips for Word Games
- Fetched: 2026-10-23 (summarised extraction)

### Data
- Average word games perform moderately; top-100 word games are among the platform's top earners.
- Top titles: **14 min** play time; D1 **7.6%** ("13% above the platform average"); **7.9** impressions per play (about **2.8** rewarded and **4.8** midgame).
- **Conversion 71%**, one of the highest. If yours is lower, **improve the game before adding ads**: load dictionaries fast and keep the first levels simple.

### Banners
On menus and between puzzles, never during play. **Tip:** level complete, main menu, daily-challenge hub.

### Rewarded
Reveal a letter or highlight a word (a lightbulb or search icon plus a small video icon); unlock a missed or extra daily challenge (to keep streaks); double the bonus-word currency.

### Midgame
Only between puzzles; never while the player is typing or dragging letters.

### Experimental ideas
Daily return bonuses doubled with an ad; a meta-game (gardens, pets) sped up with ads; **+15 s** on the timer or a brief freeze in timed modes.

---

## Resources: Ad tips for Driving

- URL: https://docs.crazygames.com/resources/monetizing-driving/
- Title: Ad Tips For Driving Games
- Fetched: 2026-10-23 (summarised extraction)

### Data
Play time **8.7 min**; D1 **5.7%**; **7** ad impressions per play (top games). Top games "often over-rely on forced midgame ads and miss out on engaging players with rewarded ads."

### Direction
Shift toward **optional rewarded ads** and smart menu placements. For some driving games, skipping forced midgames entirely in favour of rewarded ads may fit better.

### Midgame
Between races, on the post-race summary screen once the player has seen the results. "Never show an ad while a race is active."

### Rewarded (the recommended focus)
1. **Post-race multipliers:** double or triple coins or XP, tied to expensive upgrades (engine, tyres, nitro).
2. **Fuel or energy refills:** for example, when each race costs 1 fuel unit.
3. **Cosmetics:** spoilers, decals, tyre-smoke colours.
4. **Test drives:** a locked premium hypercar for **one race**.

### Banners
**Garage and customisation screens** (long dwell while reading stats).

### Experimental ideas
Passive garage income doubled with an ad; skipping a drift, time-trial or stunt challenge; **crash revive** with a shield and boost in long stunt runs, **capped at once per session**.

### Avoid
Any ad during races or high-speed action; relying too much on forced midgames; more than one crash revive per session.

---

## Resources: HTML5 Sitelock

- URL: https://docs.crazygames.com/resources/html5/sitelock/
- Title: Sitelock - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; domains and headers exact)

A sitelock helps stop an HTML5 game being copied and hosted on unauthorised sites. It is optional (requirements/technical).

### A. HTML5 games: a hostname check
```js
function isCrazyGames() {
  const hostname = window.location.hostname;
  return hostname === "crazygames.com" || hostname.endsWith(".crazygames.com");
}
```
- The game files are served from hosts like `https://cubes-2048-io.game-files.crazygames.com/cubes-2048-io/13/index.html`.
- If the check fails, show "Available only on CrazyGames" or a blank screen. Optionally obfuscate the code (obfuscator.io).

### B. Iframe games: a CSP header
`Content-Security-Policy: frame-ancestors [...]`. Iframe games are embedded from several CrazyGames origins, so **whitelist every supported domain**.

### Domains to whitelist (as written)
```
// General
*.crazygames.com

// video ads run on
games.crazygames.com

// our iOS and Android apps, mind the scheme on iOS
https://app.crazygames.com
capacitor://app.crazygames.com

//deprecated domains (no longer need whitelisting)
www.crazygames.com, de., it., vn., gr., ar., th.crazygames.com,
www.crazygames.fr, .co.id, .cz, .dk, .hu, .nl, .no, .pl, .com.br, .ro, .fi, .se, .ru, .com.ua, .at, .jp, .pt, .vn, .com.vn, .co.kr,
www.1001juegos.com, tr.crazygames.com
```

### C. Sitelock in the app
- The apps are native WebViews running a local copy of the portal, so the embedder is not `www.crazygames.com`. iOS: `capacitor://app.crazygames.com` (iOS reserves `https` for the network). Android: `https://app.crazygames.com`.
- **Warning: "A bare host in `frame-ancestors` means `https` only."** `*.crazygames.com` under an https policy allows only https ancestors, so WebKit refuses the iOS app and shows **a white screen with no JS error**; the block appears only as a CSP violation in the console.
- `frame-ancestors` is checked against **every** ancestor. In the app, the game is framed by `games.crazygames.com`, which is framed by the app, so **both must be allowed**.
- If your sitelock checks the embedder (`document.referrer`, `location.ancestorOrigins`), compare the host and don't require `https`.

```
# fails on iOS
Content-Security-Policy: frame-ancestors 'self' *.crazygames.com;
# fixed
Content-Security-Policy: frame-ancestors 'self' *.crazygames.com https://app.crazygames.com capacitor://app.crazygames.com;
```

---

## Resources: HTML5 Common fixes

- URL: https://docs.crazygames.com/resources/html5/common-fixes/
- Title: Common fixes - CrazyGames Documentation
- Fetched: 2026-10-23 (code reproduced as extracted)

One snippet fixes four common UX issues caused by default browser behaviour: unwanted page scroll, unwanted key events, visibility changes in the Samsung app, and the context menu outside the (Unity) canvas.

```js
// Disable unwanted page scroll.
window.addEventListener("wheel", (event) => event.preventDefault(), { passive: false });

// Disable unwanted key events and spacebar scrolling.
window.addEventListener("keydown", (event) => {
  if (["ArrowUp", "ArrowDown", " "].includes(event.key)) { // extraction showed "", almost certainly " " (space)
    event.preventDefault();
  }
});

// Fix visibility change handling on webview (reported on Samsung App).
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState) {
    if (document.visibilityState === "hidden") application.publishEvent("OnWebDocumentPause", "True");
    else if (document.visibilityState === "visible") application.publishEvent("OnWebDocumentPause", "False");
  }
});

// Disable context menu after right click outside the canvas.
document.addEventListener("contextmenu", (event) => event.preventDefault());
```
Notes: `application.publishEvent` assumes an engine runtime object (Construct-style) that the page doesn't define; substitute your own pause hook. The context-menu handler blocks the menu everywhere.

---

## Resources: Unity custom build (brief)

- URL: https://docs.crazygames.com/resources/unity-custom-build/
- Title: Custom CrazyGames build
- Fetched: 2026-10-23 (summarised)

- A tool in the Unity SDK (menu **CrazySDK** -> build window) that sets the web build settings (compression, exception support, data caching, code stripping, code optimisation, WebAssembly) and builds device-specific variants: **ASTC textures for mobile and DXT for desktop**.
- It needs the latest Unity SDK.
- **Development build** for local tests. **Release build** is the one for uploading: it creates several code and data builds for mobile and desktop and applies **Disk Size With LTO**. Output goes to `Builds/CrazyGamesRelease`; **upload every file in that folder**. It takes longer and the folder is bigger, but only the matching files load.
- The Analyzer lists assets and code in the build (unused but still referenced assets inflate the size); "Show help" explains each section.
- **Info:** the feature is new. If it gives you trouble, build normally and submit.

---

## Resources: Unity optimization tips (brief)

- URL: https://docs.crazygames.com/resources/optimization-tips/
- Title: Optimization tips - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised)

The page has Info, Warning and "Expected gains" boxes. Many of these are applied automatically by the custom build. Smaller builds load faster, which the page links to higher revenue; weaker devices such as Chromebooks are a stated reason for performance work.

### Size
- **Brotli** over Gzip. Code optimisation: "Runtime Speed with LTO" or "Disk Size with LTO", not "Shorter Build Time". IL2CPP: "Faster (smaller) builds" ("Optimize for code size and build time" in 6.2). Expected gain: an empty project went from **14.7 MB to 12.5 MB**.
- Raise code stripping (and test). Use ".Net Standard". Mono, lower-quality audio. Textures: sensible max sizes (2048x2048 is often too big), low-quality compression, no mipmaps for flat sprites, try Crunch.
- **Addressables:** CrazyGames **hosts them free** (Unity 2020+). Upload them with the submission (the `Build` and **`StreamingAssets`** folders, named exactly that) and build manual URLs from `Application.streamingAssetsPath`.
- URP without post-processing saves about **1 MB**. Mesh compression example: **300 KB -> 100 KB** ("High"). Remove unused packages.

### Performance
Sprite atlases; mesh LOD (6.2+); static batching (watch the memory); exceptions set to "Explicitly thrown exceptions only" (**never submit "Full With Stacktrace"**; "None" crashes on any exception); lower quality settings; **WebAssembly 2023** (Unity 6+).

### Memory and GC
GC runs every frame on WebGL. Use StringBuilder for more than 10 concatenations, cache arrays, `CompareTag`, cached `WaitForSeconds`, and preallocated buffers. Background music: **CompressedInMemory** (about 5 MB of RAM in the example). Use the Memory Profiler.

### Other
Project Auditor; the Diagnostics Overlay; **`Application.targetFrameRate = -1`** on WebGL; **test UI text at small sizes such as 900x500** (blur comes from a high Canvas Scaler reference resolution); "Name Files as Hashes"; turn off the splash screen and "Show Unity Logo" (Unity 6); enable caching.

### Advanced (Warning)
URP adds about **3.6 MB** (drop it for simple 2D); TextMeshPro adds about **0.7 MB**, or about 0.5 MB once its Resources are trimmed.

### Important
**CrazyGames ignores your `index.html` for Unity uploads** and keeps only the build files, so custom HTML or JS is lost. Games that need custom JS can be uploaded as HTML5, but they lose the Unity-specific improvements (the loading indicator, version fixes).

---

## Resources: Unity Optimizer package (brief)

- URL: https://docs.crazygames.com/resources/optimizer-package/
- Title: Unity - Optimizer package
- Fetched: 2026-10-23 (summarised)

- **Deprecated**: "deprecated in favour of custom CrazyGames builds". It is still on GitHub and bundled with the SDK.
- An open-source WebGL optimizer (C# 6.0, Unity 2019) under `Tools > WebGL Optimizer`. It has an export-settings checklist, texture tips (scenes in the build plus `Resources` and their dependencies, with an "Include files from Packages" toggle; it can miss some textures), and a build-log analyzer that parses `Editor.log` for per-file sizes.

---

## Resources: Unity common issues (brief)

- URL: https://docs.crazygames.com/resources/issues/
- Title: Unity - Common Issues
- Fetched: 2026-10-23 (summarised)

1. **Cursor locking:** locking or hiding the cursor at startup, before any interaction, can leave it not fully locked and can make scrolling crash the game. **Lock only after a user interaction**: a "click to lock" overlay, or a Play button. This applies to any engine, since browsers need a gesture for pointer lock.
2. **macOS rendering (URP):** black or flickering meshes on Mac. Turn off **Depth Priming Mode** in Universal Renderer Data.
3. **Random huge mouse deltas in WebGL:** use the `WebGLMouseInput` filter script (`diffThreshold = 100f`, `absMax = 800f`, `maxConsecutiveSpikes = 2`). A spike (|v| > absMax, or a jump > diffThreshold) reads as 0, and after 2 spikes in a row the stored previous value resets. Read the filtered input with `GetDeltaX()` / `GetDeltaY()`.

---

## Resources: Unity Addressables guide (brief)

- URL: https://docs.crazygames.com/resources/unity-addressables-guide/
- Title: Addressables guide
- Fetched: 2026-10-23 (summarised)

- Addressables take assets (audio, textures, meshes, scenes, prefabs) out of the build and load them at runtime.
- Steps: install Addressables from the Unity Registry; mark the asset "Addressable"; build (a `StreamingAssets` folder appears next to `Build`); load it through an `AssetReference` with `LoadAssetAsync<AudioClip>()` and use `handle.Result` in `Completed`; check that it loads as a separate network request. The example clip is almost 3 MB.
- **You must upload the `StreamingAssets` folder** with the build when submitting.
- **Warning:** if the asset is still referenced directly (for example, on an AudioSource), Unity keeps it in the build, and the build size doesn't drop.
- Good practice: call `ReleaseAsset()` on unused assets; load long background music after the game has loaded; make prefabs addressable (a skin shop loaded only when opened); split into groups for smaller bundles.

---

## Resources: External resources

- URL: https://docs.crazygames.com/resources/external/
- Title: External resources
- Fetched: 2026-10-23

A list of links only; no rules.
- HTML5 / PlayCanvas: "Optimizing HTML5 Games: 10 Years of Learnings" (portal.gitnation.org); "Best performance on casual games?" (YouTube PuGwC0rZD7Y); "Building Multiplayer Open-World Web Games That Run Everywhere" (Medium).
- BabylonJS: "Improving Performance in BabylonJS" (mikecann.co.uk).
- Unity: "Masterclass on Unity Web Optimization" (YouTube live DlnS53TYJO8); "Profile and optimize a Unity Web build" (unity.com/how-to/profile-optimize-web-build).

---

## Partners

- URL: https://docs.crazygames.com/resources/partners/
- Title: Partners - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction)

### Engines
HTML5, Unity, GameMaker, Construct 3, Godot and Cocos (sdk/intro anchors); GDevelop, Defold and Wonderland (external guides). Unlisted engines can usually manage at least basic integration through the HTML5 SDK.

### Xsolla (payments)
- The Xsolla PayStation.
- **In-game purchases are for invited games only, and all of them must go through the CrazyGames Xsolla account.** See sdk/in-game-purchases. No fees are listed.

### ByteBrew (analytics)
- An official partner and **free**: analytics, live ops, A/B tests, user journeys.
- Steps: 1) create an account (bytebrew.io/startnow); 2) add your game; 3) get the Web SDK (github.com/ByteBrewIO/ByteBrewUnitySDK); 4) integrate (docs.bytebrew.io/sdk/unity); 5) add custom events; 6) invite the CrazyGames data-partner account (its email is obfuscated on the page) as a Data Partner.

### Lasso (moderation)
- AI moderation of usernames, chat, images, comments and more. A **referral bonus** is available (amount not given); contact CrazyGames. lassomoderation.com

### Photon (backend)
- Multiplayer infrastructure that scales from the first users to millions. No pricing is listed.
- Resources: a Unity WebGL Asteroids sample (Quantum) and a blog post on Photon WebGL for game jams (Fusion/Quantum).

---

## FAQ & Contact

- URL: https://docs.crazygames.com/faq/
- Title: FAQ & Contact - CrazyGames Documentation
- Fetched: 2026-10-23 (answers paraphrased by the fetch tool; numbers exact)

### Part 1: Getting your game live

#### Getting started
1. **Engines:** Unity, Godot, Phaser, Construct, Pixi.js, BabylonJS, PlayCanvas, GameMaker. Games needn't be mobile-first but should work well on every device.
2. **SDK:** yes: ads, profile info, progress saving and more.
3. **Do I need the SDK?** Basic Launch: **optional**, but without it there's no monetization. Full Launch: **required** (ads, analytics, cloud saves, social and multiplayer invites); a one-time setup.
4. **Already live elsewhere?** Allowed if you hold the distribution rights.
5. **Ownership:** you keep full ownership (see the Terms & Conditions).
6. **Testing:** a preview environment in the Developer Portal ("Submit a game"). **Passing the initial QA check moves the game into Basic Launch.**
7. **Countries:** submissions are accepted from anywhere.
8. **Selection:** QA review, then Basic Launch, then Full Launch.
9. **Devices:** desktop browsers plus the mobile app; optimise for both.

#### Submitting & publishing
**What a submission needs:** a web build, SDK integration, metadata (description, instructions, thumbnails), and cover plus trailer art and video.

- **Step A, initial QA check.** The QA team plays every submission to check that it works, meets the quality bar and is fun. **Reasons a game fails:**
  - bugs or broken mechanics
  - **no English-language support**
  - **unoriginal content (clones, asset flips)**
  - inappropriate themes or content
  - not meeting the Developer Requirements, the Terms & Conditions or ethical standards
  - **not following PEGI-12**
  - **content aimed at kids**
  Reviewers give constructive feedback.
- **Step B, Basic Launch.** A soft launch to a small segment of players; only the Basic requirements apply. It keeps QA fast, gathers retention, playtime, **CTR** and gameplay conversion data, and catches issues early.
- **Step C, Full Launch.** Games that do well in Basic Launch and meet the Full requirements get **another QA review**, then worldwide exposure.

#### Updates and launch status
- **Update timing:** usually processed **within the same working day**, then visible once the cache refreshes. **Updates to games in Basic Launch go live instantly.** **An update that breaks the Terms & Conditions means immediate termination.**
- **Why ads are off in Basic Launch:** a better early experience and metrics free of ad interruptions. Ads are turned on once the game passes Basic Launch and becomes eligible for Full Launch.
- **Hosted on another portal?** CrazyGames won't iframe games from competing browser portals, only games on independent domains.
- **On your own domain?** It is iframed as a regular submission, but hosting on CrazyGames is strongly recommended. **Externally hosted games only earn revenue if the SDK is integrated correctly.**
- **Dimensions:** see the gameplay requirements.
- **Portrait and landscape:** both are supported; on desktop, portrait games use side padding (black bars or background images). You are responsible for how the game looks at every screen size.
- **Chat:** allowed, but **you must monitor it and add a profanity filter**; the SDK has a disable-chat setting.
- **CrazyGames logo:** not required, but appreciated (new brand assets promised "by September").
- **Acceptance:** you are told by email.
- **Resubmitting a rejected game:** yes, after meaningful improvements and once it meets the requirements.

#### After launch
- Traffic: the Developer Portal dashboard.
- **Player feedback:** players who leave a negative rating are asked why. It appears in the Portal, with optional email notifications.
- **Updates:** at any time; upload the files and submit for approval.
- **Rankings:** several algorithms (by device, country and OS, some personalised); new games may get an initial boost. They are driven by **play count, average playtime, retention, conversion and feedback**.
- **Homepage:** the new-games carousel shows games to millions of players a day; staying visible depends on playtime, retention and conversion.

#### Earning money
- **Eligibility for revenue:** **no branding from another game portal; SDK integrated; no external ads; original and clearly distinct from existing games.**
- **Ad provider:** CrazyGames SDK only.
- Games also on Steam, Google Play, the App Store or Facebook **remain eligible** for revenue share.
- **How much:** it varies; no figures (see the Terms & Conditions).
- **Payment:** **monthly once the balance reaches €100**; smaller balances roll over. Wire transfer or PayPal.

#### Technical
- **CDN:** yes, worldwide caching; no cache management needed.
- **Unity StreamingAssets / Addressables:** recommended; upload `Build` and `StreamingAssets` together.
- **Browsers: Chrome and Edge are required; Safari and Firefox are recommended.**
- **White screen in the iOS app:** a `frame-ancestors` sitelock with bare hosts allows https only; add the app origins.
- **Multiplayer server:** not provided; bring your own (e.g. Photon).

### Part 2: Web Games 101 (marketing Q&A)
- **50M+ monthly players**, mostly in the US, UK and other English-speaking or Tier 1 markets; from Gen Z to older players (teens lean towards .io, older players towards puzzles).
- **Zero UA cost** claimed. IAP goes through web payments and the SDK, not Apple or Google billing.
- Benefits: ads plus IAP, analytics, support and QA feedback, cloud saves, multiplayer tools, soft launch, and help scaling to mobile stores for selected titles.
- Hobbyists welcome; no-code tools (Construct, GDevelop) and AI tools are fine.
- Publishing: an HTML5 build through the portal, the SDK and metadata; reviewed for quality, performance and compliance. The SDK includes WebGL optimisations.

### Contact
- The **Developer Support form** on the developer portal. No email or Discord is listed.
- Before reporting an issue, check the browser console; if it happens in preview, include the preview link.

### Not on this page
How long the initial QA review takes; exclusivity; the revenue-share %; numeric launch thresholds.

---

## Payouts

- URL: https://docs.crazygames.com/payouts/
- Title: Payouts - CrazyGames Documentation
- Fetched: 2026-10-23 (summarised extraction; numbers exact)

### Provider and onboarding
- **Tipalti** handles the monthly payouts. Onboarding is in the Developer Portal under Account -> Billing (steps 1 to 4) and **must be finished before any payment**; finishing early is recommended.
- You can finish onboarding without payment details by choosing **"hold payments"** in step 2; self-billing invoices are still generated each month.
- Registration asks for personal or company details, address, country, tax details and payment info. Each section auto-saves on Next. Accept the suggested address format if prompted. A different payout country can be set at the bottom of the address form. **Set the payment country to "United States" to enable PayPal.** Some changes may invalidate tax or bank info you already submitted.
- Tipalti's wizard picks the right tax form for your location and entity type. CrazyGames gives no tax or legal advice. VAT isn't mentioned.

### Thresholds and schedule
- **Payout minimum: €100** in earnings, for every method.
- **Invoicing threshold: €10**; smaller amounts carry over to the next month.
- Monthly, once the unpaid earnings reach €100. **Terms are NET 60, but CrazyGames aims to pay by the 10th of the following month** ("NET 10 in practice").
- Example 1: €100 earned in January -> invoice in early February -> paid mid-February.
- Example 2: €30 in January plus €70 in February -> invoices in early February and early March -> both paid mid-March.
- Invoices appear a few business days after month-end, under Account -> Billing -> Payment & Invoice History (PDF receipts and status).

### Methods and fees
- Wire transfer, direct deposit/ACH, eCheck, PayPal (availability depends on the country). Each may have its own fees and minimums.
- **PayPal is processed in USD; choose USD to avoid FX fees.** Converting from USD or EUR into another currency incurs FX fees. Your bank deducts intermediary-bank and FX charges.
- Holding payments and then releasing them sends every held invoice in one transaction, which cuts fees.

### Reporting and issues
- To estimate, use the Portal's reporting view set to Previous Month. **The self-billing invoice amount is authoritative**; small timezone or cut-off differences are normal.
- "In process" for a long time usually means missing or invalid info. For rejected payments, read the notes under Billing -> History and fix the details; it retries next cycle. For locked billing info, contact support.
- **No revenue-share percentage is stated** here (nor anywhere else in the docs; see the Terms & Conditions).

---

## Pre-submission checklist and contradictions

Page keys: intro = /, req-intro = requirements/intro, tech = requirements/technical, gameplay = requirements/gameplay, ads = requirements/ads, account = requirements/account-integration, mp = requirements/multiplayer, covers = requirements/game-covers, quality = requirements/quality, sdk-intro, sdk-ads = sdk/video-ads, sdk-banners, sdk-game, sdk-user, sdk-data, sdk-iap = sdk/in-game-purchases, lb = sdk/leaderboards*, linking = sdk/user-linking, aps = other/aps, app = resources/crazygames-app, sitelock = resources/html5/sitelock, fixes = resources/html5/common-fixes, mouse = resources/mouse-control, blm = resources/basic-launch-metrics, loading = resources/getting-to-the-first-frame, mon-* = the monetization guides, unity-* = the Unity resources, faq, payouts.

**Tier:** [B] means it applies to Basic Launch (and so to Full Launch too); [F] means Full Launch only; [G] means a guideline or recommendation.

### Process (how review works)
- [ ] Test in the Developer Portal **Preview tool** before submitting (intro, sdk-intro, faq).
- [ ] Understand the flow: **QA review, then Basic Launch** (7 to 21 days; it ends at 7 days AND 500 plays, or automatically at 21 days; ads off), **then Full Launch** (a second, full QA review; monetization on) (intro, blm, faq).
- [ ] Basic Launch is judged on **average playtime, gameplay conversion (% who play at least 1 min) and D1 retention** against platform benchmarks. Benchmarks: playtime **10+ min**, D1 **10 to 15%**, conversion **80%+**, load **under 10 s**, build **under 20 MB** (blm). Platform average D1 is **6.7%** (mon-midcore, mon-action).
- [ ] Outcomes: all metrics good, so integrate the Full SDK and resubmit for Full Launch; some good, so you may be offered another Basic Launch; most bad, so you can only **resubmit as a new game with significant improvements** (intro).
- [ ] Multiplayer games needing a big audience, and invited games already published elsewhere, may skip Basic Launch (intro, mp).
- [ ] Updates: you can update during Basic Launch (approved automatically and live at once); otherwise they are processed the same working day. **An update that breaks the T&Cs means immediate termination** (blm, faq).
- [ ] **Repeatedly submitting non-compliant games can get you restricted from future submissions** (gameplay).
- [ ] Submission metadata: a description, **controls/instructions**, covers, preview videos, supported orientations, a lobby size (multiplayer), and the **Progress Save option** set correctly (req-intro, tech, mp, sdk-data, faq).

### Technical
- [ ] [B] Initial download **<= 50 MB** (measured up to the first `gameplayStart`; without the SDK, the total size counts) (tech, req-intro).
- [ ] [B] Total size **<= 250 MB** (50 MB without the SDK); **<= 1,500 files** (tech, req-intro).
- [ ] [G] **<= 20 MB** initial download to be eligible for the **mobile homepage** (tech); under 20 MB is the top-title benchmark too (blm).
- [ ] [B] Externally hosted or loaded files: **<= 20 s to reach gameplay** (tech).
- [ ] [B] **Relative paths only**; absolute paths fail (tech).
- [ ] [B] Works in **Chrome and Edge** (required); Safari and Firefox recommended, and a game that runs badly on Safari is disabled there (tech, faq).
- [ ] [B] Runs smoothly on a **4 GB RAM Chromebook**, or it is disabled on ChromeOS (tech).
- [ ] [B] Mouse and keyboard supported; touch too if the game supports mobile (tech).
- [ ] [B] **Playable in landscape on desktop**; portrait is allowed with side bars or a background (tech, faq).
- [ ] [G] `user-select: none` (and the vendor prefixes) on `body` for tablets (tech).
- [ ] [G] Resume a `suspended` AudioContext in a `touchend`/`click` handler (iOS) (tech).
- [ ] [G] Block page scroll on wheel, arrow and space keys, and the context menu (fixes).
- [ ] [B] Unity: Brotli or Gzip only (dev builds won't run); never submit "Full With Stacktrace" exceptions; `index.html` and custom JS are ignored for Unity uploads; upload `Build` plus `StreamingAssets`; Unity on iOS is off by default; DPR is 1 on iOS and low-memory Android (sdk-intro, unity-*, tech, faq).
- [ ] [B] If you sitelock, whitelist `*.crazygames.com`, `games.crazygames.com`, `https://app.crazygames.com` **and `capacitor://app.crazygames.com`** (or iOS shows a white screen) (tech, sitelock, app).
- [ ] [B] If you collect personal data beyond SDK events, show new players a simple **Privacy Policy / T&C notice** (not a blocking popup) (tech, req-intro).
- [ ] [G] App: put important UI inside `env(safe-area-inset-*)` when `applicationType` is `google_play_store` or `apple_store` (app).
- [ ] [G] Mouse-steered top-down games: lock or confine the pointer, show a custom cursor, offer an unlock key (Esc/Tab). First-person games: lock in the centre. Lock only after a user gesture ("we require", mouse; unity-issues).

### Gameplay
- [ ] [B] Text and images legible at **DPR 1** and at the 16:9 iframe sizes **907x510, 1216x684, 1077x606, 821x462** (desktop windowed), **1366x768, 1920x1080, 1536x864, 1280x720** (fullscreen), **800x450** (mobile) and **1080x607** (tablet) (gameplay). Unity: test UI at about **900x500** (unity-opt).
- [ ] [B] Physics consistent at **144 Hz and 165 Hz** (gameplay).
- [ ] [B] **English localisation required**; other translations must be accurate; use the SDK `systemInfo.locale`, falling back to English (gameplay, sdk-user, faq).
- [ ] [B] Intuitive controls on every device; loads fast; **no errors or crashes** (gameplay).
- [ ] [B] **Original** name, assets and content; no clones or asset flips (gameplay, faq, quality).
- [ ] [B] **No custom fullscreen button** (CrazyGames provides fullscreen) (gameplay).
- [ ] [B] **No cross-promotion.** Allowed: privacy/T&C links; Discord or developer-site links on the menu only (never to a playable web version); Steam/Epic links only on the main menu or at the end of a demo; CrazyGames backlinks; other games in the same series; none of them the main call to action. **Never App Store links** (gameplay).
- [ ] [B] **PEGI 12**, audience 13+; not aimed at kids; no inappropriate themes (gameplay, faq).
- [ ] [B] No branding from another game portal (faq; also a revenue condition).
- [ ] [F] **Land new users straight in gameplay, with at most 1 click before play** (gameplay, req-intro).

### Ads
- [ ] [B] **No external ads**, ever; only ads through the CrazyGames SDK (req-intro, ads, faq).
- [ ] [B] If the ad SDK is integrated in Basic Launch, the game must **run smoothly with ads disabled** (`adsDisabledBasicLaunch` / `adError`): no freeze between levels, **no rewarded buttons that do nothing** (ads, sdk-ads).
- [ ] [F] Midgames only at natural breaks (level end, death/respawn, summaries); **never during gameplay; never on navigation buttons** (main menu, settings, shop) (ads).
- [ ] [F] **Pause and mute on `adStarted`; resume and unmute on `adFinished` or `adError`**; block the UI with a spinner while the ad is requested (ads, sdk-ads).
- [ ] [F] Handle `adError` (`unfilled`, `adblock`, `adCooldown`, `other`) and carry on; the SDK enforces **1 midgame per 3 minutes**, so request at every natural break without timers of your own (ads, sdk-ads, mon-midgame).
- [ ] [F] Rewarded: optional, never needed to finish a level, no chaining, not on an active gameplay screen, a video icon, a "no thanks" option **of the same size, font and colour**, skip/close never hidden or delayed, an alternative (coins), **reward only on `adFinished` and never on `adError`** (ads).
- [ ] [F] **No out-of-lives rewarded offer on every death**; use a timer if it's frequent. Guides say revive **once per session** (ads, mon-*).
- [ ] [F] Between levels use **either** a midgame **or** "watch to keep playing", not both (ads).
- [ ] [F] Banners: only on screens open **5 s or more on average**, never during gameplay, never covering UI at any size, clearly ads, **at most 2 per screen**; refresh **at least 30 s apart** per container, **120 refreshes per session per size**, fully inside the game window and visible; clear them after hiding (ads, sdk-banners).
- [ ] [F] **Works with AdBlock:** the game is fully playable; you may lock extras (skins, some levels) with a non-popup notice; rewarded buttons must not be clickable with no effect (ads, sdk-ads).
- [ ] [G] First midgame after the tutorial, or 3 to 5 minutes, or level 3 to 4; give a 3 to 5 s "Ad starting in 3..." warning in clicker games; keep a 10 to 20 px gap between banners and buttons (mon-*).

### Account
- [ ] [B] **No external login options** (Facebook, Google, email) in Basic Launch; guests and registered users play as guests (account, req-intro).
- [ ] [F] If the game has users: show the **CrazyGames username and avatar**; **auto-register and auto-login** CrazyGames users; guests can play; **no in-game logout and no external login** (account).
- [ ] [F] **Request the user on every game start**; never trigger the auth prompt automatically; a "Login with CrazyGames" button is allowed but not the main call to action (top-right suggested) and must call `showAuthPrompt` (account, linking).
- [ ] [F] Identify users by the server-verified `userId` from `getUserToken()` (RS256, `publicKey.json`), **never by `__dangerousUserId` or `username`**; don't store the token (it lasts 1 h) (account, sdk-user).
- [ ] [F] **Progress save required** (unless it doesn't apply): the Data module (preferred), your own back end plus the User module, or **APS (not allowed with IAP)**; progress syncs across devices (account, sdk-data, aps).
- [ ] [F] Listen for logins with `addAuthListener` (logout reloads the page); use `showAccountLinkPrompt` for linking, never a custom modal (sdk-user, account).

### Covers & metadata
- [ ] [B] **3 covers:** landscape **1920x1080 (16:9)**, portrait **800x1200 (2:3)**, square **800x800 (1:1)**, with consistent visuals (covers).
- [ ] [B] Covers: no borders, **no text but the title** (no "New" or "Play now"), no icons or store logos, no copyrighted art you lack rights to, nothing blurry or pixelated (covers).
- [ ] [G] Covers: not a raw screenshot; simple; the game name in a stylised font (covers).
- [ ] [B] **2 preview videos:** landscape **1080p 16:9** and portrait **1080p 2:3**, **15 to 20 s** (cut at 20 s), **<= 50 MB**, **no sound, no fast-forward**, **open on the static cover**; no black intro or logo, no letterbox bars, no default cursor, no "Play Now" or promo text, no app or social icons; animation only if it represents the gameplay (covers).
- [ ] [G] The name and imagery reflect the real gameplay; don't change the genre after submission (quality).

### Quality (guidelines)
- [ ] [G] Onboarding inside gameplay, skippable, visual, showing the controls (keyboard overlay) (quality).
- [ ] [G] Buttons clearly labelled, not sized to push ads, with no confusing delays (quality).
- [ ] [G] Key bindings adapt to the keyboard layout (AZERTY gives ZQSD); avoid **Esc** (it exits fullscreen) and **Ctrl/Cmd+W** (quality).
- [ ] [G] High-resolution, consistent art and style; balanced audio; quick response; no grind; solo play as prominent as multiplayer (quality).

### Multiplayer (if applicable)
- [ ] [F] `updateRoom({ roomId, isJoinable, inviteParams })` / `leftRoom()`; joinable right after launch; handle `isInstantMultiplayer` (a new private room straight away, an optional config screen, and 20+ player games may go public); check `inviteParams` at start; `addJoinRoomListener`; next round with the same group (mp, sdk-game).
- [ ] [F] Show the CrazyGames usernames; declare the lobby size at upload (mp).
- [ ] [B] Chat: honour `settings.disableChat`; **moderation required** (at least a profanity filter); UGC moderation required; bring your own server (mp, sdk-game, faq).
- [ ] [G] Spectator join mid-round; Get friends (`listFriends`) (mp, sdk-user).

### In-game purchases (invite only)
- [ ] [F] Xsolla via the CrazyGames Xsolla account; signed-in users only; orders carry the CrazyGames `userId`; a working close button; tell players to allow popups if PayStation opens a new tab; hide "Back to the game" ("Manual redirect condition" = None); never charge without crediting (webhooks or inventory); **turn sandbox off before submitting**; **hide purchases in the CrazyGames App**; lootbox country rules (BE, CN, NL, RS, SK restricted; TW and KR need odds disclosed; JP conditions) (sdk-iap, partners, app).

### SDK
- [ ] [B] Load `https://sdk.crazygames.com/crazygames-sdk-v3.js` in `<head>` and **`await CrazyGames.SDK.init()`** before any call (during loading) (sdk-intro, sdk-data).
- [ ] [B] Check `SDK.environment` (`local` / `crazygames` / `disabled`); every call throws when `disabled` (sdk-intro).
- [ ] [B] Fire **`gameplayStart` at the first playable moment** (it measures the initial download) (tech, sdk-game, loading).
- [ ] [F] `gameplayStart` on every start, resume, revive or next level; **`gameplayStop` at every break** (menus, level end, pause); not on focus loss (sdk-game).
- [ ] [F] **`settings.muteAudio` overrides the in-game audio toggles**, plus `addSettingsChangeListener` (sdk-game).
- [ ] [G] `loadingStart`/`loadingStop` (optional); `happytime()` sparingly (not for routine events); `reportGameCompletedPercentage` (at least 100 at completion); `setGameContext`/`clearGameContext` for feedback (sdk-game, tech).
- [ ] [F] Data module: read before you write; at most **1 MB** of JSON (`dataLimitExcedeed`); saves debounced 1 to 30 s; migrate old localStorage/PlayerPrefs keys; choose "Yes, using the Data Module" at submission, or `dataModuleDisabled` (sdk-data).
- [ ] [F] Leaderboards (invite only): one per game; encrypted `submitScore({encryptedScore, score})`; or the server API with `X-API-Key`, at most 100 scores per batch, 1000 requests per 60 s, timestamps never in the future (lb).

### Contradictions and inconsistencies between pages
1. **Which SDKs support everything.** req-intro says HTML5 and Unity; sdk-intro says HTML5, Unity **and Godot**. Yet the Godot tabs lack room data, invite links, listFriends, game context, completion % and responsive banners.
2. **Is the SDK needed to submit?** The FAQ lists "SDK integration" among the submission requirements; intro, req-intro, tech, blm and the FAQ's own "Do I need the SDK?" answer say it is **optional for Basic Launch**.
3. **External logins.** account says to turn off external login (Basic) and that external login is **not allowed** (Full); sdk/user-linking describes keeping Google/Facebook sign-in alongside CrazyGames and offering "other providers" on the launch screen. The safe reading is that linking is an advanced, case-by-case path, and the requirement page wins at review.
4. **The CrazyGames account as identifier.** account says the `userId` "must be usable as an in-game identifier" and to link on `userId`; user-linking says "Don't use the CrazyGames account as the identifier" (Unity: "sole identifier") and to keep a mapping. They reconcile as: key a mapping table on the verified `userId`.
5. **How often to offer a revive.** ads only forbids an out-of-lives offer "each time the users lose a life" (and suggests a timer); the ad monetization, rewarded, hypercasual, action and driving guides all say **once per session "to comply with platform frequency caps"**. Once per session is the conservative rule.
6. **Midgame at next-level load.** The ad monetization guide lists "Loading the next level" as a natural break; the midgame pacing guide says **don't request ads right as the next level is loading**; the hypercasual guide says request on the "Next Level" click, not on load. ads also bans midgames on navigation buttons (menu, settings, shop), so "Next Level" sits in a grey zone that the guides allow.
7. **Timing of the first midgame.** The SDK already "accounts for game start" (ads); the pacing guide says wait for the tutorial, or 3 to 5 minutes, or level 3 to 4; the ad monetization guide says that on mobile you might bring the first midgame "slightly earlier".
8. **Gap between banners and buttons.** 10 to 15 px (banner best practices) vs 15 to 20 px (puzzle guide).
9. **Banner count.** ads says at most 2 per screen; sdk-banners states no limit.
10. **Ad pausing.** sdk-ads Info says the game "is paused automatically when an ad is requested"; its own Warning (and ads) says you must pause and mute on `adStarted`. In context the automatic pause applies to engine wrappers (Unity), so HTML5 games must pause themselves.
11. **muteAudio and Unity.** sdk-game says a Full Implementation needs `muteAudio` for HTML5, **Unity**, Cocos and Construct; the same page's Info says games submitted as Unity have audio muting handled automatically.
12. **Feedback on rejection.** sdk-ads and sdk-banners say games that break the ad requirements are "**rejected without feedback**"; the FAQ says reviewers give constructive feedback.
13. **Resubmission.** The FAQ says a rejected game can be resubmitted after meaningful improvements; intro says a game whose Basic Launch metrics are mostly below benchmark must come back **as a new game**. These are probably two different cases: a QA rejection versus a failed Basic Launch.
14. **Kids content.** gameplay mentions a kids site (kids.crazygames.com, no monetization); the FAQ lists "content targeted at kids" as a reason to fail. The main site is 13+.
15. **Update approval.** blm says Basic Launch updates are approved automatically; the FAQ says updates go live "within the same working day" and that you "submit for approval", but Basic Launch updates go live instantly. This is consistent once you split Basic and Full; the docs just don't say so plainly.
16. **Room field name.** mp says `room`; sdk-game says `roomId`. Use `roomId`.
17. **Friends method name.** mp says "Get friends"; sdk-user names it `listFriends({page, size})`.
18. **Leaderboard API host.** The documented endpoint is `leaderboard.crazygames.com`; the example class defaults to `userportal.crazygames.com`.
19. **Puzzle numbers.** "8.9 impressions per play" against a 4.2 + 4 = 8.2 split (mon-puzzle).
20. **Safari.** tech says games that run badly on Safari are disabled there (a de-facto expectation); the FAQ says Safari is only "recommended". It's not a rejection reason, but it costs reach.
21. **The error code spelling `dataLimitExcedeed`** (sdk-data) is a typo; match it literally.
22. **Revenue share is never stated** on any docs page (intro, faq, payouts); it is deferred to the Terms & Conditions.
