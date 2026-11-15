---
name: reward-systems
description: Use when designing or reviewing a game's progression, economy or reward cadence - XP and levels, currencies, unlocks, chests, crates, loot boxes, drops, gacha, pity, daily login or playtime rewards, missions, streaks, battle or season passes, spins, rewarded-ad offers - especially for a game whose audience includes teenagers or is rated PEGI 12 or lower.
---

# Reward systems

The big games all moved the same way between 2019 and 2025. Progression became fixed and visible,
and randomness survived only as a small, free, bounded layer on top. Build that structure from the
start:

- **The spine:** progress the player can always see and always earns.
- **The random layer:** optional, earned by play, with published odds and a guarantee.
- **Money and ads:** they buy fixed things, never chances.

The evidence and sources are in `reports/Multiplayer reward systems teardown.md` (in the `profit`
research folder). The rules below come from it.

## What the evidence says

- **The commercial claim for random rewards is unproven.** No game-specific study shows variable
  rewards keep players better than fixed ones. The best natural experiment is Brawl Stars in
  December 2022: removing all randomness held daily players flat and cut revenue about 14%. Free
  random drops came back as the game recovered, but other features shipped at the same time, so the
  cause is unclear.
- **Effects that do replicate:**
  - a progress bar that is nearly full pulls players to finish it (goal gradient);
  - a bar that starts partly filled gets completed more often (endowed progress);
  - players like some variability as long as the range stays bounded.
- **Hidden odds roughly double what players will pay.** Being transparent costs spending, not
  retention.
- **Where pity values are published** (Hearthstone, Overwatch 2, Genshin), the guaranteed drop
  arrives at or before twice the expected wait.

## The rules

| Mechanic | Status (PEGI 12 target, 2026 rules) |
|---|---|
| XP levels from every match, win or lose; mastery tracks; a free season track whose tiers stay earnable after the season; missions that pile up instead of expiring | **Allowed.** Rewarding a return is PEGI 7. |
| Free, earned crates with odds shown in the game, a visible pity counter and duplicate protection | **Allowed** |
| Fixed-price cosmetics bought with earned currency | **Allowed** |
| A premium pass or direct cosmetics for real money: fixed and previewed contents, real-money price shown, missed tiers still earnable later | **Allowed later.** On CrazyGames, in-game purchases are invite-only. |
| Rewarded ad for a fixed, capped bonus (double XP for one match, a stated amount of currency), with a non-ad path to the same reward | **Allowed** |
| A daily bonus that just refreshes, such as first win of the day, where missing a day loses nothing the player already has | **Allowed.** It rewards a return without punishing absence. |
| Daily rewards that expire, or streaks that wipe progress | **Risky:** exactly PEGI 12, no margin. Pause instead of resetting. |
| Time-limited or quantity-limited offers (weekday deals, one-per-account packs, seasonal items that never return) | **Risky:** exactly PEGI 12 |
| A rewarded ad that buys a spin, a crate or a re-roll | **Risky and untested.** No regulator has ruled on whether an ad view counts as payment. Don't ship it without legal advice. |
| Crates, keys or spins bought with money or with currency that can be bought | **Ruled out.** PEGI 16 by default since June 2026; the FTC acted on loot boxes sold to under-16s. |
| Player trading, or any market that converts to cash | **Ruled out.** It is the "thing of value" behind gambling claims (New York v. Valve). |
| Paid power: upgrades to max level, stat gear for sale | **Ruled out** in competitive games |
| Slot, wheel, roulette or casino imagery, even when free | **Ruled out.** It can push the rating to 18. Open a chest instead. |
| NFTs or blockchain items | **Ruled out** (PEGI 18) |

## A reference design

These are starting numbers. Tune them against the platform's measured targets.

- **Account level.**
  - XP comes from every match.
  - The first bar starts partly filled, with a stated reason such as "welcome bonus".
- **Mastery.** Each weapon or character has fixed tiers that unlock cosmetics or sidegrades, never
  stronger stats.
- **Season track.**
  - About 30 free tiers whose rewards never expire.
  - Tiers stay earnable after the season ends.
- **Missions.**
  - Daily and weekly missions pile up unclaimed.
  - The streak counts one run a day, earns freezes, and shows the longest streak.
- **Supply crate.**
  - One crate per two wins, capped at three a day.
  - Odds are shown, for example Rare 75%, Epic 20%, Legendary 5%, with Rare or better guaranteed.
  - Pity is a visible counter: an Epic within 5 crates, a Legendary within 20.
  - Unowned items come first. A duplicate converts to a stated amount of currency.
  - Opening is a chest, never a reel.
- **Rewarded ads.**
  - Fixed, capped bonuses only.
  - Ads never chain.
  - Never shown during play.
  - Every reward also has a path that needs no ad.

## Check a design

1. **Mark every random element.** For each one, answer:
   - Is it free and earned?
   - Are its odds shown in the game?
   - Is there a visible guarantee at or before twice the expected wait?
   - Is there duplicate protection?

   A "no" to any of these means fix it.
2. **Trace every path where money or ads come in.** Each must end in something fixed.
3. **Find every timer, expiry and limited offer.** Each one moves the rating up to exactly PEGI 12.
   Remove it, or decide to keep it knowingly.
4. **Check that nothing for sale changes how a match turns out.**
5. **Test the economy with the simulation, the way an economy test does.** Show when each reward
   unlocks for a casual player and for a heavy player. Check that the free path reaches the season's
   cosmetics.

## Common mistakes

- **Random rewards for watching an ad:** a free daily spin, a crate per ad. Grant a fixed bonus
  instead.
- **Selling the currency that buys chances.** That makes the chances paid.
- **Pity hidden from the player, or far beyond the expected wait.** Show it, and set it at or under
  twice the wait.
- **Wheels and near-miss animations.** They are casino idioms, and a rating board reads them as
  gambling.
- **Pressure on daily rewards:** "Come back or lose your streak." Pause the streak instead.
- **Trusting what competitors get away with.** Older games were rated under older criteria. A new
  submission is judged under the current ones.
- **A pick with an obvious answer.** Two upgrade cards on one screen did the same thing at 20% and
  30%, and a playtester said "obviously im going to choose the 30 percent". Never offer two
  options that change the same thing, and prefer options that change how the player plays over
  ones that only change a number by how much.

## Related skills

- `player-vignette` treats a pick screen or a shop as an event with a record: what the player
  sees, expects and decides there.
