# Character Lab changes

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

- Mario now performs Fox, DK, Luigi and Falcon normal attacks, including angled
  variants, aerial landing poses and supported Falcon/Luigi third jabs.
- 94 shared compact clips cover 115 new variants alongside the three unchanged
  pilots. Hitboxes, damage, knockback, timing and landing windows retain their
  independent source catalog.
- Handle source hidden/reserved rotation channels, neutralize body cosmetic
  channels and preserve native TopN/facing/detached TransN physics.
- Check actual compiled poses against original C playback/world orientations;
  test all new runtime frames/ownership/guards and linked ROM bytes/pointers.
- ROM CPU checks pass for four Mario donor presets, 2,082 live compact poses,
  editor returns and four differently assigned Mario builds in VS.
- Updated docs and play package; rendered mesh/contact acceptance remains pending.

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

## 0.1.2 - 2026-10-03: projectile neutral specials

Add Mario Fireball, Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire to the Neutral B selector and randomizer. Foreign bodies keep their own neutral poses, use donor firing/recovery clocks and donor spawn geometry, and call the native projectile constructors. No donor fighter status or passive union is transplanted. Matching donor bodies keep their native move.

Ground/air transitions continue the clock without a second shot. Resource preload covers fireballs, jolt surface animation, PK Fire spark/pillar and particle banks. Actual adapter tests cover all bodies/four player slots, native fallbacks, transitions, interrupted actions and allocation failure. Native animation/matrix and linked-ROM checks validate all eight source definitions. Rendered gameplay/contact acceptance and retargeted animations remain pending; charge, return/catch, melee/movement and capture neutrals still need dedicated adapters. Kirby copy is excluded.

## Training grab combo continuity - 2026-10-02

- Training preserves the existing combo count and damage through grabs, cargo
  holds and throw windup, then continues through throw hitstun until recovery.
- Applies to native and creator fighters. Bare grabs add no hit or damage; actual
  hitstun flags, throw behavior and other scenes retain their existing handling.
- Automated production counter tests cover all bodies, four slots, hold/release,
  escape/recovery, independent counters and non-Training resets. The built ROM
  includes the verified counter update; in-game acceptance remains pending.

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

- Falcon up-air trajectory on Kirby and every foreign original-roster body;
  original radii, 16 damage, angle phases, hit groups, active/recovery and landing
  timelines retain donor handling. Visible animations remain the body's own.
- Generated donor-move registry handles all five supported attacks and Kirby
  up-tilt aliases. Adding a donor path requires no body-specific runtime branch.
- Native oracle calls and translated/facing checks are generated for the catalog;
  donor models are shared when several moves use the same fighter.
- Compiled data/registry pointers are checked in the ROM; runtime checks cover
  all foreign bodies and landing transitions. In-game acceptance remains pending.

## Donor collision paths — 2026-10-02

- Kirby up-tilt collision trajectory on all eleven foreign original-roster bodies,
  including the selected body's three up-tilt variants when applicable.
- Shared donor-relative collision layer; Falcon down-air, Fox straight forward
  tilt and DK straight forward smash trajectories now work across bodies too.
- Donor sizes, event windows, damage/knockback and recovery stay on the existing
  attack clock. Collision updates preserve hit records and swept-position history.
- Body animations remain native outside the three existing Mario pose pilots.
- Geometry is checked against original native playback/matrices, including target
  size, position and both facings. In-game acceptance remains pending.

## Next release — repository setup

- Newcomer README, feature checklist, play/build guides and release instructions.
- One build command that verifies the ROM and creates a play package under `dist/`.
- Automatic build/release workflow for pushes to `main`, manual runs and `v*` tags.
- Fixed download filenames, source commit information and SHA-256 checksums.
- Compiler emulator setup keeps verified compatibility libraries locally on Ubuntu 22.04.

## Current gameplay build

- Training tests return to the same build's character editor (`62f65219e`).
- Neutral B can select Body Move or Fox Laser. Foreign-body lasers use a finite
  firing action; DK no longer runs his charge loop underneath a laser.
- DK skips cargo carry when another fighter's forward throw is selected (`8cb8b29bf`).
- Three Mario animation pilots: Falcon down air, Fox straight forward tilt,
  DK straight forward smash (`ad41465b1`). Numeric verification passed; visual review pending.
- Original donor normal-attack timing, hitbox values and knockback, plus mapped
  grab timing and numeric forward/back throw customization.
- Four presets, human/CPU assignments in VS, Training HITBOX view, native menu
  styling, unlockable fighters and Item Switch.

For remaining work and limitations, see [the checklist](docs/status.md).
