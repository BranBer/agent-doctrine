---
name: player-vignette
description: Use when designing, reviewing or changing anything a player experiences in a game - a default attack, an ability, a role's kit, an enemy, a wave, a run's pacing, an upgrade or item pick, a shop, a batch of sound effects or prompts, visual effects, damage numbers - and especially when the work covers one dimension at a time, when a playtester calls something repetitive, unfun, useless, boring, annoying, overwhelming or "ear torture", or before writing a game's design spec. Use it for "player experience", "what the player feels", "unified experience", "player journey" or "vignette".
---

# Player vignette

A player meets a game as events: I act, something happens, the world answers, I decide again. Each
event is made of parts that are usually designed apart: the sound, the picture, the numbers, the
enemy's reaction, the feel, the interface. A run is made of events.

A vignette is a short first-person record of one event, or one stretch of play, written before any
part of it is designed. Every part then takes its size from the player's moment, not from its own
craft. The record is a prediction: playtests test it.

## Why this exists

**The case.** A battle-mage's default attack was "ear torture, it feels like screeching in my
ears". Its sound had been prompted in a batch of 18, as "quick roaring whoosh of flame igniting" with
the fire family's style phrase "roaring torch flame" appended. Each choice was defensible on its own;
nobody had pictured it as "my bread-and-butter, twice a second for ten minutes". The player's own
prompt did better: "Crackling, whooshing firebolt impact with a subtle, satisfying hiss."

**The test.** Fresh agents without this skill designed well when asked for the whole attack: a quiet
sound, ember marks for the burn, no screen shake. Asked for one dimension, they fell apart. In a batch
of sound prompts they appended the family's "roaring" to the default attack beside their own "soft",
kept 2–3 takes of a sound heard twice a second, gave the healer's twice-a-second bolt a bell, and
gave the mage's attack no impact sound at all. Work is usually split by dimension, so every
single-dimension task has to start from the whole event.

**The theory.** Designers see a game from mechanics up to the feelings it causes; players see it the
other way round: "aesthetics set the tone, which is born out in observable dynamics and eventually,
operable mechanics" (MDA).

## The levels

Each level is made of the one below. Halo's "30 seconds of fun" was, in its author's own correction,
"a 3-second loop inside of a 30-second loop inside of a 3-minute loop that is always different".

| Level | For example | Lasts | Asks |
|---|---|---|---|
| Event | I cast my default attack | under a second | does it land, and how is the hundredth one? |
| Encounter | a wave | 30–90 s | what changes from the last one? |
| Run | ten waves | about 10 min | does it build, and what do I own at the end? |
| Session | a few runs | 20–60 min | why one more? |
| Return | the days between | days | what do I come back for? |

Cover every level before detailing one, as Cooper's scenarios are "complete in breadth more than in
depth". An attack record without a wave record misses "all these events together seem repetitive".

## The record

Fill in every slot. A slot left empty is a question for the design.

```
### <event> (<level>), <status: draft | read by the user | tested in play N>
Player: <a specific player: role, which run, the games they know well>
Rate: <times a minute, for how long>   Tier: <bread-and-butter | signature | climax | cue>
Goal: <the situation we want, in one line>
Beats, first person:
  1. I <act>. I expect ... I see ... I hear ... I feel ...
  2. It <travels / lands / ...>. I expect ... I see ... I hear ...
  3. The world answers. I expect ...
  4. I decide <reflex | considered>: ...
Dimensions        | its share at this tier | what varies each time
  sound           |                        |
  picture         |                        |
  numbers         |                        |
  enemy's answer  |                        |
  feel            | (hit-stop, shake, camera)
  interface       |                        |
The hundredth time: <what it's like then, and what I ignore, dislike or tune out>
Nightmare: <the worst case at minute ten>
Predictions: <falsifiable, e.g. "never lowers the effects slider", "names the bash unprompted">
Gaps: <an expectation not met, each one a design item; or broken on purpose, and why>
```

Expectations come from four places:
- **The metaphor:** fire burns, a shield blocks, a bell rings. "If it's going to be a car, it needs
  to read as a car" (Swink).
- **The genre and the player's own games:** a League player expects a shop; a Diablo player expects
  loot.
- **Earlier beats:** the last hit staggered it, so this one should.
- **The stakes:** my default attack shouldn't drown my teammate's warning.

## Tiers

How often an event happens sets its tier, and its tier sets every dimension. Each tier has two
budgets:
- **priority:** whether it can be masked or culled;
- **spectacle:** its loudness, brightness, length and screen effects.

DOOM's guns are never ducked; League's basic attack gets the least spectacle. A default attack can
top one budget and sit at the floor of the other.

| Tier | When | Priority | Spectacle |
|---|---|---|---|
| Bread-and-butter | many times a minute: default attacks, own hits, steps | the player's own never masked | the floor: short, quiet, small, no hit-stop or shake; 6–8 takes; a little variation in every dimension |
| Signature | every few seconds to a minute: abilities, an elite's attack | high | a clear moment: a fuller sound, a bigger picture, a light hit-stop |
| Climax | a few times a run: an ultimate, a champion's death, the last stand | top | everything else steps back: ducks, shake, the longest tail |
| Cue | whenever it matters: a threat aimed at me, a reward, the objective hit | top, never masked | fixed: the same every time, its own band, small |

League rates "a spell's importance from 1-10" so "the visual importance matches the gameplay
importance": "if everything is important, nothing is important". Helldivers 2: "reserve the headroom
for the things that must feel loud".

**Every side of an event has its own tier.** The tier belongs to the moment as each party lives it,
not to the sound file. Once enemies fought whoever stood in their road, a tank was hit several times
a second. Its "you're hurt" thud and the duck that came with it had been made as an alarm, and they
buried the music 14 LU deep. For a tank, being hit is bread-and-butter; only a heavy blow or low
health is an alarm. A mechanic that changes how often something happens changes its tier, so
re-read the records it touches.

## Rules

1. **Start from the player's end.** Write what is felt and sensed first, what is seen to happen next,
   and the mechanic last.
2. **Open the record before working one dimension.** A batch of sound prompts, an upgrade list, a
   visual-effects pass and a damage table are each a list of events. Find or write each event's
   record, and take its tier and expectations from it.
3. **The tier sets the intensity; a family sets the material.** A family's style phrase names
   material and texture, never intensity. A bread-and-butter prompt carries a restraint word:
   subtle, soft, small. "Huge" and "roaring" belong to climaxes.
4. **Write the hundredth time, not the first.** "More frequent stimulation results in more rapid
   ... response decrement", but "very intense stimuli may yield no significant observable response
   decrement" (habituation research). A quiet frequent sound fades into the background, as it
   should; a loud one keeps claiming attention. How fast something repeats drives how sick of it
   people get, and people misjudge that.
5. **Put the payoff where the player looks.** On a projectile, the impact and the enemy's answer
   carry the satisfaction; the cast is a flick.
6. **Keep the metaphor's promise in every dimension.** Fire burns: a crackle, an ember mark, a
   smoulder. A huge sound on a small spark breaks the promise, and so does a thin one on a meteor.
7. **Vary every dimension of a repeated event a little, and fix the cues.** That means the take,
   the pitch, the stagger, the spark and the number. Overwatch gives its cues "minimal variation".
8. **Every choice shown is a real decision.** No option on one screen is strictly better than
   another; two cooldown cards at 20% and 30% are one choice. A considered decision shows its
   trade-off; a reflex decision is almost always right, or can be undone.
9. **Every role's minute has a signature moment only it delivers.** A role made only of
   bread-and-butter reads as "I'm just slashing ... and that's all I can do". Write the goal as a
   situation the player finds themselves in (Fullerton's experience goals), not a feature.
10. **Name a specific player, from what is known.** Make them precise rather than average, and never
    the designer. Cooper: "Real users are not elastic." Take their games and habits from the user's
    words or the game's audience research. When nothing says who they are, write "unknown: a guess"
    and the guess, and never borrow the example's player.
11. **Write the nightmare beside the hope,** the worst case at minute ten.
12. **Predictions are falsifiable, and play decides.** After each playtest, put the player's words
    beside the record's predictions, correct every mismatch, and mark the record as tested. A record
    never overrules what a player said. In one game study only real players found "boredom,
    challenge and pace level"; the authors call user testing "the benchmark".

## How vignettes go wrong

| Failure | Guard |
|---|---|
| **The elastic player:** the imagined player bends to justify what is being built (Cooper) | a named, specific player, fixed before the design |
| **The designer as the player** | the player's own games and habits, from their words |
| **Too favourable:** AI-made users "seem to care about everything" and praise what they're shown (NN/g, 2024) | every record says what the player ignores, dislikes or tunes out, and has a nightmare |
| **A story that can't be wrong** | predictions a playtest can check |
| **Justifying after the fact** | write the record before the design, and keep its first version |
| **Replacing playtests** | records predict; only play finds boredom and pace |
| **Fiction instead of records:** adjectives, no rates | the template, at 15–25 lines a record |
| **Records for everything** | in a prototype round, about ten: each role's default attack and key ability, one wave, one run, the pick screen |

Don't hang a decision on "System 1": the two-systems split is contested, and even Kahneman calls the
systems "fictitious characters". Tag a decision as reflex (mid-wave, under a second) or considered
(between waves, a shop) instead.

## With the other skills

The records come first; the other skills design their dimension from them.

- `sound-design` and `game-audio`: the tier sets each prompt's intensity word, how many takes it
  needs, its mix level and whether it can be culled.
- `combat-feel`: the beats are its four beats of a hit, and the tier sets hit-stop and shake.
- `intensity-director`: the encounter and run records are its build, peak and relax.
- `reward-systems`: the pick screen and the shop are events with records, and rule 8 applies.
- `game-lore`: the fiction is where the metaphor's promises come from.
- `games-doctrine`: in the prototype lane, the core events' records come before the build, and the
  user reads them.

## Files

Keep the records in the game's `design/vignettes.md`, grouped by level, each with its status. After
a playtest, log the player's words in the game's feel log and link each tested record to that entry.

## Example: the mage's default attack, as built when it failed

```
### Ember bolt (event), tested in play 5
Player: plays League (ARAM) and Diablo IV a lot; third run, as the battle-mage
Rate: about 2 a second, all ten minutes   Tier: bread-and-butter
Goal: I paint the horde steadily and save my attention for the threats
Beats:
  1. I hold the button. I expect a flick, felt more than heard.
     v3.2: a roaring whoosh, the loudest part of the event.
  2. It flies. I expect to see it go where I aim.
  3. It hits a skeleton. I expect it to burn: a crackle, a hiss, an ember mark.
     v3.2: a filtered noise burst, the same for every fire hit.
  4. The skeleton answers. I expect a stagger, or smouldering. v3.2: not checked.
  5. I decide (reflex): the next target, without thinking about the bolt.
The hundredth time: the roar never fades into the background; it grates.
Nightmare: at minute ten I turn the effects down, and lose every cue with them.
Predictions: after the fix, the player no longer mentions the attack's sound.
Gaps: cast and impact the wrong way round; no burn in sound, picture or enemy;
nothing varies but the sound's take.
Play 5: "the battle mage autoattack is ear torture, it feels like screeching in my ears".
```

## Sources

- Hunicke, LeBlanc and Zubek, "MDA", 2004: https://users.cs.northwestern.edu/~hunicke/MDA.pdf
- Wharton, Rieman, Lewis and Polson, the cognitive walkthrough (1994), via the UXPA Usability BoK: http://usabilitybok.org/print/cognitive-walkthrough/
- Desurvire, Caplan and Toth, "Using heuristics to evaluate the playability of games", CHI 2004: https://hci.rwth-aachen.de/materials/conferences/CHI2004/2p1509.pdf
- Pruitt and Grudin, "Personas: Practice and Theory", DUX 2003: https://www.microsoft.com/en-us/research/wp-content/uploads/2017/03/pruitt-grudinold.pdf
- Cooper, *The Inmates Are Running the Asylum*, 2004 edition, chapters 9 and 11
- Rosala and Moran, "Synthetic Users", Nielsen Norman Group, 2024-06-21: https://www.nngroup.com/articles/synthetic-users/
- Fullerton, *Game Design Workshop*, 5th edition (excerpt, 2024-04-18): https://www.gamedeveloper.com/design/book-excerpt-game-design-workshop
- Swink, "Game Feel: The Secret Ingredient", 2007-11-23: https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient
- Griesemer interview, Joystiq, 2011-07-14: https://www.engadget.com/2011-07-14-half-minute-halo-an-interview-with-jaime-griesemer.html
- Cook, "Loops and Arcs", 2012-04-30: https://lostgarden.com/2012/04/30/loops-and-arcs/
- Rankin et al., "Habituation revisited", 2009: https://pmc.ncbi.nlm.nih.gov/articles/PMC2754195/
- Galak, Kruger and Loewenstein, satiation and consumption rate, JDM 2011: https://ideas.repec.org/a/cup/judgdm/v6y2011i3p230-238_5.html
- Jacobsen, "Game audio immersion", A Sound Effect, 2018-05-16: https://www.asoundeffect.com/game-audio-immersion/
- Walden on Helldivers 2, A Sound Effect, 2024-04-26: https://www.asoundeffect.com/helldivers-2-game-sound-design/
- Riot, "Clarity in League", 2021-03-12: https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/
- Riot, "Anatomy of a LoL missile, part 2", 2020-05-25: https://realtimevfx.com/t/anatomy-of-a-league-of-legends-missile-part-2-what-are-we-communicating-with-our-vfx/13062
- Mossholder on DOOM's sound, ADSR, 2016: https://www.adsrsounds.com/news/the-sound-design-of-doom-exclusive-qa/
- Melnikoff and Bargh, "The Mythical Number Two", 2018: https://acmelab.yale.edu/sites/default/files/melnikoff_bargh_2018_mythical_number_2_0.pdf
