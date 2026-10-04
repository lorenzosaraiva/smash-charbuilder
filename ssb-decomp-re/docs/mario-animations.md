# More donor animations on Mario

> Current coverage: version 0.1.7 extends normal animations to all twelve bodies
> and donors. See [full-roster animations](full-roster-animations.md). The report
> below records the earlier milestone; its packed format has been replaced.

Version 0.1.6, 2026-10-03. This expansion is decomp only. Remix retains the three
earlier Mario pilots. Rendered mesh/contact acceptance remains pending.

## Try it

Open Options -> Character Lab, choose a **Mario body**, and select **Fox, DK,
Luigi or Captain Falcon** for any normal attack row. Test in Training or assign
the build to a human/CPU slot in VS. Training View -> HITBOX shows donor attacks.

All thirteen normal families now have donor poses for those four choices:
jabs, dash attack, forward/up/down tilts, forward/up/down smashes and all five
aerials. Angled tilt/smash variants and the five aerial landing timelines are
included. Falcon/Luigi third-jab poses are included where Mario's existing chain
supports them. This does not add rapid-jab states to Mario.

Good comparisons: Mario + Falcon up air, Fox up smash, DK down smash, Luigi
forward smash, then angled Fox forward tilt and DK forward smash. Compare both
facings and landing early during an aerial. The source catalog's fallback is
used when a donor has no distinct angled or landing animation.

Other donors/bodies, specials, grabs and paired throws still need animation work.
Donor damage, knockback, reach, hit windows, recovery and landing timing keep
using the existing collision/timing system independently of visible posing.
Mario keeps his bone lengths, mesh and hurtbox definitions; larger donor reach
can extend beyond his hands/feet. Native sounds, effects and normal-move physics
remain separate compatibility work.

## Shared conversion and playback

The catalog covers **118 donor/variant entries** through **97 distinct clips**:
the three unchanged float pilots plus 94 new shared compact clips. Resolved
descriptor aliases share data. Every clip uses the existing per-player donor
clock, including restart frames, frozen hitlag and recovery-end clamping.

The converter evaluates the native setup/hidden-joint traversal and descriptor
flags. Source XRotN/YRotN orientations are folded into the mapped root/limb
orientations. Source TransN is detached before FK and remains outside the pose;
this avoids importing actor movement twice. Runtime neutralizes any body
XRotN/YRotN cosmetic channels before writing the converted pose. TopN position,
facing, scale and detached TransN physics remain engine-owned.

World orientations are converted through donor/Mario bind bases. Mario retains
fixed bind translations and unit scales; root translation deltas use the bind
root-height ratio. Visible squash/stretch and accessories are omitted. Missing
mapped DObjs reject the whole write before any transform changes.

The compact format stores 24 Euler rotations as signed 16-bit values at 1/4096
radian resolution and one root translation at 1/16 engine-unit resolution.
Other translations share Mario's bind table. Each frame is **150 bytes**, versus
628 in the original pose/collision pilot; collisions already have their own
independent shared tables. Overflow fails generation. No donor assets, callbacks,
animation-heap allocations or per-player pose buffers are needed at runtime.

The new sampled tables contain **3,766 frames / 564,900 bytes**; the direct
12-by-33 lookup adds 3,168 bytes and the shared bind translations 288 bytes.
This is a bounded Mario expansion. Other bodies should reuse donor curves or a
more compact common rig representation before multiplying this format further.

Measured against v0.1.5: ROM and resident overlay growth **568,912 bytes**, with
**zero BSS growth**. The ROM is **17,761,568 bytes**. Training retains at least
**1,973,152 bytes** of free Expansion Pak heap in the scene regression.

## Verification and remaining acceptance

The build runs the production runtime host checks for all 115 new registry
entries, all frames, nonzero starts, recovery-end clamping, frozen clocks,
independent four-player ownership, scene/body/demo guards, missing joints and
reserved-channel double-rotation prevention. The original three pilots retain
their existing pose/collision tests.

The original C figatree/playback oracle supplies donor poses independently.
`verifyMarioAnimationData.py` reads the actual compiled compact tables and compares
their decoded world orientations and root translations with those source poses.
Maximum permitted matrix-coordinate error is 0.002; root translation error must
be below 0.0313 engine units. This measures compression/retargeting numerically,
not rendered mesh appearance.

Observed maxima: matrix error **0.0006424**, root translation error **0.03125**.

The ROM verifier checks every compact clip byte and all 396 lookup
pointers/counts against the tested host data, alongside source collision data
and N64 CRC checks. Training/VS allocation headroom and scene returns are checked
with an isolated emulator CPU harness using null rendering.

The CPU regression checked **2,082 live compact poses** across representative
normal attacks for all four donors, then returned to each preset's editor and
loaded four differently assigned Mario builds into VS. Ground checks exclude
leg chains after native slope-contour adjustments; aerial checks include all
mapped limbs. This does not establish rendered mesh quality or complete contact
acceptance for every variant. Run `python3 tools/testTrainingScenes.py --mario-animations`
with the Mupen paths described in the [neutral-special guide](neutral-specials.md).

- [x] Four donor rigs, normal families, angled attacks and aerial landings on Mario.
- [x] Shared compact clips and independent gameplay collision paths.
- [x] Native-source/compiled-pose, runtime lifecycle and linked-ROM checks.
- [x] Live ROM poses for all four donors, four editor returns and four-Mario VS loading (null rendering).
- [ ] Rendered limb/mesh quality at both detail levels and both facings.
- [ ] Contact, shields, hitlag, landing and damage-interruption visual acceptance.
- [ ] Remaining donor rigs on Mario, then animation coverage on other bodies.
- [ ] Special, tether and paired throw/victim animations.

Regenerate with `python3 tools/generateCustomAnimations.py`, then run the normal
root build command. The build's vanilla checksum comparison prints `FAILURE`
for this modified ROM; the custom verification checks must pass.
