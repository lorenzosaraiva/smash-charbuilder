# Spin Attack, Screw Attack and Rest

Version 0.1.10, updated 2026-10-04. This milestone is decomp only.

The earlier adapters could enter each donor's native states and reproduce numeric
hitbox values. They did not preserve complete donor collision geometry or all
movement/recovery attributes on foreign bodies. This update completes those
three gameplay adapters; their foreign-body special animations remain temporary.

| Move | Gameplay coverage |
| --- | --- |
| Link Spin Attack | Original fighter hit paths, 16/8-damage phases, 60-tick ground action, 100-tick air action, 40-tick ground ending, donor aerial rise/gravity/drift and native floor/cliff callbacks. Ground/air changes resume the original clock. |
| Grounded spin weapon | Native Link Main weapon data, root spawn, two expanding attacks, source radius flags (120/100/80), movement history, lifetime, hitlag and destruction. The air-start version does not spawn this ground weapon. |
| Samus Screw Attack | Original four-hitbox paths, repeated hits and finisher, 50-tick ground/48-tick air action, distinct TransN-driven ground-launch versus fixed-rise aerial physics, startup intangibility (6 ground/4 air ticks), original platform-pass/cliff callbacks. |
| Jigglypuff Rest | One active tick at donor frame 1, 20 damage, radius 130, angle/knockback/element/shield fields from US sources, invulnerability until frame 30, 250-tick sleep, donor friction/gravity/air limits. Landing and edge transitions continue sleep. |

Aerial recovery keeps donor gravity, terminal velocity and drift until landing.
Source landing animation lengths/rates give Link 13, Samus 20 and Mario/Luigi
25 ticks. Landing during active Spin Attack enters Link's separate 40-tick ending
instead of substituting a generic landing. Body hurtboxes and the body's jump
inventory stay native. No remaining Kirby jumps bypass helpless recovery.

The grounded spin weapon is destroyed on native completion, floor/cliff paths,
and damage/capture/reset exits. The original code called a weapon hit-position
function with a fighter pointer; it now supplies the owned weapon pointer.
Ground/air transitions reinstall its hitlag callback after status replacement.
Foreign spin-weapon ownership has separate per-player storage, preventing common
landing/capture setters from overwriting it before status replacement.
Cleanup requires a matching action clock, owner and fighter generation, so a
Training reset cannot interpret a recycled status union as a weapon pointer.

## Checks

The required build runs `testDirectSpecials.py`, compiling production callbacks,
physics, clock/recovery helpers and Link weapon behavior with real 32-bit fighter
and weapon layouts. Native donor versus deliberately different body attributes
are compared for every body, four player slots, both facings, ground/air starts
and five stick directions. It also exercises ground/air continuation, source
landing lengths, map branches, hitlag and owned-weapon interruption cleanup.

`testNativeAnimation.py` compares all 30 special path phases with original C
animation playback and collision matrices. `verifyCustomMoveRom.py` checks
linked production code, source packed hit fields, scripts, paths and recovery
clock records in the ROM. A recycled-fighter regression deliberately leaves an
invalid old weapon pointer and verifies the reset skips it. Native weapon data
is loaded through Link's original weapon factory, independently of body proportions.

Optional Linux emulator checks use actual menu handlers and fighter input:

```bash
python3 tools/testTrainingScenes.py --direct-special 5
python3 tools/testTrainingScenes.py --direct-special 3
python3 tools/testTrainingScenes.py --direct-special 10
```

These inspect source damage/radius/knockback, foreign collision centers, startup
hit status, complete action/recovery timing, Link's ground weapon, Training reset,
return to the same editor and four assigned VS slots. The renderer is null, so
these checks establish CPU gameplay execution rather than visual acceptance.
Timing runs select Dream Land to avoid stage hazards interrupting the action;
the ground and air starts are separated by a real Training reset to clear staling.
All three donors passed on all twelve bodies in the 0.1.10 ROM: 72 ground/air
starts, 72 Training resets, 36 returns to the same editor and three four-slot VS
loads. Foreign compiled-source center checks stayed within 0.0002 engine units.
Native body/donor fallbacks keep the original native data; their centers are
recorded diagnostically (up to 3.78 units versus the sampled source), while their
hit fields/timing are asserted. Original C matrix comparisons independently
check the source geometry; this does not establish bit-identical native N64
matrix rounding. See [emulator setup](neutral-specials.md).

The final binary also passed uninterrupted cold boot through all nineteen intro
scenes and title/Start, Mario Up B on DK, Ness steering/controlled self-launch
on DK, and 1,288 live normal poses on Mario plus four-slot VS regressions.

## Remaining acceptance

- [ ] Retarget the visible special animations onto each body.
- [ ] Rendered hit/contact, multihit connection, DI, wall/ceiling/platform/ledge
      interactions, damage/capture interruptions and every matchup.
- [ ] Matching special effects/voices and foreign sword/costume/accessory visuals.
- [ ] Port this special fidelity to the separate Remix build.

The gameplay adapters are implemented and automatically checked. Full visual and
manual gameplay acceptance remains pending; report the body, donor, emulator,
commit and steps for any mismatch.
