# Character Lab changes

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
