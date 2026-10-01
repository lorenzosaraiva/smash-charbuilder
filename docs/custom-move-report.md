# Mario custom normal-attack foundation

The US N64 ROM builds successfully at `build/smashbrothers.us.z64`, in the existing output directory. Mario's down-air now has one continuous Falcon-inspired hitbox phase while retaining Mario's down-air animation, normal aerial status, skeleton, sounds, recovery and landing policy. No donor motion script or status implementation is executed by this proof.

Select ordinary Mario and use down-air (jump, then down + A). The experiment applies to ordinary Mario, including CPU Mario, independently of the earlier character-builder settings. Demo fighters, Metal Mario, polygon Mario and all other fighters are excluded.

## Audit and architecture

The implementation was preceded by inspection of Mario, Fox, Captain Falcon and Link main motion scripts, fighter/model data, `ftMotionCommandMakeAttackColl`, `FTAttackColl`, `ftParamGetJointID`, `ftMainSetStatus`, motion-event processing, and common aerial/landing handlers. The pre-implementation architecture summary was supplied in the chat.

| Audit question | Finding from the code |
|---|---|
| 1. What defines gameplay? | Motion-event timing; hitbox IDs/groups; damage, angle, knockback scale/weight/base; diameter/offset; element, collision targets, rebound, shield damage and sound; motion flags; common or character-specific status callbacks; target animation length and movement. |
| 2. What is animation-specific? | `FTMotionDesc.anim_file_id`, `FTAnimDesc` flags, figatree tracks, transforms, animation speed/length, animation-driven body movement, recovery and many presentation events. |
| 3. What is skeleton-specific? | Attack/effect/hurtbox joints, local axes/offsets, model/texture part indices, hidden parts, item sockets and figatree topology. |
| 4. What can be copied numerically? | A bounded attack's timing, damage, signed angle, knockback, diameter, collision flags, shield damage, element and hit sound. Local offsets need anatomical adaptation; encoded signed values must be normalized. |
| 5. What cannot be copied blindly? | Raw joints, foreign animation/status IDs, pointers or script branches, model/texture/hidden-part identifiers, source status-variable unions and character-specific callbacks. |
| 6. How are hitboxes created/cleared? | Five-word MakeAttack events initialize `FTAttackColl`, assign the joint pointer, set New/active state, share records for the same group, and apply move staling. ClearAll uses `ftParamClearAttackCollAll`; refresh creates a new hit record. Status changes normally clear attacks unless preserving hits. |
| 7. How are startup/active/endlag represented? | Async waits select an absolute animation frame; sync waits add a duration. Create/clear delimit active time. End of the script does not end the move: the animation/status callback controls recovery. |
| 8. Where is aerial landing behavior controlled? | Scripts set `motion_vars.flags.flag1`. `ftCommonAttackAirProcMap` checks that flag, Z-cancel timing and landing motion availability. A missing dedicated landing animation uses `LandingAirNull` at `flag1 / 100` animation speed. Other landing logic also considers vertical velocity. |
| 9. Why can foreign scripts crash? | The parser treats joint/model IDs and pointers as belonging to the current fighter. Invalid skeleton or model accesses can reach unchecked dereferences; a valid index can still mean the wrong body part. See concrete examples below. No emulator crash trace was available to identify one particular prior crash. |
| 10. Safest integration point? | The script selection and existing two-script motion-event machinery in `ftmain`, after the engine selects the target fighter's animation. Generate bounded, local collision events and preserve target status/presentation policy. |

The runtime path is: normalized definition -> semantic joint resolution against Mario -> locally generated collision-only events -> existing attack collision parser. The generator operates on definitions, with no source fighter resources at runtime.

## Root cause analysis

`ftParamGetJointID` only converts the special value -2 to the active fighter's light-item socket. It does not translate anatomical joints between fighters.

The MakeAttack branch in `ftMainParseMotionEvent` assigns `fp->joints[joint_id]` to the collision. `ftMainProcPhysicsMap` later passes that joint to `gmCollisionGetFighterPartsWorldPosition`. A foreign joint can therefore leave a NULL collision joint that is used downstream. Link's neutral-air uses joint 32; ordinary Mario's default setup initializes model joints 4 through 27. Mapping every invalid joint to TopN avoids that particular NULL access but destroys anatomical placement. It is not a semantic mapping.

Even valid indices differ: Falcon down-air joint 26 is his right knee, while Mario's right knee is 25 and Mario 26 is the ankle pivot. Falcon's model has an additional waist entry before the leg chains. Numerically valid indices are insufficient evidence of compatibility.

Foreign scripts can also issue model-part commands. Link down-air changes parts 21 and 19, which are Link equipment-related parts, while those slots belong to Mario's left leg chain. `ftParamSetModelPartID` uses the target's model-part tables and calls `ftGetParts(joint)` before its later NULL check. Foreign model IDs/table shapes are another concrete unchecked-access hazard. Script subroutine/goto/parallel pointers additionally require their original relocated resources to remain loaded.

Direct status transplantation has a separate problem: `ftMainSetStatus` ordinarily chooses the special-status table using the active fighter kind, while `ftFoxSpecialHi...` functions select Fox-specific status IDs and use `status_vars.fox.specialhi`. An integer status or a compatible-looking union is not a portable move implementation. Existing special adapters in this dirty clone are separate prior work; this change neither extends nor edits them.

## Semantic joint layer

Runtime files added:

- `src/ft/ftcustommove.h`: semantic enum and normalized hitbox/move definitions.
- `src/ft/ftcustommove.c.inc`: Mario mapping, one definition, validation, generator and native-collision filter. Included in `ftmain` so it stays in the existing overlay without a linker/YAML change.

Runtime file changed: `src/ft/ftmain.c`, adding that include, disabling the old donor selector for Mario's mapped normal slots, suppressing native collision events only for the custom down-air, and installing its generated script in parallel slot 1.

| Semantic joint | Mario raw joint | Verification |
|---|---:|---|
| Root | 0 / TopN | Existing `FTPartsJointLabels`; manager creates the root. |
| Torso | 5 | Central depth-1 body pivot in MarioModel; also used by vanilla body hitboxes. This is a torso pivot, not a separate chest surface joint. |
| Head | 12 | Depth-4 head display beneath the neck branch; MarioMain skeleton/head reference also identifies 12. |
| Left hand | 10 | End of the first arm chain. |
| Right hand | 16 | End of the second arm chain, parent of right item socket 17. |
| Left elbow | 9 | Forearm origin between the first upper arm and hand. |
| Right elbow | 15 | Forearm origin between the second upper arm and hand. |
| Left knee | 20 | Lower-leg origin in the left leg chain. |
| Right knee | 25 | Lower-leg origin in the right leg chain. |
| Left foot | 22 | Shoe display joint below the left ankle. |
| Right foot | 27 | Shoe display joint below the right ankle. |

These are ordinals in `src/relocData/296_MarioModel.c:dMarioModel_JointTree` plus `nFTPartsJointCommonStart` (4), not DObjDesc hierarchy depths. `ftManagerMakeFighter` passes the model slots starting at 4, and `lbCommonSetupFighterPartsDObjs` increments the destination for each ordinal even when a setup bit is absent. Mario's `0xFFFFFF00` setup mask initializes the first 24 model entries. MarioMain's right-hand item socket 17 and left/right slope leg roots 18/23 establish branch identity. Despite their field names, `joint_lfoot_id` and `joint_rfoot_id` refer to the slope leg roots; copying those fields as shoe or knee locations would be wrong.

There is no map for another fighter. A distinct chest location, shoulders, hips, neck, weapon/equipment sockets and other locations are not supported. They should be added only after data verification, rather than guessed.

## CustomMoveDefinition

`FTCustomMoveDefinition` stores an absolute startup animation frame, one active duration, a hitbox count, and up to four `FTCustomHitboxDefinition` entries. Four matches the actual collision array, although packed event attack IDs have three bits.

Each hitbox stores a semantic joint, group ID, damage, signed angle, knockback scale/weight/base, motion-event diameter, signed `Vec3h` local offset, `GMHitElement`, rebound flag, the existing ground/air event mask, shield damage, `GMAttackLevel`, `GMAttackSound`, and position-scaling flag. The generator uses existing motion-command packers; the collision parser halves diameter to produce its runtime radius.

The definition deliberately has no fighter status ID, animation ID, raw skeleton index, script pointer, donor fighter requirement, endlag, landing program, extra status variables, callback pointer, phase array or rehit schedule. The target keeps recovery, presentation and landing policy. Only a continuous collision phase is normalized today.

## First mixed aerial

Mario slot: down-air (`nFTCommonStatusAttackAirLw` / `nFTCommonMotionAttackAirLw`). Source: Captain Falcon down-air, `dCaptainMainMotion_AttackAirD` in `235_CaptainMainMotion.c`. Animation: unchanged Mario down-air, US file ID 626 (`626_FTMarioAnimAttackAirD.c`); its animation flags and tracks are retained.

| Property | Falcon source | Mario experiment |
|---|---|---|
| Activation | Animation frame 7 | Same |
| Active duration | 18 animation frames; clear at 25 | Same; active interval [7, 25) |
| Damage | 14 for each box, before staling | Same |
| Angle | -80 degrees | Same signed 10-bit value |
| Knockback scale / weight / base | 100 / 0 / 0 | Same |
| Diameters | 330 and 190 | Same; runtime radii 165 and 95 |
| Box 0 joint | Falcon raw 26: right knee | RIGHT_KNEE -> Mario 25 |
| Box 0 offset | (0, 120, 0) | (0, 45, 0), reduced for Mario |
| Box 1 joint | Falcon raw 5: torso | TORSO -> Mario 5, independently verified |
| Box 1 offset | (0, 30, 0) | (0, 0, 0), centered on Mario |
| Group / element / targets | Group 0 / normal / ground and air | Same |
| Rebound / shield damage / hit sound | Enabled / 0 / strong kick | Same |
| Animation, recovery and landing | Falcon-specific | Mario's original behavior |

The numeric source values were additionally checked against the extracted original US motion binary, `assets/us/relocData/235.vpk0.bin`, at the descriptor offset 0x1874.

Mario's native down-air Make/Clear/Refresh collision events are consumed without execution, so his original drill/rehit loop cannot clear or reactivate these boxes. Timing, loop control, sounds and flags in Mario's original script continue normally. The generated parallel script only waits, makes the two validated boxes, waits 18, clears and ends. Both boxes share group 0, preserving ordinary single-hit victim tracking through the existing parser.

Mario's original landing flag remains 20 from frame 10 to 33. Thus the custom attack starts three frames before Mario's original landing-lag window and finishes before it ends. Falcon's landing flag of 40, animation length, limb motion, recovery and sound cadence are not transplanted. World-space reach cannot be identical with a different animated skeleton and adapted offsets.

## Crash safety and verification

The resolver rejects unsupported fighter kinds, invalid enum values, out-of-array indices and NULL joint pointers. The generator validates player bounds, count against both the four-entry definition and the actual collision array, positive durations, bounded timing, all packed numeric ranges, enum values and Boolean flags. Signed local offsets use the existing signed 16-bit vector type. A rejected hitbox is skipped; a rejected definition produces an empty script rather than restoring native hitboxes. Failures increment `gFTCustomMoveValidationFailures`, a visible ELF/debugger symbol; no invalid joint falls back silently to TopN.

Each player has separate bounded script storage. Ordinary status changes clear attack collisions and clear the parallel script slots. Scope requires both Mario's down-air status and its matching common motion; demo mode and invalid player indices are excluded. No foreign status-variable member is accessed by this layer.

`tools/testCustomMove.c` runs the actual generator/filter in a minimal freestanding 32-bit host harness. It passed checks for encoded hitbox values and waits, the full four-box buffer bound, invalid joints/definitions/counts/player indices, separate simultaneous-player storage, the native refresh/clear filter, preservation of landing flag events, and exclusion of other motions/fighters/demo mode. The scaffold uses minimal engine objects; it is not an engine or emulator test.

Reproduce the host checks in WSL from the repository root:

```sh
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
  -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 \
  tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
```

## Build

Build command from the Windows workspace:

```powershell
wsl -d Ubuntu -- bash -lc 'make -j4 COLOR=0'
```

Result: compiler, linker, ROM conversion and N64 CRC patching completed successfully (exit 0). `RELOC_DATA` remains at its normal default; no relocation asset or animation arrays were changed. The final vanilla byte-comparison prints `FAILURE` because this is a modified ROM; it is not a compiler/linker failure.

ROM output: `C:\Users\Lorenzo\Documents\Workspace\smash\ssb-decomp-re\build\smashbrothers.us.z64`.

- Size: 16,792,128 bytes.
- SHA-256: `74d7d92192a7a52bbf12352c60d5c2a1b12185b830ecc16e37a33d79cea6accf`.
- Header: valid big-endian N64 magic `80371240`.
- CRC: both stored header CRC words match the repository's calculator.
- Artifact verification found the new definition and Mario mapping in the ROM and confirmed the linked parser/status code bytes at the ELF load addresses. Verification script/logs are under `build/`.

The artifact is a normal N64 ROM for opening in RMG-K. **It has not been tested in-game**, and emulator crash freedom, hitbox placement, landing behavior and simultaneous-fighter behavior still require a runtime smoke test.

## Vanilla roster audit

The [complete table and per-script evidence](custom-move-normal-audit.md) cover jab, dash, tilts, smash attacks and all five aerials for all 12 original fighters, including angled variants, jab3 and rapid-jab setup/loop entries. Generate it with `python3 tools/auditNormalMoves.py`.

The initial one-phase definition can express the numeric collision timelines of **134 / 230 unique descriptor-selected normal script entries (58.3%)**, after source joints are identified and mapped. The denominator includes rapid-jab setup entries with no hit; duplicate descriptor references are counted once per fighter, and distinct angled/byte-offset entries are separate. This is collision-only parameter coverage, not whole-move compatibility or demonstrated support for 58.3% of a playable mixed roster.

The census marks multihit, sequential phases, moving geometry, landing hitboxes, callback/state dependencies, weapon/skeleton dependencies, hurtbox changes, and other cleanup/control-flow dependencies separately. Examples include Fox up-air's two groups, Mario down-air refresh loops, Falcon forward-air's two separated hits, Falcon up-air's angle phases, Link back-air switching legs, Link down-air bounce/rehit, Kirby and Purin down-air landing hitboxes, Pikachu forward-air landing hitboxes, and Ness forward-smash's reflector. Kirby up-air leaves collision cleanup to status/animation end. These are gaps, not additional implemented moves.

## Remaining limitations and recommendation

Only one move and Mario's map are implemented. The visual animation remains a drill while collision gameplay is a single meteor-like hit. Mario's recovery, sounds, movement and landing lag are deliberately retained. The structure does not support multihit/late-hit phases, changing groups over time, jab machines, landing hitboxes, invulnerability programs, weapon semantic joints, character-specific callbacks, or specials. There is no broader character-creator UI or configuration feature in this change. Earlier unrelated changes and special adapters already present in the local clone were preserved.

This architecture is a suitable first foundation for single-phase normal/aerial parameter reuse: it routes verified semantic body locations into the existing N64 collision machinery and builds without donor-script execution. The code/audit support that narrow conclusion. Extending it across the roster will need per-fighter verified joint maps, explicit phase/rehit designs, and separate recovery/landing/callback policies; the present build does not establish runtime stability or full cross-character move equivalence.
