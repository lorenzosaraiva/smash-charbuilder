# Mario and Luigi Up B

Version 0.1.13, updated 2026-10-04. This milestone is decomp only.

Choose any original body, set **Up B** to **Mario** or **Luigi**, then Test in
Training. Matching body/donor combinations retain native behavior. Foreign
bodies use shared retargeted phase/recovery poses with independent donor gameplay.

## Implemented gameplay

Four original ground/air paths preserve the source 40-frame action duration,
collision centers relative to fighter position/facing, damage, size, angle,
knockback, hit groups, refreshes and creation/clear timing. Body proportions do
not change the donor reach or movement. Source US fields remain distinct:

- Mario: 5-damage opening, repeated 1-damage hits, then a 3-damage finisher.
- Luigi: 25-damage opening sweetspot, then 1-damage continuation. Ground and air
  sweetspots keep their original different angles and knockback fields.

Source TransN movement samples supply velocity without reading a foreign or
missing body joint. Native callbacks retain input steering and the facing-change
window, ground-to-air takeoff, aerial startup horizontal damping, ascent damping,
platform passing, cliff checks and landing transitions. Source opening
invulnerability and jump-exhaustion events are included in the bounded script.

Helpless recovery keeps the selected donor's gravity, terminal speeds, air
acceleration/friction and drift cap until landing. The body's full jump inventory
is exhausted, including bodies with more jumps than Mario/Luigi. Landing uses the
donor's 25-tick recovery clock independently of the body's animation length.

Per-player recovery ownership checks fighter identity and generation. Ordinary
status changes, damage, scene changes and respawn cannot reuse the prior action's
travel, steering or recovery physics. Body hurtboxes and ordinary movement remain
native outside this move. Shared animation retargeting and safe source sound/effect
events are implemented in 0.1.13; complete voice/color and rendered polish remain pending.

Borrowed startup plays source frame zero once. The native extra startup playback
is skipped only for an active borrowed visual, avoiding a second donor-clock
advance. Ground/air live pose and recovery regressions passed with Mario on DK,
Samus and Luigi, and Luigi on DK and Samus. These newer checks use Dream Land so
the stage cannot interrupt the finisher before its source frame.

## Automated checks

- `testSuperJump.py` compiles the actual Mario callbacks, engine physics, shared
  travel accessors and recovery guards against real fighter layouts. Native and
  borrowed execution are compared on twelve bodies/four slots, ground/air starts,
  both facings and five horizontal stick positions. It checks helpless physics,
  25-tick landing, damage-status cleanup and ownership/respawn isolation.
- `testSpecialTiming.py` checks all 96 phase clocks and 24 path definitions.
- `testNativeAnimation.py` checks source animation playback, movement deltas and
  collision matrices; `verifyCustomMoveRom.py` checks original packed hit fields,
  event timings, linked path pointers, recovery data and the N64 CRC.

Optional real-menu/input CPU checks, using the isolated emulator setup described
in [neutral specials](neutral-specials.md):

```bash
python3 tools/testTrainingScenes.py --superjump 0
python3 tools/testTrainingScenes.py --superjump 4
```

These check ground/air hit fields and positions, opening invulnerability,
helpless recovery, landing duration, Training reset/editor return and four-slot
VS loading. Null rendering does not establish visible contact or animation quality.

The 0.1.9 ROM passed both donors on all twelve bodies: 48 ground/air starts,
24 Training resets/editor returns and four assigned VS builds. The Luigi sweep
retained at least 1,970,980 bytes of Training heap headroom. Source-path position
bounds apply to foreign adapters. Matching donors keep their original binary
animation and collision code; their fields/timing are checked, and their source
position diagnostic differs by about two engine units. The test does not certify
bit-exact native N64 contact geometry.

The same build also passed the full nineteen-scene intro, title and Start into
the main menu, plus a Ness Up B steering/self-contact/recovery regression on DK.

## Rendered acceptance still needed

- [ ] Native donor versus small/large bodies, facing left and right.
- [ ] Luigi opening sweetspot versus late weak hit, in both ground/air starts.
- [ ] Mario multihits and final hit against an opponent and shield.
- [ ] Steering/facing changes, slopes, platforms, stage edges and cliff catch.
- [ ] Damage interruption, hitlag, KO/respawn, Training reset and four-player use.
- [x] Borrowed Up B/recovery poses and safe source sound/effect events.
- [ ] Complete coin/fire/color/voice polish and rendered acceptance.
