# Character Lab on Smash Remix

Character Lab has an original-roster Remix preview, **0.1.23 (2026-10-09)**.
It is a separate ROM built on Smash Remix +EXTRA. Keep **Original 12 Only** on
for shared donor timing, collision paths and retargeted normal/special poses.
The [checklist](docs/character-lab-status.md) tracks the remaining mechanics and props.
This is a partial port. The [full port matrix](docs/decomp-port.md) lists which
mechanics are implemented and which still need adapters or playtesting.

## Randomize a four-player match

Open **Settings -> Character Lab -> Randomize 4 Builds** and press A.
This replaces and saves **all four builds** while keeping their names. Each
body, normal, special (including Kirby inhale), grab, throw and taunt gets an
independent donor from the original twelve. Repeated bodies/moves are allowed;
Original 12 Only is switched on automatically.

All four builds are enabled and assigned to P1-P4. VS selection opens with
all four bodies ready: connected ports are human players, unused ports are
level-5 CPUs. Rules are **4 stocks, items off, free-for-all**. Press Start and
choose a stage. You can edit the VS player settings before starting.
Use the button again for another roll; the last four recipes persist in SRAM.

Version 0.1.23 protects entrances and native specials from borrowed rapid-jab
clocks. Jab follow-ups retain their donor timing and clear ownership on
interruptions. Rendered randomized entrance/jab recovery acceptance is pending.

Version 0.1.22 protects the actual body model during Link bomb pickup and
pause/unpause, keeping donor timing and bomb ownership. Rendered acceptance
of the reported Yoshi distortion/freeze remains pending.

Quit a paused match with A+B+R+Z. Version 0.1.21 clears donor state before
loading results, including when a borrowed special was still active. CPU checks
cover quitting, returning to VS selection and starting the next match; rendered
acceptance of this exit fix remains pending.

The user confirmed the randomizer works in game. Automated tests cover the
selection/setup path; broader rendered four-controller
acceptance and arbitrary randomized matchups remain pending.

## Make a build and fight with it

1. Open `remix-character-lab.z64` in your emulator.
2. Open **Settings -> Character Lab** and choose BUILD 1, 2, 3 or 4.
3. Edit the name, **Body** and attack donors with the native menu controls.
4. **USE BODY FOR ALL MOVES** gives you a native starting point.
   It also updates Neutral B to the body's explicit donor, keeping native copy for Kirby.
5. Change any jab, dash attack, tilt, smash, aerial, grab or throw donor.
6. Neutral Special offers **your body's fighter name** and all twelve original
   donor choices, including Kirby inhale/copy. Hold B to inhale, then A to spit
   or B/down to copy the held victim's Neutral B. L discards the copy.
   Inhale includes native wind and a discard star; the added mouth overlay is removed. Use A or L to spit a held opponent. Full body/stretch poses and copied hats remain pending. See [neutral controls](docs/neutral-specials.md). Up/Down Special
   remain experimental. Mario with Falcon Kick/Pikachu Up B is the first
   regression target; use native body specials for unverified mechanics.
   A ground-only donor such as DK Down B does nothing in the air; land to use
   its grounded attack. It never substitutes the body's original Down B.
7. Select **TEST IN TRAINING**. The Training CSS opens with your build's Body
   selected and a native Mario dummy; choose a stage and start.
8. Exit Training, or press Back on its CSS, to reopen the same preset editor.

On the VS or Training character-select screen, open **Player Settings -> Custom
Build** for each player. Choose Off or any saved build for human and CPU slots.
The selected fighter must match the build's Body. All four ports can use builds
independently, including different recipes with the same body.

In Training, press **D-pad Down** to cycle Model Display through **HITBOX**,
**HITBOX+**, ECB and normal rendering. Its **Improved Combo Meter** is enabled by default and includes grabs
and wall bounces. The four unlockable fighters and Item Switch remain unlocked.

Fully charged **DK Neutral B** blinks while the punch is stored. **Samus Down B**
turns your body into a body-colored Morph Ball, including the small original hop;
one input still creates one bomb. Visual acceptance of the local 0.1.16 fix is pending.

## Saved presets

Four presets start enabled with mixed normals; their bodies are Mario, Fox,
Link and Kirby. Names and move selections use Remix's native SRAM serializer.
**TEST IN TRAINING** saves before leaving the editor. Per-port Custom Build
assignments are match settings rather than part of a recipe.

The earlier initial preview changed the upstream Remix SRAM revision. This
neutral expansion preserves existing Character Lab presets: full neutral choices
use spare creator-options bytes while the original recipe bit layout stays fixed. Keep emulator saves separate from other Remix versions.
Changing the compiled roster later can change selector indexes.

## What the moves inherit

Remix 0.1.16 draws borrowed fighter parts in the native fighter pass and
restores its one-cycle state afterward, addressing noisy tether textures and
white stage layers. Beam materials advance once per frame. Native material
submission and exit state have regression checks; rendered acceptance of this
fix remains pending.

Samus Bomb creates one bomb per Down B input, even on DK's body. Landing or
entering the air cannot replay that spawn. A new input creates a new bomb;
aerial availability follows the selected donor, so DK can use Samus Bomb in
the air. DK Down B has two slaps in one native cycle; tap B again during the move to
request another cycle. Samus Bomb becomes a body-colored donor Morph Ball on
frames 3-48, follows the original hop and restores the selected body on exit. Samus tether includes its native
glow alongside the donor beam parts. These changes pass CPU checks; visible
alignment and broader interruption acceptance remain pending.

For original-roster normals, the body keeps native fighter data and hurtboxes.
Normal gameplay callbacks follow the chosen donor. Shared donor poses retarget onto its native rig. A separate per-player move clock
supplies donor startup, active frames, hitbox clears and total recovery. It
advances with the native animation update, so hitlag pauses it too.

Attack events supply donor damage, radius, angle, knockback parameters, element
and other numeric collision values. Donor collision centers follow original
root-relative trajectories, compensated for body size. They no longer depend
on whatever limb the body happens to animate. The engine still owns contact
detection, staling, hit records and swept collision history.

The tables use vanilla US donor values, matching Character Lab. Remix balance
changes and enabled gameplay modifiers can affect the resulting battle. This
ports donor root movement too, including Fox dash and Kirby forward smash.
Jab chains, buffering/rapid phases, Link down-air bounce, Ness bat reflection,
donor traction/air attributes, angle availability and landing behavior follow
the source. See [normal mechanics](docs/normal-mechanics.md) for jab controls and
the rendered contact checks still pending.

Grab choices use donor reach, pull timing and source tether/tongue props.
Forward/Back Throw choices use donor attacker/victim sockets, facing, release
flags and numeric damage/knockback. DK Forward Throw enters cargo; use movement,
jump and throw inputs to carry/toss. Kirby Forward Throw lifts, falls and
releases on landing. Victims retain native Remix animation rigs and parent
mapping. Expanded-roster pose fidelity remains pending.

**Taunt** selects any original donor. Press L during play. Donor poses,
duration/cancel flags, safe effects and sounds follow the source. Mario grows
and shrinks the selected body; Luigi keeps his one-damage hitbox at frames
47-49. Interruptions restore growth. Old presets default Taunt to Body.
See [grab, throw and taunt guide](docs/paired-grabs-and-taunts.md).

The eleven other original neutral donors use the shared source
clock and phase poses on foreign original bodies. Projectiles keep their donor
resources and native flight/contact callbacks. Giant Punch and Charge Shot
support B/A release, Z/roll storage, full charge and interruptions. Boomerang
keeps one outstanding weapon and its empty/catch phases; Egg Lay keeps source
capture/release anchors and native egg damage/escape. Selecting the body's name
restores native behavior. See [neutral controls and limits](docs/neutral-specials.md).

All shared normal poses now retarget on twelve original bodies. The three
Mario pilots (Falcon down-air, Fox straight forward tilt and DK straight forward
smash) remain unchanged. Supported borrowed specials and recovery use the same
ROM-backed catalog. Cutter sword/trails, Stone replacement, Falcon flames,
blaster/tongue props and the charging orb now use source clocks and owned
cleanup; see [effects](docs/special-effects.md) and [animations](docs/animations.md).
Broader rendered acceptance remains pending.

## Expanded roster and experimental specials

Turning off Original 12 Only exposes the earlier expanded-roster creator.
Remix-exclusive bodies retain its legacy normal/special adapters. They do not
have the shared original-roster trajectory fidelity. Original bodies safely
fall back to their own normal when a donor outside the original twelve is
selected. Grab/throw donors stay limited to the original twelve.

Up/Down Special mixing temporarily borrows donor code/resources. Borrowed
phases with original-roster donors retarget the source pose onto the body.
Native status setup still uses safe idle/fall assets before the shared pose is applied. Original-roster donors have separate phase clocks
for recovery/events, respecting frozen dash phases and animation speed.
Pikachu stretching and Fox/Ness recovery pitching are suppressed on borrowed
bodies while their movement callbacks remain active.

Source special collision events/paths and TransN travel are now connected.
Collision placement compensates for body size, and native special physics uses
donor attributes during its callback. The actual body keeps recipe ownership
through the donor compatibility context. Fire Fox directional hitboxes, donor
Reflector/Magnet volumes, source projectile sockets, independent passives and
donor helpless/landing clocks are connected. Link held-bomb throws retain donor
timing, values and release sockets. Falcon Dive uses the donor attacker socket
and frame-16 release while keeping native Remix victim offsets. Their rendered
contacts, interruptions and visual attachments still need playtesting.
Missing-joint fallbacks are suspended during native status setup so animation
initialization preserves the body's world-root position. Foreign body-part
commands remain suppressed; the supported props use separately owned effect objects.

Expanded Remix donors retain the earlier finite taunt fallback because their
phase clocks are not yet compiled.

Rendered special props/effects and retargeting acceptance remain pending. Projectile placement, directional
paths, model changes and capture mechanics still need rendered acceptance.
In particular, check Mario with Pikachu Up B:
first dash, direction change for a second dash, recovery, interruption and
landing. The body should keep its size and finish at the position it moved to. Original-roster
normals use compiled data without consuming donor-file cache slots; legacy
expanded normals and specials keep the bounded pre-match cache.

## Build and verify

From the repository root on Windows/WSL:

```powershell
.\tools\build-remix-character-lab.ps1
```

See [building.md](../docs/building.md) for dependencies and the original ROM.
The command generates assets, compiles the shared runtime, assembles, checks
production code and packages `dist/remix-character-lab.z64` and `.zip`. It copies
the ROM to the requested Desktop ROM folder as `smash-character-lab-remix.z64`.

Automated checks cover actual compiled MIPS routines, linked bytes, tables and
CRC. They do not replace an emulator playtest of visuals, input and contact.
Report body, donor, move, emulator, enabled Remix settings and source commit.

## Implementation map

- `extra_imports/CharCreatorMenu.inc`: native Settings pages and SRAM fields.
- `extra_toggles/css/CharCreator.asm`: human/CPU preset assignments.
- `extra_imports/CharCreator.asm`: recipe lookup, resource cache and special dispatch.
- `extra_imports/CharLab.asm`: native engine, parser, clock, collision and Training hooks.
- `extra_imports/CharLabRuntime.c`: shared donor runtime with the native Remix ABI.
- `extra_imports/CharLabMovement.c.inc`: donor normal/special travel, attributes and source collision placement.
- `extra_imports/CharLabSpecials.c.inc`: independent state, source sockets/volumes and donor recovery.
- `extra_imports/CharLabVisuals.c.inc`: source visual/audio clocks, attachments and cleanup.
- `extra_imports/CharLabVisuals.inc`: private pre-match effect resources.
- `scripts/generate_charlab_visuals.py`: source prop/audio/effect imports.
- `scripts/test_charlab_visuals.py`: linked-MIPS timing, placement and ownership checks.
- `scripts/generate_charlab_specials.py`: reviewed callback imports and borrowed-only native bridges.
- `scripts/build_charlab_runtime.py`: freestanding MIPS compilation and ELF relocation import.
- `scripts/verify_charlab_rom.py`: ROM/data checks and production MIPS execution tests.
- `scripts/test_charlab_special_adapters.py`: steering, recovery, ownership, volume and native fallback regressions.
- `scripts/test_charlab_scenes.py`: optional real-input CPU fixture, isolated saves and null rendering.
- `scripts/build_charlab.py`: asset generation, build, verification and packaging.
- `character_appender.py`: generated source/catalog, owned overrides and menu injection.

Change owned sources, then rebuild. Files under `src/`, `main.asm` and `build/`
are generated; `smashremix/` is a pinned dependency.
