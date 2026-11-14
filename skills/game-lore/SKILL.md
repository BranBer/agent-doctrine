---
name: game-lore
description: Use when writing or reviewing a game's lore, world or story - the setting, history, factions, the threat, the player's role, classes and powers given an in-world origin, quest, item and enemy text, a codex or bestiary, a world or story bible - or when the user wants the lore written first, wants players to feel part of a larger story they can shape, asks how to tell a story through play rather than cutscenes, or needs an interview to pull their world out of their head. Use it even when they only say "worldbuilding", "the setting" or "what's the story".
---

# Game lore

In the games people keep playing, the story isn't told at the player: it's found by playing.
Skyrim teaches lockpicking during an escape from an execution. A Souls game puts a kingdom's
history in the description of a ring. Good lore does three things:

- **Gives the player a place in a larger story** that matters, and that they can change.
- **Gives reasons to explore and to get stronger.** Each new power or area reveals more.
- **Unfolds in layers that reward attention, and stays ignorable.** A player who skips every
  word still plays the whole game.

This skill turns the user's world into a canon and plans how each piece reaches the player.

## Who writes what

**The user is the author of the core canon. Claude interviews, drafts, checks and fills in.**

- **The quality bar.** A world in the author's own words reads as someone's, and generated filler
  reads as AI slop.
- **Ownership.** In the US, text generated purely by AI can't be copyrighted, but a human's own
  writing, choices and arrangement can. For a game whose story is its identity, keep a record of
  what the user wrote and what they accepted.

Every canon entry carries a status:

| Status | Means |
|---|---|
| `pillar` | The user's own words, kept verbatim and dated. Never rewritten without asking. |
| `accepted` | Claude drafted it, and the user read and accepted it. |
| `draft` | Not canon yet. Nothing in the game may depend on it. |

Never fill in a pillar on the user's behalf. When they're stuck, offer two or three options that
differ sharply and let them choose or mix. A blank they answer themselves beats a polished guess.

## Lore runs beside the prototype, never ahead of it

Elden Ring is the usual argument for writing lore first. There, George R. R. Martin wrote the
deep past, the myths and history before the game. FromSoftware wrote everything you play,
including the item text. All of it sat on a combat core proven over five earlier games.

Without a proven core, write the lore and build the grey-box core-loop prototype at the same
time:

- The lore says what the enemies, classes and places are.
- The prototype says which of them are fun.
- Change the lore to fit what plays well, not the other way round.

## The order

1. **Interview** the user, one round at a time (below).
2. **Pillars:** the few sentences everything else must agree with.
3. **The deep past:** what happened before the game. It is mostly told indirectly.
4. **The present:** the world as the player first finds it. Cover what is broken, who holds
   power and what they're fighting about.
5. **The player's role:** who they are, why they matter, and what they can change.
6. **Reasons for the mechanics.** Every system the game has gets an in-world reason. Take each
   wave, respawn, class, upgrade, currency and season, and ask why it exists in this world.
7. **The delivery plan:** where each piece reaches the player (below).
8. **The mysteries register:** every open question, with its true answer.

## The interview

Ask three to five questions per round, then stop and wait. Use the games the user loves as
references ("like the cart ride at Skyrim's start?"). Record the answers verbatim in
`lore/interview.md`, then reflect each round back in one or two lines before the next.

| Round | Ask about |
|---|---|
| 1. Feel | The world in one sentence. Three works (games, books, films) whose mood is right. What it must never feel like. How dark it is, and how funny. |
| 2. The wound | What broke the world, or is breaking it now. Who is blamed for it, and whether that's the truth. What was lost. |
| 3. The threat | What the enemy is, where it comes from, and what it wants. Why it comes in waves, if the game has them. Whether it's right from its own side. |
| 4. The player | Who the player is at the start: often an outsider or underdog, like a prisoner in the wrong place or a corpse that won't stay dead. Why they matter. What they can change. Why they can come back after dying. |
| 5. Powers and factions | Where each class or power comes from (each is a tradition, order or trade). Two to four factions: what each wants, what it fears, and where its own members disagree. |
| 6. The shared story | What the whole player base changes together, such as a front line or a season's outcome. What is hidden for the dedicated few to find. What players might make up for themselves. |

The user can answer a round in a sentence or an essay. Both are fine. Ask a follow-up only where
an answer leaves a pillar open.

## Rules for the canon

- **Every power has consequences.** Trace each one through three orders:
  - who gains power from it;
  - how the world's systems adapt;
  - what becomes normal.

  A world where a power changes nothing reads as a painted backdrop.
- **No side is uniformly evil.** Give every faction ordinary members and internal arguments. A
  monstrous enemy still needs a reason, even an inhuman one.
- **When a draft contradicts canon,** show both, say which is canon, and offer three fixes: change
  the draft, change the canon (only with the author's say), or explain it in the world.
- **Every mystery gets a written true answer,** even one that is never revealed. Hints stay
  consistent across writers and years, and players who test theories find a world that holds
  together.
- **In-world sources disagree.** Record who claims what, beside the truth. Rumour, propaganda and
  myth are lore too.
- **Go deep where the player touches the world.** Leave the rest as an outline. A mystery left
  unexplained can be worth more than an answer.
- **Names:**
  - Give each culture one naming sound.
  - Search every major name for trademarks and famous uses before it becomes canon.
  - Borrow no names or terms from the user's favourite games. A world can be inspired by them,
    never a copy.
- **Keep to the age rating.** For PEGI 12:
  - fantasy violence against non-human or fantasy creatures is fine;
  - no lingering gore, sexual content or real-world hate symbols;
  - no mockery of real religions;
  - no glamorised drugs or gambling.

## Lore through play

Every canon entry names at least one place where the player meets it, or is marked
`backstory`. A canon with no delivery plan becomes a document nobody reads.

| Channel | Example | Rule |
|---|---|---|
| **The opening** | Skyrim's cart ride and dragon attack | Teach the controls through story events in the first minute. Never use an unskippable wall of text. |
| **Item and upgrade text** | A Souls ring's two sentences of history | One to three sentences. Put history in the object, and leave the reader a question. |
| **Enemies** | What a creature's look and behaviour say it is | A bestiary entry deepens with each kill, so fighting reveals the story. |
| **Places** | Ruins, bodies, barricades, graffiti | Show what happened here without a word of text. |
| **Voices** | Riverwood's gossip, an announcer, barks overheard in a fight | Short lines that react to what the player just did. |
| **Progress** | New areas, classes and tiers | Getting stronger reveals more of the story. Gate the deeper lore behind progress, not behind reading. |
| **The community** | A front line every player's runs move, season chapters, secrets found together | The player's play changes the shared world, and the change is visible next session. |

For short-session games, such as browser portals:

- Show at most one line of story at load.
- Tell the details through item text, the bestiary and places.
- Never stand between the player and their first action.

## Writing the text

- Use concrete nouns and specific details over adjectives. "The bell rang for nine days" beats
  "an ancient evil awoke".
- Avoid stock fantasy unless it is subverted: chosen ones, prophecies that foretold this, "ancient
  evil", and every name with an apostrophe.
- **Watch for AI slop tells:**
  - adjectives in threes;
  - "whispers of", "tapestry", "echoes of", "a testament to";
  - every sentence epic;
  - every line the same length.

  Read the text aloud. If it could fit any world, it fits none.
- Humour, grit and plain speech are allowed. People in a world at war still complain about the
  food.
- `humanize-copy` may polish `draft` and `accepted` text, store copy and devlogs. Never run it on
  a `pillar`: its edits, such as removing em dashes, would rewrite the author's words.
- **Keep in-game text in data files, keyed by id, never in code.** Lore edits then never touch
  logic, and translation stays possible.

## Files

Keep the lore in plain markdown under `lore/` in the game's repo:

```
lore/
  interview.md     the user's answers, verbatim and dated
  pillars.md       the few sentences everything must agree with
  history.md       the deep past, with in-world claims beside the truth
  present.md       the world as the player finds it: the wound and who holds power
  player.md        the player's role, and the reason behind each mechanic
  threat.md        the enemy, what it wants, and why it comes
  factions/        one file per faction, with its classes or powers
  mysteries.md     each question, its true answer, its clues and where each clue sits
  delivery.md      each canon entry, its channel, and whether it's planned or in the game
  glossary.md      names and terms: spelling, pronunciation, the culture each belongs to
```

Give each entry its status: `pillar`, `accepted` or `draft`.

## Before calling a lore milestone done

1. **Contradictions.** Have a fresh reviewer read only `lore/` and return APPROVE, CONCERNS (each
   contradiction or unanswered mystery) or REJECT (a pillar is broken). It lists the entries it
   checked against and anything it could not check. An approval with no list doesn't count, and
   a check that didn't run is reported as not run.
2. **Coverage:**
   - every mechanic has an in-world reason;
   - every entry has a channel or is marked `backstory`;
   - every mystery has a true answer.
3. **Slop.** Read it aloud against the tells above.
4. **Names.** Every major name has been searched.
5. **The user.** They have read every `pillar` and `accepted` entry, and nothing in the game
   depends on a `draft`.

## Related skills

- `game-concept-research` picks the concept.
- `game-audience-research` and `concept-art` take the lore's mood into the art direction and the
  house style.
- `reward-systems` frames progression. The lore gives each reward a reason, and that skill keeps
  rewards teen-safe.
- `games-doctrine` covers where the text and data files live in the code.
