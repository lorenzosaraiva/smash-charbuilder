# Changes

## Download/version information - 2026-10-03

- Put both ROM and play-package downloads together in the root README.
- Added project version 0.1.0, a last-updated date and each published ROM's date
  and exact source build.
- Documented how to keep these fields current when publishing releases.

## Character Lab on Remix preview - 2026-10-03

- Ported original-roster donor normal values, timing and root-relative collision
  paths through Remix native engine hooks, using the shared Character Lab tables.
- Added grab/throw selections, donor throw values, DK direct foreign throw,
  Body Move/Fox Laser, Mario animation pilots and return from Training to the editor.
- Preserved SRAM presets, human/CPU assignments, native display/unlocks and
  the improved combo meter. Expanded-roster fidelity remains a future task.
- Added checked build/ROM/ZIP packaging and production MIPS execution tests;
  rendered gameplay acceptance remains pending. Older Remix SRAM resets once.
- Updated play/build guides and both feature checklists.

## Training grab combo continuity - 2026-10-02

- Training keeps combo count and damage during capture, cargo carry and throw
  windup, continuing into throw hitstun for native fighters and creator builds.
- Production counter regression tests cover all bodies/slots, recovery and escape,
  empty grabs and scene isolation; linked counter code is verified in the new ROM.
- Updated guides/checklists and recorded a future Remix port assessment. Remix
  gameplay is unchanged; it already has an improved combo meter.

## Full normal donor collision paths - 2026-10-02

- Original paths across all twelve donor/body choices for normal attacks, angled
  variants, weapon/tail attacks, multihits, landing hits and body-supported jab phases.
- One shared descriptor/fallback catalog; direct lookup and trimmed frame tables
  preserve donor reach without per-body trajectory data or new player allocations.
- Engine joint enable/insertion/traversal, extra rotation channels, Luigi translation
  scaling, raw track-length commands and rapid-jab cycles supported by the converter.
- Native playback/matrix checks for all 293 resolved timelines; 396 registry entries,
  repeated loops, foreign bodies and linked ROM bytes verified.
- Updated checklist and new ROM/ZIP. Visible animations remain body-owned outside
  the Mario pilot; in-game acceptance and donor-specific mechanics remain pending.

## Falcon up-air and shared move registration — 2026-10-02

- Falcon up-air follows its original collision path on Kirby and all other bodies,
  preserving damage/knockback phases, active windows, recovery and landing timing.
- Generated donor-move registry replaces individual runtime move branches.
  One donor trajectory serves every body; native verification expands from the
  same move catalog, including multiple attacks from one donor.
- Updated documentation/checklists and checked ROM/ZIP release.

## Donor collision paths — 2026-10-02

- Kirby up-tilt uses its original hitbox path on DK and every other foreign body.
- Falcon down-air, Fox straight forward tilt and DK straight forward smash paths
  now work across bodies; visible retargeted poses remain Mario-only.
- Native engine geometry, both facings, body-size compensation and runtime
  lifecycle checks; checked local ROM/ZIP builds include these tests.
- Updated the roadmap and retained pending in-game acceptance explicitly.

## Combined project repository

- Both creator experiments now live in `lorenzosaraiva/smash-charbuilder`.
- Remix and decompilation main-branch histories are preserved as parents of the import.
- Existing Remix creator edits are included; its dependency's Sonic creator hook
  is stored as a reproducible source override.
- One root README, issue forms, build entry point and release workflow.
- Character Lab ROM and play package are also copied to root `dist/`.
- Python environments stay local and are no longer tracked.

The current Character Lab gameplay is unchanged by this migration. See its
[gameplay changelog](ssb-decomp-re/CHANGELOG.md),
[feature checklist](ssb-decomp-re/docs/status.md), and the
[Remix creator guide](remix/character_creator_guide.md) for each version's behavior.
