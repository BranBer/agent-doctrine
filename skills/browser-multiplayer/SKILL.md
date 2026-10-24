---
name: browser-multiplayer
description: Use when planning, building or costing real-time multiplayer for a browser game - netcode, authoritative servers, Colyseus, Nakama, Photon, matchmaking, rooms, bots, friends, parties, clans, chat, leaderboards, hosting, server bills, anti-cheat, chat moderation - or when a portal such as CrazyGames asks for multiplayer or chat requirements.
---

# Browser multiplayer

For a small team, multiplayer is a bandwidth bill and a moderation duty more than a code problem.
Own the server on flat-rate hosting, keep it portable, and ship chat last.

The evidence and prices (read 2026-10-23) are in `reports/Multiplayer reward systems teardown.md`
in the `profit` research folder. Load `games-doctrine` for the shared headless simulation. Load
`crazygames-publishing` for the portal's multiplayer and chat rules.

## The stack

| Layer | Choice | Why |
|---|---|---|
| Simulation | One headless TypeScript sim, shared by client and server | The client predicts and the server decides. Clients send inputs only. The server resolves movement and hits with lag-compensated rewind. |
| Game rooms | Colyseus over secure WebSocket, 20–30 Hz snapshots, delta compression, interest culling | Never send positions a player can't see. That is what defeats wallhacks. |
| Social and meta | Nakama (Apache-2.0, Postgres): accounts keyed to the portal user, storage, friends, groups as clans, channels for chat, leaderboards, matchmaker | Built in and free. Per-user vendors cost thousands. |
| Empty lobbies | Bots fill public rooms, then leave as humans join | Bullet Force and Hazmob are reported to fill lobbies with bots |
| Transport | WebSocket first | WebTransport only as a later upgrade. geckos.io (WebRTC) needs open UDP ports. |
| Hosting | Flat-rate servers (Hetzner, OVH), one region at launch, Docker images | Bandwidth sets the bill. Hathora and Unity Multiplay both shut down in 2026, so stay portable. |

## Cost

These figures assume about 10 KB/s per player and an average load around 35% of peak. Measure your
own bytes per player in the first spike and redo the sums.

| Stage | Peak players at once | Setup | Per month |
|---|---|---|---|
| Build and playtest | under 20 | Docker on your own machine | $0 |
| Launch | up to ~100 | One server running Colyseus, Nakama and Postgres | ~€20–35 |
| Growing | ~1,000 | Game servers in the EU and US-East, plus a separate Nakama/Postgres box | ~€90–130 |
| Hit | ~10,000 | ~40 vCPU across three regions, plus two backend boxes | ~€750–900 |

How the alternatives compare:

- **Metered relays and hosts cost 5–10 times more at scale.** Photon, Unity Relay and Edgegap
  charge per player or per GB. Photon includes only 3 GB per player per month.
- **Client-authoritative modes invite cheating.** Photon Fusion Shared and peer hosting fail a
  competitive shooter.
- **Chat priced per monthly user is a trap.** Stream costs about $3k a month at only 100 peak
  players.

## Login and operations

- **Login.**
  - Nakama's custom authentication receives the portal's user token. On CrazyGames, that is the
    `getUserToken()` token, an RS256 token valid for 1 hour.
  - The server verifies the token against the portal's public key, then keys the account on the
    verified `userId`.
  - The client asks for a fresh token before the hour is up and re-authenticates the socket.
- **Operations, which is nearly the whole running cost after hosting:**
  - nightly Postgres dumps sent to another box;
  - the host's included DDoS protection;
  - an uptime check plus server logs;
  - a monthly update of Nakama and Colyseus.

## Anti-cheat

There is no browser anti-cheat to buy, so the server is the anti-cheat:

- inputs only from clients;
- server checks on speed, fire rate and line of sight;
- per-socket message rate limits;
- leaderboard scores written only by the server;
- bans tied to the portal account;
- reports that snapshot the server's last inputs.

## Chat and moderation

The platform asks for little. The law and the ratings ask for more:

- **CrazyGames:** a profanity filter, and honouring `disableChat` at start and on change. It can
  force chat off after complaints.
- **PEGI:** rates player communication without block, report and filter at 18.
- **The FTC's Epic order:** treats voice and text chat switched on by default for children and teens
  as harmful.
- **New York:** its 2026 law bars adults who are not connected to a child from messaging them.
- **The UK Online Safety Act:** expects block, mute and report.

The setup that meets all of this, for about $0 a month:

- **Strangers:** public rooms get quick-chat phrases and emotes only. A "global chat" open to
  everyone is a quick-chat channel, never free text.
- **Free text:** only among friends, parties and clans, off by default and opt-in. It unlocks after
  a cooldown and an account level. A neutral age question keeps under-13s on quick-chat; get legal
  advice on how to ask it.
- **Names:**
  - Use portal usernames.
  - Clan names come from preset word lists.
  - Any custom text passes the `obscenity` package plus a custom leetspeak list.
  - Links, digit strings and @handles are blocked.
- **Player controls:** mute, block and report on every name and message, with rate limits and
  automatic mutes after repeated filter hits or reports.
- **Back office:**
  - OpenAI's free moderation endpoint checks flagged messages asynchronously.
  - An admin page and a ban list.
  - A server switch that kills free text.
  - Logs kept 30–90 days.
- **Never ship:** voice or image uploads. Don't build on Perspective API, which shuts down on
  31 December 2026.
- **Paperwork:** terms, community rules, a contact email, the UK risk assessments, and no "safe for
  kids" claims.

## Build in stages

Each stage has a gate. Don't build the next stage until the gate passes.

| Stage | Ships | Gate |
|---|---|---|
| 0. Netcode spike (2–3 weeks) | Shared sim, one room, prediction and interpolation, server hit checks, bots, measured bytes per player | 8–10 players plus bots feel fair at 150 ms simulated latency |
| 1. Launch build | One mode, 2–3 small maps, instant join with bots, the portal's room and invite calls, usernames, quick-chat only, fixed unlocks | The portal's launch metrics |
| 2. Progression | Persistence, missions, season track, crates per `reward-systems`, mute, block and report, name filter, admin page | Playtime and next-week return improve |
| 3. Social | Friends, parties, clans, clan leaderboards, opt-in free text, ranked play, second region | Ranked queues fill in under a minute without bots |

Two rules stop wasted work:

- **Low traffic:** if peak players online stay under about 50 for a month after full launch, freeze
  ranked and clans and keep the game as bot-backed casual play.
- **Chat switched off:** the game must work on quick-chat alone, for the day the portal forces chat
  off.

## Common mistakes

- **Building on a hosted relay or a client-authoritative mode for a competitive game.** It is
  cheatable, and it gets expensive at scale.
- **Chat or social features from per-monthly-user vendors.** Use Nakama's built-in chat and social
  features instead.
- **Free-text chat with strangers before block, report and filter exist.** It breaks the PEGI 12
  ceiling.
- **Estimating cost from CPU.** Measure egress instead.
- **Tying the game to one hosting vendor.** Two closed in 2026.
