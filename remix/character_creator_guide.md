# Character Lab on Smash Remix

Character Lab has an original-roster Remix preview, **0.1.2 (2026-10-05)**.
It is a separate ROM built on Smash Remix +EXTRA. Keep **Original 12 Only** on
for the shared donor timing and collision system. Most visible poses still
belong to the body; the [checklist](docs/character-lab-status.md) tracks what remains.
This is a partial port. The [full port matrix](docs/decomp-port.md) lists which
mechanics are implemented and which still need adapters or playtesting.

## Make a build and fight with it

1. Open `remix-character-lab.z64` in your emulator.
2. Open **Settings -> CHARACTER LAB** and choose BUILD 1, 2, 3 or 4.
3. Edit the name, **Body** and attack donors with the native menu controls.
4. **USE BODY FOR ALL MOVES** gives you a native starting point.
5. Change any jab, dash attack, tilt, smash, aerial, grab or throw donor.
6. Neutral Special offers **Body Move** or **Fox Laser**. Up/Down Special
   remain experimental. Mario with Falcon Kick/Pikachu Up B is the first
   regression target; use native body specials for unverified mechanics.
7. Select **TEST IN TRAINING**, then select the preset's Body on the Training CSS.
8. Exit Training, or press Back on its CSS, to reopen the same preset editor.

On the VS or Training character-select screen, open **Player Settings -> Custom
Build** for each player. Choose Off or any saved build for human and CPU slots.
The selected fighter must match the build's Body. All four ports can use builds
independently, including different recipes with the same body.

In Training, press **D-pad Down** to cycle Model Display through **HITBOX**,
**HITBOX+**, ECB and normal rendering. Its **Improved Combo Meter** is enabled by default and includes grabs
and wall bounces. The four unlockable fighters and Item Switch remain unlocked.

## Saved presets

Four presets start enabled with mixed normals; their bodies are Mario, Fox,
Link and Kirby. Names and move selections use Remix's native SRAM serializer.
**TEST IN TRAINING** saves before leaving the editor. Per-port Custom Build
assignments are match settings rather than part of a recipe.

This preview changes the SRAM layout/revision, so older Remix recipes and
settings reset once. Keep emulator saves separate from other Remix versions.
Changing the compiled roster later can change selector indexes.

## What the moves inherit

For original-roster normals, the body keeps native fighter data, hurtboxes,
action callbacks and usually its animation. A separate per-player move clock
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
Jab phases must still exist on the body. Donor traction/air attributes,
followups, Link bounce, Ness reflection and landing callbacks remain pending.

Grab choices borrow donor hitbox events and timing. Throw choices borrow
numeric damage/knockback while preserving body capture, victim statuses and
release choreography. DK skips cargo for a foreign forward throw. Tether reach,
paired animation and complete donor throw choreography remain unfinished.

Fox Laser uses its original firing frames (25 ground / 15 air), repeat flags
and finite recovery (55 / 45). DK and Samus use finite neutral end poses instead
of staying in a charge loop. Body Move restores native neutral behavior. Fox
itself retains its native laser callbacks.

Three Mario-only pose pilots are carried over: Falcon down-air, Fox straight
forward tilt and DK straight forward smash. Broader animation retargeting and
rendered acceptance of these pilots remain pending.

## Expanded roster and experimental specials

Turning off Original 12 Only exposes the earlier expanded-roster creator.
Remix-exclusive bodies retain its legacy normal/special adapters. They do not
have the shared original-roster trajectory fidelity. Original bodies safely
fall back to their own normal when a donor outside the original twelve is
selected. Grab/throw donors stay limited to the original twelve.

Up/Down Special mixing temporarily borrows donor code/resources. Borrowed
phases with original-roster donors use body idle/falling poses instead of taunts, avoiding Mario growth
and taunt displacement. Original-roster donors have separate phase clocks
for recovery/events, respecting frozen dash phases and animation speed.
Pikachu stretching and Fox/Ness recovery pitching are suppressed on borrowed
bodies while their movement callbacks remain active.

Source special collision events/paths and TransN travel are now connected.
Collision placement compensates for body size, and native special physics uses
donor attributes during its callback. The actual body keeps recipe ownership
through the donor compatibility context. These foundations are shared;
directional hitbox rotation, projectile sockets, independent passives and
helpless/landing recovery are not yet a complete port.

Expanded Remix donors retain the earlier finite taunt fallback because their
phase clocks are not yet compiled.

Full special retargeting remains pending. Projectile placement, directional
paths, model changes and capture mechanics still need
work and per-pair playtesting. In particular, check Mario with Pikachu Up B:
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
- `scripts/build_charlab_runtime.py`: freestanding MIPS compilation and ELF relocation import.
- `scripts/verify_charlab_rom.py`: ROM/data checks and production MIPS execution tests.
- `scripts/test_charlab_scenes.py`: optional real-input CPU fixture, isolated saves and null rendering.
- `scripts/build_charlab.py`: asset generation, build, verification and packaging.
- `character_appender.py`: generated source/catalog, owned overrides and menu injection.

Change owned sources, then rebuild. Files under `src/`, `main.asm` and `build/`
are generated; `smashremix/` is a pinned dependency.
