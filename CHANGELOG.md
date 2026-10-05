# Changes

## 0.1.17 - 2026-10-05: Normal attack momentum

- Fix the donor normal TransN flag: legacy descriptor macro labels were reversed, so Fox dash attack and Kirby forward smash lost their original movement.
- Regenerate normal travel using the native flag and keep donor size, source clocks and native traction selection.
- Keep the sampled end-to-start velocity at repeated rapid-jab loop boundaries.
- Check flag packing with the MIPS compiler, compare root velocities with original C animation playback, and add live ROM movement/recovery checks.
- Rendered movement/contact acceptance remains pending; Build One retains its Yoshi recipe.

## 0.1.16 - 2026-10-05: Yoshi starter build

- Set default Build One to the requested Yoshi recipe, including all normal attacks, specials, grab/throws and Mario's taunt.
- Document every donor in the play guide and include that guide in the download package.
- Check the initialized recipe in the linked ROM alongside the existing build/host checks; rendered playtesting remains pending.

## 0.1.15 - 2026-10-05: Customizable taunts

- Add an independent TAUNT donor to each build, plus body reset and randomization.
- Share all twelve donor taunt poses, original durations and grab/guard cancel windows across all twelve bodies.
- Preserve Luigi's original 1-damage foot hitbox/path and frames 47-49 active window.
- Retain safe donor audio/rumble/common effects; keep body hurtboxes native.
- Add production selection/cancel, original-C collision, ROM-input and linked-data checks.
- Foreign body scaling, facial/mesh variants and rendered visual acceptance remain pending.

## 0.1.14 - 2026-10-05: Tether grabs and paired throws

- Add 61 donor grab/pull/throw/carry phases and 288 native victim status pairs.
- Retain donor grab hitbox paths/windows, pull offsets, release flags, facing,
  throw descriptors and capture matrices, including animated scale.
- Extend shared attacker poses to grabs/throws; victims retain their own rigs and
  donor-selected native capture/thrown animations. Add native hook/rope/beam/tongue props.
- Run DK cargo movement/jump/fall/damage/toss and Kirby lift/fall/landing mechanics
  on foreign bodies, with donor movement attributes and source timing.
- Keep state isolated by player and fighter generation; use donor sockets for
  catch effects instead of requiring hidden body joints.
- Add original-C matrix/pose, production phase/ownership and linked-ROM checks.
  Rendered contact, body intersections, materials and stage/interrupt acceptance remain pending.
- Build the checked decomp ROM/package; Remix remains unchanged.

## 0.1.13 - 2026-10-04: Shared special animations

- Reserve an Expansion Pak pose bank so the expanded catalog cannot push game
  overlays into video buffers; add link/ROM memory boundary checks.

- Extend the common retargeter to all implemented special adapters on all twelve
  bodies: 40 neutral phases, 99 Up/Down B phases and 16 helpless/landing recovery
  entries. The catalog contains 429 distinct normal/special clips.
- Keep source gameplay clocks and donor collision/travel/socket paths independent
  of pose loops, source body proportions, charge speed and directional flight.
- Fix charge loops using a permanently positive animation countdown: donor cycle
  boundaries now advance Giant Punch charge/store/release and Charge Shot loops.
- Fire stored full Giant Punch after donor startup, and keep frame-zero Up B timing
  by avoiding duplicate borrowed Mario/Luigi playback.
- Restore safe Reflector, Sing, PSI Magnet, Final Cutter and Falcon Punch effects;
  map visual joints by semantic role and retain standard interruption/hitlag cleanup.
- Add standalone native blaster, extending tongue and Stone props and a held
  Charge Shot orb. Preload required assets and keep prop scales outside body rigs.
- Add production selector/loop/recovery tests, original-engine pose/prop comparisons,
  live ROM pose sampling and linked visual-registry checks. Rendered acceptance,
  full voice/color polish, tethers and paired victim choreography remain pending.
- Build and publish the checked decomp ROM; the separate Remix ROM is unchanged.

## 0.1.12 - 2026-10-04: Donor normal mechanics

- Make jab-chain availability, buffering and third/rapid phases follow the donor
  on every original body. Preserve native thresholds, loop/end timing and refresh
  groups; Pikachu repeats jab one and Puff's unused rapid states stay unreachable.
- Add Link down-air's original contact bounce, frame-35 rewind, 30-tick rehit
  timer and fastfall cancellation to borrowed down-air.
- Add Ness bat reflection with source frame-16/22 window, socket/size and native
  projectile/item ownership behavior. Foreign normals suppress body gameplay events.
- Use donor root travel, normal traction/air physics, angled variant availability,
  aerial landing selection and mapped part-intangibility timing. Body hurtbox
  shapes, jump inventory and movement outside attacks stay native.
- Keep donor normal collision scripts valid on bodies missing a corresponding
  joint, including Samus's absent right hand; donor world paths keep the hitbox.
- Expand Training/VS asset caches to 512 entries so all twelve normal donor
  attribute/model files can load without the old cache-full freeze.
- Skip the resource-heavy intro with 4 MB memory so menus can show the existing
  8 MB gameplay requirement instead of overflowing before that guard.
- Keep native release setup for customized grabs. Fix an Egg Lay interruption
  crash by installing the original donor escape-damage descriptors on every body.
- Add production normal callback, source data and linked-ROM checks. Live CPU
  tests pass for all 144 donor/body jab chains, twelve Link bounces/Ness bat
  reflections, editor returns and four assigned VS builds (null rendering).
  Rendered contact/stage/interrupt acceptance and visual/audio polish remain open.
  This milestone is decomp only; Remix is unchanged.

## 0.1.11 - 2026-10-04: Remaining special mechanics

- Add source paths/events/sockets for bombs, eggs, Thunder, Fire Fox, Quick
  Attack, Reflector, PSI Magnet, Sing, Falcon Dive, Final Cutter and Stone on
  all original bodies. Keep native item/weapon/capture mechanics and body hurtboxes.
- Expand to 99 donor clocks and 96 collision/travel/socket phases, including
  Link's common bomb toss: frame-8 release, source hand socket and donor throw values.
- Keep native charge/zip/travel/hold/release timers independently of pose loops;
  merge parallel gameplay streams and stop at pauses. Preserve source hit fields,
  radii, changing sizes, active windows and recovery physics.
- Isolate held egg and Thunder ownership/destruction state from common status
  unions; guard cleanup across damage, capture, Training reset and respawn.
  Preload Pikachu Model for Thunder trails and all selected donor attributes.
- Reflector and PSI Magnet use source field geometry and native ownership/healing
  rules. Sing keeps its sleep collision. Falcon Dive keeps donor catch anchors
  and safe source throw descriptors. Final Cutter keeps its landing beam and
  movement multiplier without shrinking the foreign body. Stone keeps native
  38% US armor, 18-tick minimum and 160-tick timeout and is now selectable.
- Move stage selection into the Expansion Pak arena to accommodate the larger
  gameplay overlay. Add production callback, source geometry, linked-ROM and
  live CPU regression coverage; see the remaining-special-mechanics guide.
- Borrowed special poses/effects and rendered contact/stage acceptance remain
  pending. Decomp only; Remix is unchanged.

## 0.1.10 - 2026-10-04: Spin Attack, Screw Attack and Rest gameplay

- Complete donor collision paths, hit fields and gameplay clocks for Link Spin
  Attack, Samus Screw Attack and Jigglypuff Rest on every original body.
- Preserve Link's grounded spin weapon, expanding attack radii, native lifetime,
  hitlag, ground/air continuation and 40-frame ending. Remove the native wrong
  fighter/weapon pointer call and clean up owned weapons on damaging/reset exits.
  Isolate foreign spin-weapon ownership from common landing/capture status data;
  guard cleanup and move clocks against recycled fighter generations.
- Preserve Samus's separate ground/air movement, multihit/finisher sequences,
  intangible startup, platform/cliff callbacks and donor recovery physics.
- Rest keeps its one-frame 20-damage hit, original radius/knockback, 30-frame
  invulnerability and 250-frame sleep. Landing/edge transitions continue sleep.
- Use donor friction, gravity and speed limits during borrowed specials;
  recovery retains donor attributes and source landing lengths (Link 13 ticks,
  Samus 20, Mario/Luigi 25). Body hurtboxes and jump inventory remain native.
- Add production callback/physics/weapon lifecycle checks and original animation
  matrix checks for all 30 special path phases. Add optional live ROM coverage
  for these three donors, Training reset/editor return and four-slot VS.
  All three passed on all twelve bodies: 72 ground/air starts and 36 editor returns.
- Recheck the complete intro/title boot, Mario Up B, Ness steering/self-launch
  and 1,288 live normal poses on Mario.
- Special animation retargeting and rendered contact/ledge acceptance remain
  pending. Decomp only; Remix is unchanged.

## 0.1.9 - 2026-10-04: Mario/Luigi Up B gameplay

- Add source ground/air Super Jump Punch collision paths and movement on every
  original body. Preserve Mario's opening/multihit/finisher and Luigi's distinct
  25-damage sweetspot, weak continuation, angles and knockback.
- Keep native steering, facing, ground-to-air timing, aerial startup damping,
  opening invulnerability, helpless physics and 25-tick landing recovery.
- Avoid foreign TransN joints; preload donor attributes and isolate steering and
  recovery ownership. Exhaust the body's jump inventory during helpless fall.
- Add native-versus-borrowed callback/physics checks for twelve bodies, four slots,
  both facings and ground/air starts, with interruption and respawn cleanup.
- Add optional live ROM checks for source collision centers/fields, recovery and
  Training reset. Special animation retargeting and rendered acceptance remain pending.
- Live CPU checks passed both donors on all twelve bodies: 48 ground/air starts,
  24 Training resets/editor returns and four assigned VS builds.
- Recheck the full intro/title/menu boot and Ness steering/self-launch on DK.
- Decomp only; Remix retains its previous special coverage.

## 0.1.8 - 2026-10-04: black-screen startup fix

- Fix the opening room exhausting its lower-bank heap before the first frame
  after the normal animation expansion. All nineteen opening scenes now use
  the same separate Expansion Pak arena as Training/VS.
- Add an uninterrupted cold-boot regression through the full intro, title and
  actual Start input into the main menu, with heap bounds and progress checks.
  It passes all nineteen scenes with at least 2,309,952 bytes of heap headroom.
- Recheck Mario's eleven foreign normal donors (1,288 live poses), Training
  return and four assigned builds in VS with three CPUs.
- Verify every linked opening scene calls the Expansion Pak helper. Keep the
  SDK/controller layout and normal animation/gameplay tables unchanged.
- Public ROM assets and the Desktop ROM come from the same checked binary;
  downloaded copies can be tested with the new smoke-test `--rom` option.

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
