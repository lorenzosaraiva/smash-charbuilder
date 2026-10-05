# Shared special animations

Version 0.1.13, updated 2026-10-04. Decomp only; Remix keeps its previous build.

Borrowed specials now show donor poses adapted to the selected body. Choose a
neutral, Up B or Down B donor, then **Test in Training**. Hold/release charge moves,
try an aerial version, and use **Start -> View -> HITBOX** to compare the visible
pose with the donor attack path. Matching donor/body moves still run natively.

## Coverage

| Catalog | Included phases |
| --- | --- |
| Neutral B | 40 ground/air entries: Laser, Fireballs, Jolt, PK Fire, Punch, Pound, Giant Punch startup/charge/partial/full release, Charge Shot startup/charge/release, Boomerang throw/empty/catch and Egg Lay grab/catch/release. Kirby copy is excluded. |
| Up B / Down B | All 99 existing donor phase clocks, including DK Hand Slap startup/slap/end, direct attacks, bombs/eggs/Thunder, directional Fire Fox/Quick Attack, held fields, Falcon Dive, Final Cutter and Stone. |
| Recovery | 16 helpless/landing entries for Mario, Luigi, Link, Samus, Fox, Pikachu, Falcon and Ness. Landing pose rate follows the existing donor landing lag. |

The common catalog contains **429 distinct normal/special clips**: the original
293 normal timelines plus 136 special/recovery timelines. Shared bind maps adapt
them to all twelve bodies; this does not require hand-authoring every combination.

Source startup, active time, damage, knockback, hitbox reach, movement and recovery
remain independent gameplay data. A short looping Thunder/PSI pose cannot restart
its longer gameplay script. Charge startup speed, ground/air continuation and
interruptions use existing source clocks. Hitlag/pause freeze pose progress with
the action. Physical root travel is applied once, separately from visual posing.
Fire Fox/Quick Attack flight and Super Jump steering adjust the visible pitch.
Charge callbacks use the donor cycle boundary directly, so a looping pose cannot
leave Giant Punch charging forever or prevent a stored/full release.

## Effects and props

- Native Reflector, Sing and PSI Magnet effects run on borrowed specials.
- Final Cutter draw/up/down/trail and Falcon Punch/Kick attachments use semantic
  visual joints. Gameplay projectile, capture and collision sockets keep their
  independently sampled donor paths.
- Fox's blaster, Yoshi's extending tongue and Kirby's Stone model are standalone
  effect objects using original assets and sampled donor transforms. They do not
  replace the body's rig or scale its hurtboxes. Stone temporarily hides only
  body rendering, then restores it on release or interruption.
- Samus's held Charge Shot orb uses its native visual asset/size as a collision-free
  effect. It follows the source charge socket and disappears when charging ends.
- A separate source-timed visual script restores safe common effects and sound
  events. Donor model/texture edits, actor-specific constructors and full voice/color
  changes are not blindly applied to another body.

Required model/effect assets are preloaded for selected builds. Standard fighter
effect cleanup handles interruption and phase changes; prop tracking validates
live effect ownership before using a saved pointer. Per-player generation checks
protect pose/recovery state against stock loss and reused fighter memory. Scene
allocation resets saved effect/recovery pointers before player identities restart.

Compressed pose keys live in a separately loaded Expansion Pak bank. The game
heap starts after that bank, so the larger catalog cannot push lower-bank game
code into the original video buffers. Linking and ROM verification reject
overlapping overlays or a pose bank that leaves too little gameplay memory.

## Verification and remaining work

The standard build runs `testSpecialAnimations.py`, original C playback/matrix
comparisons for every clip/frame/body, prop-transform/extension checks, existing
gameplay regression tests and linked-ROM verification. `testTrainingScenes.py
--special-animations` compares live MIPS poses with those host references and can
be combined with the existing neutral, special-mechanic and recovery sweeps.

The 0.1.13 checks passed all 429 clips on twelve body rigs: 5,421,262 joint-world
orientations and 1,372 native prop transforms compared with original C playback.
The selector fixture checks all 139 attack bindings and 16 recovery entries.
Live CPU sweeps passed neutral entries, charge/store/partial/full release, held
fields, directional movement, Cutter/Stone and Mario/Luigi Up B on selected foreign
bodies, including same-editor returns and four assigned human/CPU builds in VS.
Normal-animation and twelve-normal-donor preload regressions also passed.

To repeat the charge transition check alongside live pose comparisons:

```bash
python3 tools/testTrainingScenes.py --special-animations --charge-animations
```

These automated CPU checks use null rendering. They do not establish rendered
mesh, material, lighting, sound or contact quality. Compact bodies can still look
odd, and donor reach can extend beyond their limbs. Full voice/color polish,
paired victim rotation/choreography, tethers and Kirby copy remain pending.

Please report **body + donor + phase/input + emulator + build version**, ideally
with a short clip. Keep gameplay timing/reach ahead of cosmetic improvements.
