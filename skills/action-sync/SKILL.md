---
name: action-sync
description: Use when timing a sound to an animation or a game event - an attack's whoosh and impact, a bow or spell release, footsteps, hit and death reactions, ability wind-ups - when a hit sounds late, early, detached from the motion or "like the game playing a sound", when deciding which part of a sound lines up with which frame and what fires it, or when checking audio-to-action sync by measurement instead of by ear.
---

# Action sync

A hit is one instant across three channels: the contact pose, the sound's onset and the victim's first
reaction. When they agree in time and in weight the player perceives one event they caused. When each
fires correctly but on a different beat, the player perceives code executing.

`game-animation` holds the move sheet these times come from. `game-audio` covers sourcing, the engine
and the mix; `sound-design` the sounds themselves.

## Which part of the sound belongs to which moment

Build an action's sound in separately triggered parts, as shipped action games do. The offsets are
starting values: only the split and the trigger rule have published support.

| Part | Lines up with | Fired by | When the action is cancelled |
|---|---|---|---|
| Wind-up (grip, cloth, charge loop, an enemy's tell) | First frame of the wind-up pose | Entering the wind-up | Fade over 30 to 80 ms |
| Effort voice | Start of the forward swing | The commit, on its own rationed voice | Let it finish |
| Whoosh | Its **loudest point** on the weapon's fastest frame, just before contact | Scheduled ahead from the swing's start | Drop it if not yet started |
| Release (bow twang, cast) | The frame the projectile spawns | The sim's spawn event | - |
| Impact | Its **onset** on the contact frame, which is also the first frame of hit-stop and the victim's flinch | The sim's hit event | Never cancelled |
| Victim's voice | Start of the hit or death reaction | The sim's event, rationed | - |
| Tail, ring-out, debris | The recovery; cut by the same actor's next impact | Rings out from the impact | Rings out |

**When the sim acts on the press** there is no wind-up to hang a lead-in on: a whoosh, a bow draw or
a charge started on the press peaks after the blow it should announce. Choose one, knowingly:

- play only what belongs from the moment on (impact or release, then the tail), and move the lead-in
  to the recovery, where it reads as readying the next attack (re-nocking, re-gripping);
- use a lead-in short enough to be over inside the entry blend (a peak under about 30 ms); or
- give the sim a wind-up of a few ticks, which is a gameplay change for the designer to feel.

**When presses outrun the rhythm**, every sim hit still fires its impact, and each impact cuts the
last one's tail. Lead-ins and effort voices are the parts to ration: at most one per chain step, and
none if the previous one is still sounding.

## Rules

- **Facts follow the simulation, motion follows the animation.** A sound that asserts something
  happened (impact, block, death, release) fires once from the sim's event. A sound that describes
  movement and is harmless if dropped (whoosh, footstep, cloth) follows the clip or is scheduled from
  the move sheet. Clip-attached events are documented to skip, double and fire for cancelled clips.
- **Late is forgiven, early is not.** People notice sound about 45 ms early but only about 125 ms late
  (broadcast thresholds; 75 and 188 ms for a hammer blow). Aim for the onset 0 to 40 ms after the
  visual contact, and never before it. [The window is our inference from those thresholds.]
- **Consistency beats shortness.** A constant wind-up becomes part of what the player predicts, and
  the hit arriving on schedule is what makes it feel theirs. Varying the interval does the damage.
- **A steady skeleton, a varied surface.** Players memorise an exact waveform within a few hearings.
  Vary the take, pitch and layer by cause (target, strength, chain step); keep the timing fixed.
- **Frequent sounds are modest.** A basic attack is heard every half second: informative, not a
  spectacle. Save intensity for finishers and abilities.
- **Precision belongs on impacts and releases.** A swing has no sharp visual moment, so the whoosh
  tolerates far more error than the hit.

## Measure it

Two scripts in `scripts/`, run with `uv run --no-project --with numpy --with soundfile python -I`.

**`transients.py <audio dir> --out sync.json`** reads every sound file and reports where its sync
point is: `onset` for a hit, `peak` for a swell, plus leading silence and the spread between takes.
A hit whose onset is past 15 ms lands that late when started on the event. Fix it one of two ways:

- trim the file's lead, or re-cut the take; or
- where the moment is known ahead, start it early by its sync time:
  `at = audioNow + secondsUntilMoment - sync / 1000`, never before `audioNow`.

A whoosh is the second case: started on the swing's first frame, it must peak at the contact, so a
whoosh that peaks at 80 ms needs a move with at least 80 ms of wind-up, or a shorter whoosh.

**`synccheck.py <capture dir> --sync sync.json`** reads a probe's recording of the game: a bus stem
and `trace.json` with `starts` (`name`, `bus`, `call`, `at` in seconds from the recording's first
frame, one per sound the engine started). For sounds that stood alone it reports how long after the
call the stem actually rose. `arrive` should equal `wait` plus the file's own onset: anything more is
the engine holding the sound.

The probe is the project's own (see `game-audio` for the recording pattern): wrap the engine's play
call while recording, and log the audio clock when it is called and the time it schedules.

First run, a tank's sword on a web game: 44 clean swings arrived a median 14 ms after the call against
a file onset of 13 ms, so the engine added about 1 ms and all the lateness was in the files. The same
pass found the swing whoosh peaking 80 ms after a hit that lands on the press: the whoosh trailed the
blow it should lead.

## What this cannot see

- It measures the engine's output. Wired output adds tens of milliseconds; Bluetooth adds 150 to 370,
  beyond any fix. Log `AudioContext.baseLatency` and `outputLatency`; do not compensate.
- Schedule predictable sounds on the audio clock (`AudioContext.currentTime`); start reactive ones in
  the same tick as their event. A timer or a frame callback slips.
- A check that did not run is reported as not run. Both scripts say what they measured, what they
  skipped and why.
- Sync is necessary, not sufficient: whether a hit feels good is judged in play.

Background and sources: `reports/Combat animation and sound sync.md` in the profit repo.
