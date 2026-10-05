# Normal animations on all twelve bodies

Introduced in version 0.1.7; current version 0.1.12, updated 2026-10-04. This expansion is decomp only; the separate
Remix preview retains its previous animation coverage.

All twelve original donors now supply normal attack poses to all twelve bodies.
Choose any Body and change a normal donor in Character Lab, then Test in Training.
Try Kirby + Falcon Up Air, DK + Kirby Up Tilt, or Mario + Samus Up Smash.
Enable Training's HITBOX view to compare the visible motion and donor reach.

## Coverage and limits

The shared descriptor catalog resolves 293 distinct clips and all 396
donor/variant entries: jabs, dash attacks, tilts, smashes, five aerials, angled
variants, aerial landings and donor third/rapid jab phases. Empty
rapid start/end descriptors remain empty. Donor chains now work independently of
body support; see [normal mechanics](normal-mechanics.md). Matching body/donor attacks remain native.
The three established Mario float pilots stay unchanged.

All normal hitbox paths, sizes, damage, knockback, active frames and recovery
continue to use the independent original-source collision catalog and donor
clock. Hitlag freezes that clock and pose together. Cosmetic motion does not
rescale or attach hitboxes to the body's limbs. A small body performing a long
donor kick may visibly fall short of its hitbox; preserving donor gameplay reach
is the current policy. Body hurtboxes remain native.

Each skeleton has an explicit 24-role map for root, pelvis, chest, head, arms and
legs. Bind-normalized donor world rotations are reconstructed on the body's
native hierarchy. Bone lengths, meshes and bind scales are retained. Kirby and
Jigglypuff merge pelvis/chest and neck/head roles; head takes priority where
roles share a physical joint. Pikachu also shares neck/head and hand/grip roles.
Optional joints absent from the initialized body are skipped; missing required
joints reject the whole pose and increment the validation counter.

Unmapped ears, tails, hats and weapon/capture attachments retain native local
bind poses and follow their posed parent. Normal attacks do not add donor meshes or weapons.
Donor animated squash/stretch is omitted from cosmetic retargeting; it remains
included in independently evaluated collision geometry. This is a general
retarget, with mesh-specific polish and rendered acceptance still pending.

Version 0.1.13 extends this catalog to special startup, charge loops, transitions,
release and recovery. See [special animations](special-animations.md). Special
props are separate effect objects; native body proportions and donor gameplay
paths stay independent. Tethers, paired victim choreography and Kirby copy are
still outside this milestone.

## Shared data and playback

`generateCustomAnimations.py` retains the three pilots and invokes
`generateSharedAnimations.py`. `sharedAnimation.py` samples native donor tracks,
respects descriptor flags/reserved rotations, and emits local Euler curves.
Each sparse key uses one unsigned frame byte and two signed-angle bytes,
quantized at 4096 units per radian. Curve descriptors and channel bindings are
deduplicated globally. Root displacement is stored at 4096 units per donor
root bind height and multiplied by the body's root bind height at playback.

The shared catalog uses 266,244 scalar keys and 1,022,744 data bytes before
linker alignment, replacing the earlier Mario-only packed tables. Source FK,
bind-normalized orientation deltas and body FK use bounded stack arrays; no
new animation heap or persistent per-player pose buffer is allocated.
The 0.1.7 linked ROM was 18,219,824 bytes, 458,256 bytes larger than 0.1.6.
The common overlay ends at 0x80290100; Options BSS ends at 0x802efe40.
Common BSS decreases by 16 bytes; Training/VS retain their upper-bank heap.
TopN position/facing/scale and detached TransN physics are preserved. Cosmetic
XRotN/YRotN are neutralized after their donor contribution is reconstructed.

Playback uses the existing owned normal clock, including frozen hitlag,
nonzero restarts, landing transitions and completion. Genuine rapid-jab curves
retain a first cycle and loop their steady cycle; fallback jab loops use their
resolved source period. Original C playback confirms that every joint repeats
through successive steady cycles. Status changes, scene changes, previews, special move
pointers and unassigned players retain the existing guards.

## Verification

The portable build runs production host lifecycle checks, original-engine
animation/collision comparisons, compiled runtime pose comparisons and linked
ROM verification. `verifySharedAnimationData.py` runs the actual C retargeter
with the engine's original inverse-trig routines, then compares every
clip/frame/body against independently evaluated original donor poses.

- 293 native timelines and 2,519,424 scalar samples match original C playback.
- 3,626,238 runtime joint-world orientations cover every clip on all twelve bodies.
- Maximum world rotation matrix error: 0.0007014.
- Maximum cosmetic root translation error: 0.0542882 engine units.
- Maximum stored scalar interpolation/quantization error: 0.0003129 radians.
- Collision checks retain all 396 entries and 125,664 positions over every body
  size and both facings; maximum position error is 0.0002441 engine units.

`verifyCustomMoveRom.py` compares shared key/curve/root bytes, source and body
rigs, every relocated clip pointer and all registry entries with the checked
host build. It also checks gameplay tables, code inclusion and N64 CRC.

After a checked build, optional `python3 tools/testTrainingScenes.py
--roster-animations` uses an isolated Mupen64Plus configuration and real input
handlers. It checks live ROM joint orientations, every foreign donor/body pair,
Training/editor returns, four assigned VS builds and Expansion Pak heap bounds.
It uses null rendering: these checks do not establish rendered mesh quality or
actual hit/contact acceptance. See [status.md](status.md) for outstanding work.

The 0.1.7 ROM passed the all-body CPU sweep: 132 foreign donor/body pairs,
15,248 live pose samples, twelve returns to the same editor and four assigned
human/CPU builds in VS. Minimum measured Training heap headroom was 1,971,044
bytes. The mode samples normal families per body and at least one normal per
foreign pairing; exhaustive clip/frame coverage comes from the host oracle.
The 4 MB launch guard also passed: Test in Training stays in the editor.

Version 0.1.8 moves all nineteen opening movie heaps to Expansion Pak memory
to fix a cold-boot allocation overflow before the first intro frame. The
[boot and download notes](startup-and-downloads.md) cover the regression and
byte-identical release copies.
