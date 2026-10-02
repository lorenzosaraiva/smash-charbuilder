# Mario donor animation pilot

Implemented on 2026-10-01, following the gameplay checkpoint `c4cf93a87` and the approved [retargeting plan](animation-retargeting-plan.md). This is the first three-move milestone; rendered emulator acceptance is still pending.

## Trying it

Open Options → Character Lab, edit a Mario body build, and choose:

| Attack row | Donor | Animation coverage |
| --- | --- | --- |
| Down Air | Captain Falcon | Full down-air pose and collision path; native Mario landing pose. |
| Forward Tilt | Fox | Straight forward tilt; angled variants retain Mario poses. |
| Forward Smash | Donkey Kong | Straight forward smash; angled variants retain Mario poses. |

Assign the build to a human or CPU slot, or use Test in Training. Training's View → HITBOX shows the attacks. Other donor/body combinations continue to use the existing collision/timing system and native body animations. Builds and assignments still last for the ROM session.

The new build is copied to `C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-full-roster.z64`. `Open Character Lab.lnk` opens it in RMG-K. Reopen the ROM to load this build if an older copy is already running. The gameplay checkpoint is retained beside it as `smash-character-lab-gameplay-baseline.z64` for comparison.

## Animation and skeleton conversion

`tools/auditCustomAnimations.py` records native bind transforms, hierarchy and animation script tables. Figatree table entries follow DObj traversal order, not the numeric suffix of script names. For these three descriptors, no reserved TransN/XRotN/YRotN channels are present, and donor translation-scale attributes are NULL. The generator rejects unsupported descriptor flags, translation scaling and non-unit bind bases.

Mario joint IDs 4–17 map to the same IDs on all three donors. Mario IDs 18–27 map to Fox IDs 18–27 and Captain/Donkey IDs 19–28. These maps cover the root/pelvis, torso/chest, shoulder/arm/hand, neck/head and hip/thigh/shin/ankle/foot chains. Donor belt/tie, tail and capture-only joints are not attached to Mario.

The converter evaluates native scalar interpolation, converts each mapped animated world orientation through donor and target bind bases, and reconstructs target local rotations. Mario keeps his bind translations and unit scales; root translation deltas use the ratio of the rigs' bind root heights. Donor animated squash/stretch is retained in collision calculations and omitted from the visible Mario rig to preserve his proportions. The high-detail bind rig supplies the target bases; low-detail mesh appearance still requires visual review.

All data is immutable and sampled at the existing attack clock's one-frame interval. The runtime copies 24 local poses after native animation-key processing, then invalidates cached transforms. It uses initialized Mario DObjs throughout. Body animation heaps, meshes, textures, TopN scale, facing, actor position and status functions remain native. There is no runtime donor file load, dynamic pose allocation or donor callback.

The source skeleton separately evaluates each active donor hitbox, including local offsets, nonuniform animated scale and scaled-position commands. Compiled centers include the donor's size. Before normal collision-position processing, the runtime assigns active pilot hitboxes to Mario's TopN and divides their compiled offsets by Mario's size. Normal TopN transforms then apply facing and actor position. Hitbox sizes, damage, knockback, creation/clear events, hit groups and swept-position history retain their existing handling. Smaller body limbs may visibly separate from a larger donor's original attack reach.

The per-player clock stores its move definition and retains its owner/status/motion guards. Pose and collision lookups never advance it. Hitlag therefore freezes both, nonzero restart frames select the matching sample, and status changes invalidate playback. Missing mapped joints reject the whole pose write and increment `gFTCustomAnimationValidationFailures`; collision script validation retains its separate existing counter.

## Validation and footprint

The native host oracle compiles the original `ftAnimParseDObjFigatree`, `gcPlayDObjAnimJoint`, `gmCollisionTransformMatrixAll` and `gmCollisionGetWorldPosition`, with the original animation arrays and native bind data. All **30,672 scalar pose values** match, with maximum observed error **0**. All **70 active hitbox centers** match the original matrix/point evaluation within **0.0000584 engine units per coordinate**, well inside the planned one-unit tolerance. These are numeric host checks, not rendered N64 observations.

The actual runtime host test checks all 130 pilot frames, complete mapped pose writes, frozen frames, nonzero starts, independent clocks for four players, shared presets, preview-owner isolation, CPU/demo/scene/body guards, status/motion interruption, collision-state preservation, target-size compensation and missing-joint fallback. The existing normal/grab/throw tests also pass. ROM verification checks that all three linked pose/trajectory tables exactly match host-tested bytes and preserves the 808-hitbox source audit and N64 checksum checks.

The pilot adds **81,640 bytes** of sampled data, **1,040 bytes** of overlay text and **16 bytes** of BSS after alignment. Total overlay resident growth is **82,704 bytes**; ROM growth is **82,688 bytes**, to **16,914,992 bytes**. The training arena before transient allocations is **1,971,248 bytes**. No extra fighter animation heap or per-player pose buffer is allocated. Runtime work is bounded to 24 pose copies and at most four collision-center updates per player per animation frame. This sampled format is deliberately limited to the pilot; full-roster expansion should use shared curves/rig data rather than multiplying dense tables.

An isolated run of the installed RMG-K core with silent/headless plugins executed 600 VI callbacks. The headless setup did not enter a playable match, and the saved gameplay baseline showed the same limitation. This is not an in-game acceptance pass. The user's running RMG-K process and save files were left untouched. Visual mesh quality, actual hitlag/contact/landing behavior, both facing directions, four-player matches and repeated scene transitions remain the rendered acceptance checklist in the plan.

Reproduce automated checks from WSL:

```sh
python3 tools/auditCustomAnimations.py > build/animation-audit.txt
python3 tools/generateCustomAnimations.py
python3 tools/testNativeAnimation.py
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
  -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 -DREGION_US \
  tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
make -j4 COLOR=0
python3 tools/verifyCustomMoveRom.py
```

`tools/reportCustomAnimationMemory.py` compares the built ELF/ROM with checkpoint copies named `build/animation-baseline.elf` and `build/animation-baseline.z64`. The Makefile's vanilla comparison reports `FAILURE` for this intentionally modified ROM; compilation/linking and the custom verifier succeed.

Next: finish rendered acceptance of these three moves, then cover angled variants and other normals on Mario before expanding the body maps. Grabs and paired throw/victim animations remain a separate pass.

The newer [collision milestone](collision-trajectories.md) separates collision
lookup from Mario pose lookup. These three paths now work on every foreign body,
alongside Kirby up-tilt. Their animation coverage remains Mario-only; the original
pilot byte layout is preserved. Current expanded geometry and lifecycle results
are recorded in the collision guide.
