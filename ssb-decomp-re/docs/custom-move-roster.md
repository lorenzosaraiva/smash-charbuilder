# Character Lab: normal attacks, grabs and throws

The working Mario aerial was committed as `f0d2e1a6c` before this extension. The new ROM supports all thirteen normal attack families from all twelve playable fighters on all twelve bodies: jab, dash attack, three tilts, three smashes and five aerials. The generated table contains 396 entries including angled variants, landing scripts, third jabs and rapid-jab phases.

The editor also has independent **Grab**, **Forward Throw** and **Back Throw** donor rows after Down Air. Each accepts all twelve fighters and applies to assigned human or CPU slots. New presets start with their body's own grab and throw donors; Use Body For All and Randomize Attacks include these rows.

**Neutral B** cycles through **BODY MOVE**, **FOX LASER**, **MARIO FIREBALL**, **LUIGI FIREBALL**, **THUNDER JOLT** and **PK FIRE** with left/right. Use Body For All restores the body's native neutral; randomization includes all six choices. Initial presets retain Fox laser. This first projectile batch is decomp only; the remaining neutral-special donors are unfinished.

## Playing

1. Open **Options → Character Lab**. Select one of four builds with A, edit donor values with left/right, and return with B.
2. On the lab's main screen, select **Player One/Two/Three/Four** and use left/right to assign a build or **Vanilla**. Assigning a build enables it. The player number is the controller/CPU slot, independently of team color.
3. Select **Play VS**. Assigned bodies are preselected. Change the usual player-type control to CPU for a custom opponent. Keep that build's body selected; choosing a different body plays that body normally. Two slots can use distinct builds with the same body, or share one build.
4. **Test in Training** assigns the edited build to player one. In training, press Start, select **View**, and choose **HITBOX** with left/right. It uses the engine's red attack outlines and hurtbox visualization for both fighters. NORMAL/CLOSE UP restore ordinary rendering.
5. Leaving a training test through the pause menu, or pressing **Back** on its character-select screen, reopens that build's editor with **Test in Training** selected. Training resets keep this return destination. Ordinary training retains its usual return path.

The four unlockable fighters (Luigi, Captain Falcon, Jigglypuff and Ness) and Item Switch are unlocked on fresh and existing saves. Existing records and options are preserved. These unlocks survive a restart; creator builds and player assignments currently last for the running ROM session.

## Compatibility rules

- Normal attacks use the donor's collision parameters, startup, active windows and full animation-length recovery. An independent per-player frame clock keeps a longer donor move running after the visible animation ends, or finishes a shorter donor move while that animation is still playing. Hitlag pauses this clock. The [Mario animation catalog](mario-animations.md) applies Fox/DK/Luigi/Falcon normal poses on that clock, including angled attacks and aerial landings. Other combinations retain the body's animation. Status functions, sounds, effects, physics and invulnerability remain native; donor state functions and joint/script pointers are never loaded.
- A generated local collision timeline replaces native collision events, including native parallel collision events. It supports creation, phased changes, damage/size/sound changes, moving offsets, individual/all clears, refresh and hit groups. Native parallel effects retain their own slot; the generic collisions use a third slot.
- Each source joint initially becomes a semantic body location for safe event dispatch. The trajectory layer then positions every active normal hitbox from the original donor rig, independently of the mapped joint. Explicit JointTree maps for each target resolve that location to its own initialized skeleton. Missing/invalid joints, attack IDs, truncated commands, foreign opcodes or oversized buffers reject the complete generated script safely and increment `gFTCustomMoveValidationFailures`.
- Hitbox diameter, local offsets, damage, angle, knockback scale/weight/base, element and collision masks retain their source values. The earlier Mario/Falcon down-air offset reduction has been removed. The full normal catalog evaluates original weapon/tail/limb transforms and places compiled donor centers relative to the body's TopN, with inverse body-size compensation. Reach and path follow the donor even when the visible body has different proportions or no matching part. See the [collision guide](collision-trajectories.md).
- Third-jab and rapid-jab choices run only in states supported by the body. A donor cannot add a new chain to a body without that chain. Common jab/repeat input windows follow donor flag1 events. Rapid collision loops repeat at the donor's animation period and jump only within that player's own generated buffer, independently of the visible animation cycle.
- Aerial landing windows, landing hitboxes and landing recovery follow the aerial donor, including fallback landing duration divided by the donor's landing-animation rate. Landing or taking damage can still interrupt an aerial normally. Link's bounce, Ness's reflector, donor-specific effects and hurtbox behavior are not transplanted.
- Link's native down-air bounce and rehit callbacks are suppressed when he uses another donor's down-air, so those callbacks cannot clear or restart that donor's collision timeline. His own down-air retains its normal behavior.
- The earlier special adapters remain separate, as in the working checkpoint. This extension normalizes normal/aerial collisions; it does not add a new special-move system.
- Custom definitions apply in VS and training only. Demo/preview fighters and unrelated modes keep their normal behavior.

## Grab and throw compatibility

Grabs replace collision shapes and offsets, with donor capture anchors mapped to the body's own capture joint. Startup, active duration and whiff recovery now follow the donor. Native shield-grab logic, capture callbacks and effects remain intact. A tether donor does not transplant its tether animation or guarantee its original reach on another body.

Forward and back throws copy the donor's damage, angle, knockback scale/weight/base and element for both throw descriptors. The Grab donor also supplies the grab escape descriptor values. Each player has independent descriptor storage. Native victim status IDs, release timing and capture animations are retained. Kirby's forward throw and Donkey Kong's cargo release use their source throw values without importing their capture states into other bodies. Throw motion collisions and collateral hits remain the body's own.

Exception for DK with another fighter's Forward Throw selected: enter DK's own finite forward release motion directly, instead of his pickup/cargo-wait sequence. The victim queues the common thrown state instead of cargo's shoulder escape loop. Donor throw damage/knockback still apply; the release pose and timing remain DK's. DK's own Forward Throw and vanilla DK retain cargo behavior. Paired donor throw animations remain future work.

## Neutral-special compatibility

The old prototype spawned Fox lasers during every assigned body's native neutral special. It replaced accessory callbacks and consumed native flags while leaving charge, suction and other body state transitions active. Neutral B was also a fixed label in the editor.

BODY MOVE now uses the body's ordinary neutral-special implementation and events. FOX LASER on non-Fox bodies uses only a body-owned neutral pose, a local laser event script, common movement/collision callbacks and an independent finite frame clock. DK and Samus use their release poses rather than charge-start poses. Native neutral events and callbacks are suppressed for this action, so it cannot enter their charging loops or create another projectile/capture attack. Fox bodies keep their ordinary laser implementation. No foreign neutral-special status implementation, joint indices or animation file is loaded.

Laser firing and recovery follow Fox's US source data: grounded shot on frame 25, repeat enabled on 29, recovery through frame 55; airborne shot/repeat on frame 15, recovery through frame 45. Hitlag pauses the clock. Landing, leaving a platform or taking damage can cancel the action normally. The projectile remains the native Fox blaster; its spawn uses the body's root position. The visual pose is still the body's, not a retargeted Fox animation.

MARIO FIREBALL, LUIGI FIREBALL, THUNDER JOLT and PK FIRE use the same isolated body-pose entry, with dedicated bounded scripts and per-player firing state. Matching donor bodies use the ordinary native move. Foreign bodies spawn the actual native projectile, preserving weapon damage, size, knockback, lifetime, collision, bounce/stage following, reflection/absorption and PK Fire's spark-to-pillar behavior. Resource setup preloads their donor special files; all original particle banks are initialized by the existing playable-file setup. Projectile ownership/team/staleness remain with the borrowing player.

Firing frames (ground/air) are 16/16 for both fireballs, 21/21 for jolt, 20/20 for PK Fire. Recovery durations are 46/46, 46/46, 64/64 and 72/60 respectively. Generated spawn offsets sample each donor's original US animation/rig at its firing frame and apply donor size, then translate/mirror at the borrowing body's root. Ness retains its explicit root offset and native air/ground angle/speed. The spawn is independent of body proportions or limb mapping. Landing/edge transitions preserve elapsed time and switch to the matching ground/air definition; a spent shot cannot replay. Interrupted actions reject stale accessory callbacks, and a failed weapon allocation consumes that action's shot just as the native flag does. Common body movement and native body hurtboxes remain; donor movement and retargeted neutral animations are separate work.

Charge/store/release (DK/Samus), boomerang return/catch (Link), paired capture (Yoshi), melee/movement hitboxes (Falcon/Pound) and their visuals still need dedicated adapters. Kirby copy is excluded.

The lab uses the game's existing option tabs, font sprites at readable 2x size, gold headings, red selection and purple/gray panels. The HITBOX label is composed from the same native alphabet, rather than an external font.

## Validation

Generate the data with `python3 tools/generateCustomMoves.py`, `python3 tools/generateCustomGrabs.py` `python3 tools/generateCustomCollisions.py` and `python3 tools/generateTrainingHitboxLabel.py`. Projectile timing/spawn data use `python3 tools/generateNeutralProjectiles.py`; the verifier rejects stale output. `tools/auditNormalMoves.py` remains a read-only census of the source moves.

The freestanding host test includes the actual runtime implementation. It checks all 12 × 12 × 33 = **4,752 body/donor/variant combinations**, per-player buffers, CPU/vanilla/demo/scene eligibility, native event suppression, local rapid-loop pointers, malformed definitions and the original Falcon aerial parameters. Frame-clock tests run every valid donor variant through its complete duration while simulating an already-ended body animation, and check expiry, reset and the independent script clock. It does not simulate N64 animations or collision detection.

Grab coverage adds **144 body/donor combinations**, verifying donor timing and mapped capture joints. Descriptor tests cover **432 body/donor/grab-or-throw combinations**, preserve both native victim statuses, verify known Samus and Donkey Kong source values, and check independent player storage and eligibility guards.

Neutral adapter tests cover all twelve bodies on ground/in air across four independent slots, including CPU assignment, body/native-Fox fallbacks, finite recovery despite an ended body pose, repeat input, interruption and duplicate-shot prevention. DK tests include actual common throw dispatch and DK release callbacks with engine services stubbed: all twelve forward donors, common victim queue for foreign throws, donor numeric properties, one release, capture cleanup, native cargo and back-throw dispatch. These tests do not render or simulate victim physics. The four new projectile adapters add 352 foreign-body/ground-air/player-slot cases and 32 native fallbacks, with transition, interruption, duplicate-shot and allocation-failure checks. The native animation/matrix oracle independently checks all eight spawn definitions. The ROM verifier checks dispatch/resource code, linked projectile constructors, bounded scripts, exact pointer/duration records and spawn tables. These tests do not replace rendered projectile/contact acceptance.

```sh
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
  -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 -DREGION_US \
  tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
make -j4 COLOR=0
python3 tools/verifyCustomMoveRom.py
```

The ROM verifier checks all 396 normal and twelve grab collision tables, 36 two-part throw definitions, semantic and capture maps, donor duration metadata, grab timings, linked creator/assignment/training/frame-clock code at ELF load addresses, N64 byte order and the patched checksum. Its source audit verifies **808 original normal hitbox definitions**, including **511 tilt/smash hitboxes**, and every creation/clear timestamp against the compiled host tables. It checks damage, diameter, offsets, angle and all knockback fields without importing donor skeleton IDs. The modified ROM is expected to differ from vanilla, so the Makefile's vanilla comparison prints `FAILURE` after a successful compile/link. In-emulator playtesting of this expanded build is still required.

Output: `build/smashbrothers.us.z64`, also copied to `C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-full-roster.z64`. A companion Windows shortcut opens that copy with the installed RMG-K.
