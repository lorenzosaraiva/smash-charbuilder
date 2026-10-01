# Character Lab: normal attacks, grabs and throws

The working Mario aerial was committed as `f0d2e1a6c` before this extension. The new ROM supports all thirteen normal attack families from all twelve playable fighters on all twelve bodies: jab, dash attack, three tilts, three smashes and five aerials. The generated table contains 396 entries including angled variants, landing scripts, third jabs and rapid-jab phases.

The editor also has independent **Grab**, **Forward Throw** and **Back Throw** donor rows after Down Air. Each accepts all twelve fighters and applies to assigned human or CPU slots. New presets start with their body's own grab and throw donors; Use Body For All and Randomize Attacks include these rows.

## Playing

1. Open **Options → Character Lab**. Select one of four builds with A, edit donor values with left/right, and return with B.
2. On the lab's main screen, select **Player One/Two/Three/Four** and use left/right to assign a build or **Vanilla**. Assigning a build enables it. The player number is the controller/CPU slot, independently of team color.
3. Select **Play VS**. Assigned bodies are preselected. Change the usual player-type control to CPU for a custom opponent. Keep that build's body selected; choosing a different body plays that body normally. Two slots can use distinct builds with the same body, or share one build.
4. **Test in Training** assigns the edited build to player one. In training, press Start, select **View**, and choose **HITBOX** with left/right. It uses the engine's red attack outlines and hurtbox visualization for both fighters. NORMAL/CLOSE UP restore ordinary rendering.

The four unlockable fighters (Luigi, Captain Falcon, Jigglypuff and Ness) and Item Switch are unlocked on fresh and existing saves. Existing records and options are preserved. These unlocks survive a restart; creator builds and player assignments currently last for the running ROM session.

## Compatibility rules

- Normal attacks use the donor's collision parameters, startup, active windows and full animation-length recovery. An independent per-player frame clock keeps a longer donor move running after the visible animation ends, or finishes a shorter donor move while that animation is still playing. Hitlag pauses this clock. The body's animation, status, sounds, effects, physics and invulnerability remain native; no donor state function or animation is loaded.
- A generated local collision timeline replaces native collision events, including native parallel collision events. It supports creation, phased changes, damage/size/sound changes, moving offsets, individual/all clears, refresh and hit groups. Native parallel effects retain their own slot; the generic collisions use a third slot.
- Each source joint becomes a semantic body location. Explicit JointTree maps for each target resolve that location to its own initialized skeleton. Missing/invalid joints, attack IDs, truncated commands, foreign opcodes or oversized buffers reject the complete generated script safely and increment `gFTCustomMoveValidationFailures`.
- Hitbox diameter, local offsets, damage, angle, knockback scale/weight/base, element and collision masks retain their source values. The earlier Mario/Falcon down-air offset reduction has been removed. Weapon sockets map to the holding hand and tails map to the torso on bodies without an equivalent part. Hitbox centers follow the mapped body joints, so their spatial path still differs with the visible animation.
- Third-jab and rapid-jab choices run only in states supported by the body. A donor cannot add a new chain to a body without that chain. Common jab/repeat input windows follow donor flag1 events. Rapid collision loops repeat at the donor's animation period and jump only within that player's own generated buffer, independently of the visible animation cycle.
- Aerial landing windows, landing hitboxes and landing recovery follow the aerial donor, including fallback landing duration divided by the donor's landing-animation rate. Landing or taking damage can still interrupt an aerial normally. Link's bounce, Ness's reflector, donor-specific effects and hurtbox behavior are not transplanted.
- Link's native down-air bounce and rehit callbacks are suppressed when he uses another donor's down-air, so those callbacks cannot clear or restart that donor's collision timeline. His own down-air retains its normal behavior.
- The earlier special adapters remain separate, as in the working checkpoint. This extension normalizes normal/aerial collisions; it does not add a new special-move system.
- Custom definitions apply in VS and training only. Demo/preview fighters and unrelated modes keep their normal behavior.

## Grab and throw compatibility

Grabs replace collision shapes and offsets, with donor capture anchors mapped to the body's own capture joint. Startup, active duration and whiff recovery now follow the donor. Native shield-grab logic, capture callbacks and effects remain intact. A tether donor does not transplant its tether animation or guarantee its original reach on another body.

Forward and back throws copy the donor's damage, angle, knockback scale/weight/base and element for both throw descriptors. The Grab donor also supplies the grab escape descriptor values. Each player has independent descriptor storage. Native victim status IDs, release timing and capture animations are retained. Kirby's forward throw and Donkey Kong's cargo release use their source throw values without importing their capture states into other bodies. Throw motion collisions and collateral hits remain the body's own.

The lab uses the game's existing option tabs, font sprites at readable 2x size, gold headings, red selection and purple/gray panels. The HITBOX label is composed from the same native alphabet, rather than an external font.

## Validation

Generate the data with `python3 tools/generateCustomMoves.py`, `python3 tools/generateCustomGrabs.py` and `python3 tools/generateTrainingHitboxLabel.py`. `tools/auditNormalMoves.py` remains a read-only census of the source moves.

The freestanding host test includes the actual runtime implementation. It checks all 12 × 12 × 33 = **4,752 body/donor/variant combinations**, per-player buffers, CPU/vanilla/demo/scene eligibility, native event suppression, local rapid-loop pointers, malformed definitions and the original Falcon aerial parameters. Frame-clock tests run every valid donor variant through its complete duration while simulating an already-ended body animation, and check expiry, reset and the independent script clock. It does not simulate N64 animations or collision detection.

Grab coverage adds **144 body/donor combinations**, verifying donor timing and mapped capture joints. Descriptor tests cover **432 body/donor/grab-or-throw combinations**, preserve both native victim statuses, verify known Samus and Donkey Kong source values, and check independent player storage and eligibility guards.

```sh
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
  -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 \
  tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
make -j4 COLOR=0
python3 tools/verifyCustomMoveRom.py
```

The ROM verifier checks all 396 normal and twelve grab collision tables, 36 two-part throw definitions, semantic and capture maps, donor duration metadata, grab timings, linked creator/assignment/training/frame-clock code at ELF load addresses, N64 byte order and the patched checksum. Its source audit verifies **808 original normal hitbox definitions**, including **511 tilt/smash hitboxes**, and every creation/clear timestamp against the compiled host tables. It checks damage, diameter, offsets, angle and all knockback fields without importing donor skeleton IDs. The modified ROM is expected to differ from vanilla, so the Makefile's vanilla comparison prints `FAILURE` after a successful compile/link. In-emulator playtesting of this expanded build is still required.

Output: `build/smashbrothers.us.z64`, also copied to `C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-full-roster.z64`. A companion Windows shortcut opens that copy with the installed RMG-K.
