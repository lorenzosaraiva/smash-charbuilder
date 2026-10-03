# Neutral B donors

The decomp ROM offers Body Move plus all eleven original neutral donors other
than Kirby's copy system. Matching donor bodies keep their native move. Foreign
bodies use their own neutral pose with a separate donor action clock, source
collision path/values and native weapon or capture services.

| Choice | What follows the donor |
| --- | --- |
| Fox Laser | Ground/air fire and repeat windows, native laser |
| Mario/Luigi Fireball | Fire frame 16, recovery 46, source spawn and native weapon |
| Thunder Jolt | Fire frame 21, recovery 64, source spawn and native surface/air weapon |
| PK Fire | Fire frame 20, recovery 72 ground/60 air, native spark and flame pillar |
| Falcon Punch | Hit frames 42–46, damage/knockback/radii, 90-frame action, ground travel and aerial boost |
| Pound | Hit frames 12–27, damage/knockback/shield damage, 55-frame action, ground travel and aerial boost |
| Giant Punch | Startup, looping charge, stored charge, partial/full punch collisions and recovery |
| Charge Shot | Charge ticks, stored level, startup speed, native shot scaling and recoil |
| Boomerang | Throw/empty/catch phases, tilt/smash throw, native flight, return, reflection and lifetime |
| Egg Lay | Donor grab path/window, capture socket and swallow/release timing, native egg damage/escape state |

## Charge controls

Start charging with B. During charging, **B or A** releases; **Z** stores the
charge. Ground rolls also store it. Giant Punch applies queued release/cancel at
the source cycle boundary. A full charge stops charging and fires on the next B.
Charge Shot fires immediately in the air; leaving the floor while charging also
fires the stored level. Taking damage during charging clears the charge.
Respawning or starting another match clears stored charge and outstanding
boomerang ownership.

Throwing B again while a boomerang is out uses Link's empty phase. Returning it
during the appropriate interrupt window uses the catch phase. These callbacks
do not write the borrowing body's native special union.

## Memory and visual limits

Set the emulator to **8 MB RDRAM / Expansion Pak**. Full-roster previews and donor
resources exceeded the original scene heap, which froze Test in Training before
character selection finished loading. Training/VS selection and matches now use
a separate 4 MB arena in the upper bank, clear of overlays and framebuffers.
The editor shows the requirement and blocks Test/Play VS with only 4 MB.

Most visible poses still belong to the body. Samus's held charging orb and donor
voice/effect events are not yet reproduced. Egg Lay positions the victim using
the donor tongue socket, then hands off to the native egg state; exact victim
rotation and matching attacker animations remain pending. Body hurtboxes remain
native. Up B/Down B use the earlier experimental adapters.

Host tests cover all six new foreign-body choices, ground/air and four player
slots, stored charge, native fallbacks, boomerang identity and egg handoff.
Original C animation/matrix checks cover 30 donor phases, root travel, weapon
sockets and capture anchors. The ROM verifier checks packed source fields and
every linked phase/data pointer. These checks do not establish rendered animation
quality or complete contact/reflection/absorption acceptance.

An optional Linux ROM smoke test uses the actual menus/loaders and CPU, with
null video/audio and the Mupen64Plus HLE RSP plugin. It keeps configuration and
saves under `build/scene-smoke/`, independently of your normal emulator:

```bash
sudo apt-get install clang libmupen64plus2 libmupen64plus-dev mupen64plus-rsp-hle
python3 tools/testTrainingScenes.py
python3 tools/testTrainingScenes.py --four-mb
python3 tools/testTrainingScenes.py --egg-lay
```

Use `--core`, `--rsp`, `--headers` and `--data` for alternative installation
paths. This exercises Test -> character/stage selection -> Training, B actions
and return to the same editor across twelve bodies/choices and four presets.
It also checks four assigned builds through VS loading. The 4 MB run checks the
launch guard; `--egg-lay` repeats that neutral across all twelve bodies.
Null rendering does not verify appearance.
