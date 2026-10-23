<!-- Read from docs.crazygames.com on 2026-10-23 (48 pages). Numbers and API names were requested exactly but are near-verbatim extractions: re-check a page before relying on a number that decides a build. -->
# Pre-submission checklist and contradictions

Page keys: intro = /, req-intro = requirements/intro, tech = requirements/technical, gameplay = requirements/gameplay, ads = requirements/ads, account = requirements/account-integration, mp = requirements/multiplayer, covers = requirements/game-covers, quality = requirements/quality, sdk-intro, sdk-ads = sdk/video-ads, sdk-banners, sdk-game, sdk-user, sdk-data, sdk-iap = sdk/in-game-purchases, lb = sdk/leaderboards*, linking = sdk/user-linking, aps = other/aps, app = resources/crazygames-app, sitelock = resources/html5/sitelock, fixes = resources/html5/common-fixes, mouse = resources/mouse-control, blm = resources/basic-launch-metrics, loading = resources/getting-to-the-first-frame, mon-* = the monetization guides, unity-* = the Unity resources, faq, payouts.

**Tier:** [B] means it applies to Basic Launch (and so to Full Launch too); [F] means Full Launch only; [G] means a guideline or recommendation.

## Process (how review works)
- [ ] Test in the Developer Portal **Preview tool** before submitting (intro, sdk-intro, faq).
- [ ] Understand the flow: **QA review, then Basic Launch** (7 to 21 days; it ends at 7 days AND 500 plays, or automatically at 21 days; ads off), **then Full Launch** (a second, full QA review; monetization on) (intro, blm, faq).
- [ ] Basic Launch is judged on **average playtime, gameplay conversion (% who play at least 1 min) and D1 retention** against platform benchmarks. Benchmarks: playtime **10+ min**, D1 **10 to 15%**, conversion **80%+**, load **under 10 s**, build **under 20 MB** (blm). Platform average D1 is **6.7%** (mon-midcore, mon-action).
- [ ] Outcomes: all metrics good, so integrate the Full SDK and resubmit for Full Launch; some good, so you may be offered another Basic Launch; most bad, so you can only **resubmit as a new game with significant improvements** (intro).
- [ ] Multiplayer games needing a big audience, and invited games already published elsewhere, may skip Basic Launch (intro, mp).
- [ ] Updates: you can update during Basic Launch (approved automatically and live at once); otherwise they are processed the same working day. **An update that breaks the T&Cs means immediate termination** (blm, faq).
- [ ] **Repeatedly submitting non-compliant games can get you restricted from future submissions** (gameplay).
- [ ] Submission metadata: a description, **controls/instructions**, covers, preview videos, supported orientations, a lobby size (multiplayer), and the **Progress Save option** set correctly (req-intro, tech, mp, sdk-data, faq).

## Technical
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

## Gameplay
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

## Ads
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

## Account
- [ ] [B] **No external login options** (Facebook, Google, email) in Basic Launch; guests and registered users play as guests (account, req-intro).
- [ ] [F] If the game has users: show the **CrazyGames username and avatar**; **auto-register and auto-login** CrazyGames users; guests can play; **no in-game logout and no external login** (account).
- [ ] [F] **Request the user on every game start**; never trigger the auth prompt automatically; a "Login with CrazyGames" button is allowed but not the main call to action (top-right suggested) and must call `showAuthPrompt` (account, linking).
- [ ] [F] Identify users by the server-verified `userId` from `getUserToken()` (RS256, `publicKey.json`), **never by `__dangerousUserId` or `username`**; don't store the token (it lasts 1 h) (account, sdk-user).
- [ ] [F] **Progress save required** (unless it doesn't apply): the Data module (preferred), your own back end plus the User module, or **APS (not allowed with IAP)**; progress syncs across devices (account, sdk-data, aps).
- [ ] [F] Listen for logins with `addAuthListener` (logout reloads the page); use `showAccountLinkPrompt` for linking, never a custom modal (sdk-user, account).

## Covers & metadata
- [ ] [B] **3 covers:** landscape **1920x1080 (16:9)**, portrait **800x1200 (2:3)**, square **800x800 (1:1)**, with consistent visuals (covers).
- [ ] [B] Covers: no borders, **no text but the title** (no "New" or "Play now"), no icons or store logos, no copyrighted art you lack rights to, nothing blurry or pixelated (covers).
- [ ] [G] Covers: not a raw screenshot; simple; the game name in a stylised font (covers).
- [ ] [B] **2 preview videos:** landscape **1080p 16:9** and portrait **1080p 2:3**, **15 to 20 s** (cut at 20 s), **<= 50 MB**, **no sound, no fast-forward**, **open on the static cover**; no black intro or logo, no letterbox bars, no default cursor, no "Play Now" or promo text, no app or social icons; animation only if it represents the gameplay (covers).
- [ ] [G] The name and imagery reflect the real gameplay; don't change the genre after submission (quality).

## Quality (guidelines)
- [ ] [G] Onboarding inside gameplay, skippable, visual, showing the controls (keyboard overlay) (quality).
- [ ] [G] Buttons clearly labelled, not sized to push ads, with no confusing delays (quality).
- [ ] [G] Key bindings adapt to the keyboard layout (AZERTY gives ZQSD); avoid **Esc** (it exits fullscreen) and **Ctrl/Cmd+W** (quality).
- [ ] [G] High-resolution, consistent art and style; balanced audio; quick response; no grind; solo play as prominent as multiplayer (quality).

## Multiplayer (if applicable)
- [ ] [F] `updateRoom({ roomId, isJoinable, inviteParams })` / `leftRoom()`; joinable right after launch; handle `isInstantMultiplayer` (a new private room straight away, an optional config screen, and 20+ player games may go public); check `inviteParams` at start; `addJoinRoomListener`; next round with the same group (mp, sdk-game).
- [ ] [F] Show the CrazyGames usernames; declare the lobby size at upload (mp).
- [ ] [B] Chat: honour `settings.disableChat`; **moderation required** (at least a profanity filter); UGC moderation required; bring your own server (mp, sdk-game, faq).
- [ ] [G] Spectator join mid-round; Get friends (`listFriends`) (mp, sdk-user).

## In-game purchases (invite only)
- [ ] [F] Xsolla via the CrazyGames Xsolla account; signed-in users only; orders carry the CrazyGames `userId`; a working close button; tell players to allow popups if PayStation opens a new tab; hide "Back to the game" ("Manual redirect condition" = None); never charge without crediting (webhooks or inventory); **turn sandbox off before submitting**; **hide purchases in the CrazyGames App**; lootbox country rules (BE, CN, NL, RS, SK restricted; TW and KR need odds disclosed; JP conditions) (sdk-iap, partners, app).

## SDK
- [ ] [B] Load `https://sdk.crazygames.com/crazygames-sdk-v3.js` in `<head>` and **`await CrazyGames.SDK.init()`** before any call (during loading) (sdk-intro, sdk-data).
- [ ] [B] Check `SDK.environment` (`local` / `crazygames` / `disabled`); every call throws when `disabled` (sdk-intro).
- [ ] [B] Fire **`gameplayStart` at the first playable moment** (it measures the initial download) (tech, sdk-game, loading).
- [ ] [F] `gameplayStart` on every start, resume, revive or next level; **`gameplayStop` at every break** (menus, level end, pause); not on focus loss (sdk-game).
- [ ] [F] **`settings.muteAudio` overrides the in-game audio toggles**, plus `addSettingsChangeListener` (sdk-game).
- [ ] [G] `loadingStart`/`loadingStop` (optional); `happytime()` sparingly (not for routine events); `reportGameCompletedPercentage` (at least 100 at completion); `setGameContext`/`clearGameContext` for feedback (sdk-game, tech).
- [ ] [F] Data module: read before you write; at most **1 MB** of JSON (`dataLimitExcedeed`); saves debounced 1 to 30 s; migrate old localStorage/PlayerPrefs keys; choose "Yes, using the Data Module" at submission, or `dataModuleDisabled` (sdk-data).
- [ ] [F] Leaderboards (invite only): one per game; encrypted `submitScore({encryptedScore, score})`; or the server API with `X-API-Key`, at most 100 scores per batch, 1000 requests per 60 s, timestamps never in the future (lb).

## Contradictions and inconsistencies between pages
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
