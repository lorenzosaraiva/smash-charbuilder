# Changes

## 0.1.7 - 2026-10-04: normal animations for everyone

- Decomp: all twelve donor normal catalogs now animate all twelve bodies, including
  angled variants, aerial landings and body-supported third/rapid jab phases.
- Share 293 compact donor clips and twelve skeleton maps instead of storing every
  body/donor combination. Preserve body meshes, bone lengths and bind scales;
  collapse shared semantic joints on compact rigs and retain native accessories.
- Keep the three established Mario pilots; normal hitbox trajectories, damage,
  knockback and donor clocks remain independent of cosmetic poses.
- Compare actual runtime output for every clip/frame/body against original C
  playback: 3,626,238 joint-world orientations, maximum matrix error 0.0007014.
- Update generators, runtime guards, source/ROM checks and play documentation.
- Live ROM CPU checks: all 132 foreign donor/body pairs, 15,248 pose samples,
  twelve Training/editor returns and four assigned VS builds. Minimum measured
  Training heap headroom is 1,971,044 bytes.
- Specials, tethers, paired throws and rendered full-roster acceptance remain
  pending. This expansion is decomp only.

## 0.1.6 - 2026-10-03: more Mario donor animations

- Decomp Mario now performs Fox, DK, Luigi and Falcon normal attacks, including
  angled variants, aerial landing poses and supported Falcon/Luigi third jabs.
- Share 94 compact clips across 115 new move variants; retain the three existing
  pilots. Donor collision values/timing remain independent of the visible pose.
- Fold reserved donor rotations into the mapped rig and clear body cosmetic
  channels to prevent double rotation; preserve TopN/facing/TransN physics.
- Add native-source world-orientation checks, complete compact runtime lifecycle
  checks and linked-ROM clip/registry verification. Rendered acceptance remains pending.
- ROM CPU checks pass for four Mario donor presets, 2,082 live compact poses,
  editor returns and four differently assigned Mario builds in VS.
- Update guides/checklists and rebuild the decomp ROM. Remix unchanged.

## 0.1.5 - 2026-10-03: donor special paths and movement

- Decomp: add generated safe event scripts and donor collision paths for 20 phases covering DK Up B, Mario/Luigi Down B, all Falcon Kick phases and Ness Up B. Original damage, radii, knockback, flags and collision timing follow the source independently of visible body poses.
- Falcon Kick follows original root movement/rotation through its native ground/air/landing/bound callbacks. DK spin/Tornado/Ness aerial physics read donor attributes; foreign Tornado state is isolated and resets on landing/respawn.
- Fix foreign Falcon Kick crashing when a placeholder pose has no TransN joint; donor movement bypasses the missing joint and stores slope-transfer angles independently.
- Ness PK Thunder spawns from its original donor socket. Its self-launch clock follows the native 28-tick action timer, keeping the nine-frame looping pose from shifting collision/recovery events.
- Add original-engine geometry/movement/socket comparisons, all-body/four-slot/both-facing helper checks, and linked-ROM pointer/packed-field verification. Emulator CPU tests pass across all twelve bodies for grounded/aerial spin, Tornado B-tap rise, Kick travel and Ness steering/controlled self-contact/recovery, plus editor returns and four-slot VS.
- Full body animation retargeting, other Up/Down B donor paths/effects and rendered contact/interruption acceptance remain pending. These changes are decomp only; Remix is unchanged.

## 0.1.4 - 2026-10-03: special timing and PK Thunder freeze fixes

- Decomp: borrowed Up/Down B phases now use 96 original source durations/loop boundaries and an independent event clock. Temporary body idle/falling poses replace repeated body specials and their unrelated root movement. Native matching-body specials retain their original implementation.
- DK Down B uses the original 3-frame startup, 34-frame slap cycle and 5-frame recovery. All four hitboxes activate on cycle frames 16-17 and 26-27, with donor positions, damage and knockback. B taps queue the next complete cycle; ending, hitlag and ground/air transitions follow the phase state.
- Fix Falcon + Ness Up B freezing in PK Thunder: preload Ness's model file for wave/trail effects as well as weapon/motion files. Foreign bodies keep Thunder trail data in separate per-player storage instead of their native passive union.
- Add host clock/state tests, linked source-table checks and original animation/matrix validation for DK's slaps. ROM CPU smoke tests cover single/repeated slaps and Ness startup/hold/expiry/recovery across all twelve bodies. Null video does not verify rendered appearance.
- Up/Down B remain experimental beyond these fixes: full donor collision paths, weapon sockets, movement/effects and rendered acceptance still need further work. Matching donor animations remain a later milestone. Remix is unchanged.

## 0.1.3 - 2026-10-03: remaining neutral donors and Training loading fix

- Decomp: add Falcon Punch, Pound, Giant Punch, Charge Shot, Boomerang and Egg Lay on all original bodies. All eleven non-copy neutral donors are now selectable alongside Body Move.
- Preserve source melee hitboxes/knockback/timing, ground travel and aerial boosts. Add independent charge/store/release state, native boomerang return/catch and Yoshi capture/egg handoff without borrowing another body's passive union.
- Fix the Test in Training freeze: full-roster preview resources overflowed the original lower-bank heap. Training/VS selection and matches now use a separate Expansion Pak arena. The ROM requires 8 MB RDRAM; the editor displays this and blocks launching tests/VS with only 4 MB.
- Check all 30 donor phases against original animation playback/matrices and all foreign bodies/four slots against the actual adapters. Linked-ROM checks include every phase pointer and packed source hitbox field.
- Emulator CPU smoke tests exercise the full Training launch/return flow across twelve body/neutral choices, four presets, a four-slot VS match and the 4 MB launch guard. Borrowed Egg Lay initializes captured physics from the donor path, avoiding missing body sockets, and preloads native egg effects. These tests use null rendering; visual acceptance remains pending.
- Visible neutral animations still belong to the body. Samus's held charge orb, donor effects/voices and exact captured-victim rotation remain pending, along with rendered contact/reflect/absorb acceptance. New adapters remain decomp only.

## 0.1.2 - 2026-10-03

- Decomp: add Mario Fireball, Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire to Neutral B, alongside Body Move/Fox Laser.
- Borrowed projectiles use native weapon behavior, donor spawn positions and original firing/recovery timing on every original body. Landing/edge transitions preserve progress and prevent duplicate shots.
- Add all-body/four-slot adapter tests, original animation/matrix spawn checks and linked-ROM verification. Rendered gameplay acceptance remains pending.
- Publish a new Character Lab ROM/package; new choices are not yet ported to Remix.

## 0.1.1 - Remix borrowed-special pose/timing fix - 2026-10-03

- Replaced borrowed original-roster Up/Down B taunts with body idle/falling poses. Mario no
  longer uses his growing taunt or its root displacement for these moves.
- Added independent original-roster donor phase clocks, including frozen dash
  phases, animation speed, loops and ground/air continuation frames.
- Suppressed Pikachu Quick Attack stretching and Fox/Ness recovery pitching on
  foreign bodies; donor movement callbacks remain active.
- Added production MIPS regressions for pose selection and transform guards on
  all twelve bodies/four ports, Quick Attack recovery and its second-dash event.
- Preserved finite legacy poses for expanded donors without compiled phase clocks.
- Borrowed specials still need rendered playtesting; full donor poses, special
  hitbox paths, projectiles and paired/capture mechanics remain unfinished.

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
