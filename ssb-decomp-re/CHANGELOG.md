# Character Lab changes

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
