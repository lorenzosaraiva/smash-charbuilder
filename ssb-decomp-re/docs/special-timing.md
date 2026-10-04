# Up/Down B timing and collision paths

Borrowed specials use donor status callbacks, an independent donor clock and a
safe event stream. The body supplies a temporary idle/falling pose. Matching
body/donor combinations still run native specials. Hitlag and pause stop the
clock; native ground/air transitions preserve the requested source progress.
Their native fast-forward rules also apply: landing clears attacks and skips
earlier creations; each cleared attack ID
returns when its next source creation event executes.

Generated data comes from the original US motion descriptors, event scripts,
animation tracks, joint hierarchy and fighter size. Collision centers follow the
donor skeleton relative to fighter position/facing. The target body's joints and
size do not change donor reach. Damage, size, angle, knockback, shield damage,
hit groups and active/clear times retain their original packed values.

## Implemented donor paths

| Donor move | Coverage |
| --- | --- |
| Mario/Luigi Up B | Four source 40-frame ground/air paths; distinct hit fields, source movement/steering and takeoff events, donor helpless physics and 25-tick landing recovery. See [Super Jump Punch](super-jump-punch.md). |
| DK Down B | 3-frame startup, 34-frame repeating slap cycle, 5-frame recovery; four source hitboxes on frames 16-17 and 26-27. |
| DK Up B | Both 100-frame spin phases, source collision positions/flags, donor gravity/terminal speed and native drift/recovery callbacks. |
| Mario/Luigi Down B | Distinct donor event streams, 87-frame ground / 83-frame air phases, donor aerial gravity and native tap-to-rise behavior. |
| Falcon Down B | Ground, ground-to-air, landing, aerial and wall-bound phases; source root movement, angles, collisions and native contact/transition callbacks. |
| Ness Up B | Nine phases, source hold-phase projectile socket, native steering/expiry/self-contact logic and the 28-tick launch action. |

Tap B again during DK's grounded slap cycle to queue another complete cycle.
Tornado's rise-expenditure flag is stored separately on foreign bodies and resets
on grounding and fighter initialization. Native Mario/Luigi retain their normal
passive field. DK spin/Tornado/Ness aerial callbacks read donor attributes; the
body keeps its hurtboxes, jump inventory and ordinary movement outside the move.

Falcon Kick's translation comes from sampled donor TransN displacement and
rotation, with facing/slope conversion. Slope-transfer angles have separate
storage; movement never reads a missing body TransN joint. Native contact slowdown
and wall/landing transitions still apply; airborne recovery friction/gravity use
Falcon values. The body's placeholder animation cannot add travel.

## Ness Up B

PK Thunder needs Ness's Main weapon data and Model data for wave/trail effects.
Both are preloaded when a preset uses Ness Up B, fixing the foreign-body freeze.
Thunder's trail ring/destruction flag have independent per-player storage.

The projectile spawns from the original donor joint-12 socket. Ness's launch pose
loops every nine frames, but its native gameplay action lasts 28 ticks. The donor
clock follows that action timer so the looping pose cannot repeat or delay hitbox
and recovery events. Source launch collisions clear at frame 19.

## Checks and remaining work

`testSpecialTiming.py` compiles production clocks/accessors against real 32-bit
fighter layouts. It checks all 96 phase clocks and all 24 collision/travel/
spawn definitions on twelve bodies, four slots and both facings, including state
isolation and reset guards. The animation oracle compares every new path, active
mask, movement delta and socket with original C playback/collision matrices.
The ROM verifier follows linked pointers and checks original packed event fields.
Version 0.1.9 expands the path registry from 20 to 24 phases with Mario/Luigi Up B.
Its dedicated callback/physics test also compares native and borrowed movement,
steering, recovery and interruption cleanup. Visible special poses remain temporary.

Optional Linux emulator tests (see [setup](neutral-specials.md)):

```bash
python3 tools/testTrainingScenes.py --specials
python3 tools/testTrainingScenes.py --path-donor 2
python3 tools/testTrainingScenes.py --path-donor 0
python3 tools/testTrainingScenes.py --path-donor 4
python3 tools/testTrainingScenes.py --path-donor 7
python3 tools/testTrainingScenes.py --path-donor 11
```

Donor IDs are DK, Mario, Luigi, Falcon and Ness respectively. The path tests use
real menus/input/CPU execution and compare runtime collision masks with source
phase data. All five donors passed across twelve bodies, including grounded/air
starts, Tornado B-tap rise, Kick travel, editor return and four-slot VS loading.
Ness steering uses stick input; launch testing places the live head
inside the native self-contact box after its startup delay, then checks native
launch, hit timing and recovery. This controlled contact fixture does not verify
a player steering the entire loop back into the fighter.

Rendered contact/reflection, interruptions, visual acceptance, natural-loop
self-launch controls and broader stage/velocity comparisons remain pending.
Other Up/Down B collision paths, sockets, movement and effects are still
experimental. Full animation retargeting follows collision/timing fidelity.
Remix does not include this batch.
