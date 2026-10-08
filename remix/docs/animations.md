# Shared Remix animations

Preview **0.1.9**, updated **2026-10-06**.

Original-roster normal attacks now use the decomp's shared donor poses on all
twelve bodies. This includes tilts, smashes, dash attacks, aerials, landing poses
and available jab phases. The three Mario pilots remain unchanged: Falcon
down-air, Fox straight forward tilt and DK straight forward smash.

Existing borrowed special phases and helpless/landing recovery also use shared
poses. Charge/hold loops, transitions and direction-dependent Fire Fox/Quick
Attack presentation use the source clock. Mario/Luigi Up B presentation includes
the steering angle. Changing the body does not require another hand-authored
animation: semantic limb roles and bind orientations retarget the same donor
curves to its native rig.

Timing, collision trajectories, damage and knockback remain controlled by the
existing gameplay layer. The pose does not change the fighter's world position
or source hitbox centers. Missing donor-joint callback fallbacks are suspended
during pose writes and restored afterward, preventing cosmetic bones from
resetting the world root. Native body hurtboxes remain in use. Compact bodies
can still look unusual, and source reach can extend beyond their limbs.

## Memory and builds

The checked decomp generated curves are packed verbatim into a 2,180,944-byte ROM
bank. Only bind rigs/descriptors stay resident. Each of four player ports has a
separate 15,200-byte cache. The native synchronous DMA service loads a clip on
selection changes; repeated frames/loops reuse it. DMA buffers and lengths are
aligned, and no donor animation heap or foreign skeleton is installed.

The bank contains 501 clips. Original neutral, tether/grab/pull, paired
throw/cargo/lift/fall/landing and taunt phase entry points now select these
source clips. Long phases and loops use bounded chunk selection and donor
clocks; geometry remains independent of body proportions. Expanded bodies
keep the earlier Remix path. Rendered mesh and victim alignment acceptance
remains pending.

Build from the root with `tools/build-remix-character-lab.ps1`; generated banks
stay in ignored build directories and the checked ROM/ZIP go into `dist/`.
The decomp ROM is preserved.

## Checks and remaining work

The standard verifier compares packed keys, roots, descriptors and mixed
byte/float rig records with the independently compiled decomp ELF. It executes
the linked MIPS retargeter on every retained clip and all twelve body rigs,
checks all four player caches, and checks world-root/hitbox/clock isolation
including missing-joint callback aliases on all twelve bodies.
Existing collision, movement, special, editor-launch and recovery regressions
remain part of the build.

Optional real-input Mupen checks normally use null rendering. Their CPU results
do not establish rendered mesh/material/contact quality. The listed special
props, native flames/sword effects and safe source visual/audio scripts are now
ported; see [effects and attachments](special-effects.md). Full rendered
acceptance and other actor-specific overlays/materials remain pending.
Native donor part/texture/hurtbox commands remain suppressed on foreign bodies.
Kirby inhale/copy gameplay is available in 0.1.17. Borrowed inhale currently
uses body Idle/Fall with source gameplay clocks; mouth/stretch poses, wind
and copy hats remain deferred. Copied moves use the existing donor pose adapters.

For rendered acceptance, try body + donor combinations with HITBOX/HITBOX+ and
report the phase/input, emulator and ROM version, ideally with a short clip.

The 0.1.5 pose check passes 501 packed clips / 583,853 keys, 164,829 linked-MIPS
joint orientations on twelve rigs, 1,848 special selections, twelve callback-alias
world-root guards and four independent caches. Real-input CPU checks pass
Falcon normals on Mario/Kirby, Kirby normals on Yoshi, Falcon Kick source travel
and both Quick Attack zips/recovery. These checks use null rendering; visible
meshes, special props/effects and rendered contacts remain acceptance work.
