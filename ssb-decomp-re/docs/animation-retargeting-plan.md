# Next step: donor animations on custom bodies

Status: Mario now has Fox/DK/Luigi/Falcon normal attack poses, angled variants and
aerial landings through shared compact clips. Native-source geometry/orientation,
runtime lifecycle and linked-ROM checks pass. Rendered acceptance remains pending.
The user requested this bounded Mario expansion while visual review continues.
See [current coverage](mario-animations.md) and the [historical pilot](animation-retargeting-pilot.md).
Gameplay checkpoint: `c4cf93a87` (donor collision parameters, normal/grab timing and landing windows), following `290cffca3` (grab/throw donors) and `06f98fe70` (normal roster, player assignments, training HITBOX and unlocks).

The [collision trajectory milestone](collision-trajectories.md) now has complete
normal coverage and automated checks. Continue visible animation coverage and
rendered comparison. All normal donor paths now work
on every foreign body, including angled variants and body-supported jab phases.
Mario animation coverage has expanded; its rendered acceptance remains pending. The current checklist order is
collisions/timing, animations, neutral specials excluding Kirby copy, then tethers
and paired capture/throw mechanics.

## Intended result

A preset's selected body visibly performs the selected donor's normal attack. Its animation, collision windows and recovery share the existing donor frame clock. The body's mesh, textures, playable identity and initialized skeleton remain its own.

The first playable milestone is **Mario performing Captain Falcon's down-air**, followed by **Mario performing Fox's forward tilt** and **Mario performing Donkey Kong's forward smash**. These cover an aerial, a tilt and a smash, and expose differences in skeleton axes, proportions and attack reach. The current ROM remains the comparison baseline.

## Constraints and geometry policy

- Retarget animation data through explicit skeleton maps. Keep native body status functions and valid body joint references; do not execute a donor's fighter-specific status implementation or attach its raw joint-indexed animation table to the body.
- Keep the donor damage, angle, knockback, hitbox dimensions and event timestamps established in the current build. Retargeting must not restart or rescale that timeline.
- Preserve the body's bone lengths and mesh proportions for the first implementation. Convert donor movement into the body's joint coordinate bases, rather than copying Euler rotations between differently oriented joints. Unmapped accessories retain a valid body pose.
- Original collision reach is a separate requirement from visual similarity. Even a correctly retargeted animation changes hand/foot positions when the bodies have different limb lengths. Plan to evaluate donor collision trajectories from normalized donor pose data and place them relative to the fighter's world root. This keeps gameplay reach independent of body proportions. Expect possible visible separation between a small body's limb and a long donor hitbox; precise visual alignment can later use constrained limb posing.
- Separate cosmetic joint motion from locomotion. Reserved TopN/TransN/XRotN/YRotN channels, root scale, facing and stage position require explicit handling. Importing animation data must not accidentally move the fighter, alter facing or apply root displacement twice. Donor physics adapters remain a separate milestone.
- Bound and isolate all runtime pose state for each of the four players. A missing or unsupported animation falls back to the body's animation and reports a diagnostic counter while preserving the existing collision timeline.

## 1. Audit animation representation and skeletons

Trace the actual US data before selecting the runtime format:

| Area | What to establish |
| --- | --- |
| `src/ft/ftmain.c`, `ftMainSetStatus` | Animation selection/loading, body pose resets, figatree heap lifetime, descriptor flags, status changes and landing/restart paths. |
| `src/ft/ftparam.c`, `ftParamUpdateAnimKeys` | Per-joint playback, translation scaling, render/collision transform invalidation and the safe point to apply a retargeted pose. |
| `src/ft/ftanim.c`, `src/sys/objanim.c` | AObjEvent16/32 command semantics, interpolation, looping, end behavior and frame-zero behavior. |
| `src/ft/ftmanager.c` | Animation heap sizing and allocation limits; avoid loading a larger animation into a body-sized heap. |
| `src/relocData/*Anim*.c`, `*Model.c`, `*Main.c` | Bind transforms, hierarchy, joint axes, animation pointer-table order, body scale, translate scales and weapon/capture sockets. |
| `src/ft/ftcustommove.c.inc` | Donor clock, script timing, semantic hitbox joints and per-player ownership. |
| `src/gm/gmcollision.c` | Transform order and conversion of local hitbox coordinates into world positions. |

Produce a read-only audit tool and a mapping report. The current eleven semantic collision locations plus GrabPoint are not a complete animation rig: add explicit pelvis, shoulder, upper/lower arm, hip, thigh, shin and attachment mappings as required by the source skeletons. Record unsupported channels instead of silently assigning them to an unrelated bone.

## 2. Compile reusable donor pose data

Build a host-side converter for the three initial donor animations. Decode their native interpolation and bind transforms, then express the animated movement in a documented semantic rig. Keep the donor's timing and original collision-joint transforms available for collision trajectory evaluation.

Prefer shared donor curve/keyframe data plus twelve body rig maps over dense tables for every body/donor/frame combination. Measure ROM size, overlay memory, pose-buffer bounds and per-frame cost before expanding. The source audit determines whether the pilot should evaluate curves directly or use bounded sampled poses; choose the format after those measurements.

Validation must compare the decoded donor poses with native engine playback at frame zero, startup, each hitbox phase boundary, final active frame and recovery end. Test native interpolation and matrix conventions directly, including signed coordinates and rotations. A comparison with the converter itself is insufficient.

## 3. Integrate playback with the donor clock

Select the normalized animation together with the existing move definition. Reuse that move's frame clock for visual playback and collision trajectories, including hitlag, nonzero restart frames, loop periods and landing transitions.

The candidate integration point is in `ftMainPlayAnim`, after native animation-key processing and before fighter-part transforms are updated. Verify the ordering during the audit: the donor clock currently advances after the transform-update call, so retargeting may require moving that advance before pose application. Each animation update must advance the clock exactly once.

Apply the donor pose to valid target DObjs, retaining their bind translations/proportions and converting rotational deltas through the target joint bases. Invalidate the engine's cached transforms before rendering and collision calculations. Clear retargeting state when the fighter changes status, takes damage, lands, is recreated, or enters a scene where presets do not apply. Preserve separate state when two players share a preset or body.

For original collision trajectories, evaluate the source skeleton numerically and transform its local hitbox centers into the selected fighter's world frame before the attack-position update. Preserve hit groups, refresh behavior and swept collision history; changing the visible pose must not create extra hits or erase previous positions. Account explicitly for donor/body size and scaled-position commands.

## 4. Prove the three-move milestone in RMG-K

Use Training HITBOX and VS with human/CPU assignments. Compare the custom body and vanilla donor on a flat stage with the same facing and root position. Check both facing directions and the complete move, including recovery.

Required acceptance checks:

- Mario visibly reproduces the donor strike on all three pilot moves, with readable limbs and a valid mesh.
- Hitbox centers follow the donor trajectory in the common world frame, with a documented numeric tolerance; start with at most one engine unit per coordinate for compiled samples. Sizes, knockback and creation/clear frames remain unchanged.
- Startup, active duration, recovery and aerial landing windows match the existing donor timing. Hitlag freezes pose and collision progression together.
- Hit, shield contact, miss, landing during an aerial, damage interruption and repeated inputs leave no stuck pose, stale hitbox or stale animation pointer.
- Two players using the same body with different donors, shared presets, CPU slots and a four-player match retain independent pose state.
- Vanilla/unassigned fighters, donor-equals-body choices, demos and unrelated scenes retain their normal behavior.
- Inspect animation allocation limits and run repeated matches/scene transitions for memory corruption or leaked state.

Keep the host gameplay tests and ROM/source verifier passing. Add focused pose/interpolation and lifecycle tests, and record emulator observations separately from automated verification. Build the milestone ROM in `C:\Users\Lorenzo\Desktop\Smash 64\roms` and provide its opening link.

## 5. Expand after the milestone passes

1. Cover the remaining normal attack families, angled variants and aerial landings on the initial body.
2. Extend the rig mappings to the other bodies, explicitly reviewing large, compact and nonhuman skeletons, weapon attachments and tails.
3. Cover supported third-jab and rapid-jab states, checking donor loop timing and the body's existing chain capabilities.
4. Add grabs, tether visuals and paired capture/throw animations as a dedicated pass. These need coordinated attacker/victim posing, capture sockets and release timing; numeric throw customization alone does not solve them.

## Subsequent gameplay and usability milestones

Donor movement/physics, Link's bounce, Ness's reflector, hurtbox behavior, new jab-chain capabilities, broader special-move portability and saved creator presets remain separate work. Animation retargeting improves the visible attack and its pose data; it does not by itself reproduce those state-dependent behaviors.
